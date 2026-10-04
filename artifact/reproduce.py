#!/usr/bin/env python3
"""Offline released-data reproduction; original analyses remain in their checkout.

Reasonance's adapter reconstructs numeric SQLite input and audits identifiers.
It neither regenerates hypotheses nor calls a model or a literature service.
"""

import argparse
import contextlib
import csv
import gzip
import hashlib
import importlib
import importlib.metadata
import io
import json
import os
import socket
import sqlite3
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

PIN = "39a310db1a21c83f71455565d05f485933f648bd"
HERE = Path(__file__).resolve().parent
DIMS = ("originality", "feasibility", "clarity", "impact", "specificity")
SCORE_TABLES = {
    "lit8d_scores_3seed": "core/lit8d_scores_3seed.csv.gz",
    "e38_replay_scores": "appendix/e38_replay_scores.csv.gz",
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def csv_rows(source, relative):
    with gzip.open(source / "release_data" / relative, "rt", encoding="utf-8", newline="") as f:
        yield from csv.DictReader(f)


def verify_source(source):
    """Require a clean pinned checkout and byte-identical required inputs."""
    manifest = read_json(HERE / "source-hashes.json")
    if manifest["commit"] != PIN:
        raise ValueError("The adapter and source-hashes.json disagree on the source pin")
    if (source / ".env").exists():
        raise ValueError("Use a clean source checkout without a .env file; credentials are not needed")
    for args in (("rev-parse", "HEAD"), ("status", "--porcelain", "--untracked-files=no")):
        p = subprocess.run(["git", "-C", str(source), *args], capture_output=True, text=True)
        if p.returncode:
            raise ValueError("Source must be a local Git checkout of the documented release")
        if args[0] == "rev-parse" and p.stdout.strip() != PIN:
            raise ValueError(f"Source HEAD must be {PIN}")
        if args[0] == "status" and p.stdout.strip():
            raise ValueError("Source has tracked modifications; use a clean pinned checkout")
    for relative, expected in manifest["sha256"].items():
        path = source / relative
        if not path.is_file():
            raise ValueError(f"Required source input is missing: {relative}")
        with path.open("rb") as f:
            actual = hashlib.file_digest(f, "sha256").hexdigest()
        if actual != expected:
            raise ValueError(f"Required source input differs from the pin: {relative}")
    return manifest


def _offline(*args, **kwargs):
    raise RuntimeError("Offline analysis: network, subprocess and model calls are disabled")


def install_offline_guards():
    """Fail closed on Python socket use, external commands, and SDK clients.

    This guards the selected, verified analysis code, not arbitrary hostile code.
    Acquisition and dependency installation are separate steps outside analysis.
    """
    def audit(event, args):
        if event.startswith("socket.") or event in {
            "subprocess.Popen", "os.system", "os.posix_spawn", "os.exec", "os.fork", "os.forkpty",
        }:
            _offline()

    sys.addaudithook(audit)
    socket.socket.connect = _offline
    socket.socket.connect_ex = _offline
    socket.socket.sendto = _offline
    socket.create_connection = _offline
    socket.getaddrinfo = _offline
    # Imported by upstream's generation modules, even though analysis never
    # needs a client. Block construction before those modules are imported.
    import openai
    for name in ("OpenAI", "AsyncOpenAI", "AzureOpenAI", "AsyncAzureOpenAI", "Client", "AsyncClient"):
        if hasattr(openai, name):
            setattr(openai, name, _offline)


def score_json(row):
    """Pack the five released numeric columns; incomplete rows remain SQL NULL."""
    scores = {d: float(row[f"score_{d}"]) for d in DIMS if row[f"score_{d}"] != ""}
    return json.dumps(scores) if len(scores) == len(DIMS) else None


def hydrate(source, output):
    """Build our numeric input, preserving row order and available-case rules."""
    primary = set(read_json(source / "reports/primary_roster.json")["models"])
    db = output / "numeric-primary.db"
    counts = {}
    with sqlite3.connect(db) as conn:
        for table, relative in SCORE_TABLES.items():
            rows = list(csv_rows(source, relative))
            columns = list(rows[0])
            schema = [f'"{c}" TEXT' for c in columns] + ['"scores_json" TEXT']
            conn.execute(f'CREATE TABLE "{table}" ({", ".join(schema)})')
            placeholders = ",".join("?" for _ in schema)
            loaded = valid = 0
            for row in rows:
                if table == "lit8d_scores_3seed" and row["idea_model"] not in primary:
                    continue
                sj = score_json(row)
                conn.execute(f'INSERT INTO "{table}" VALUES ({placeholders})',
                             [row[c] if row[c] != "" else None for c in columns] + [sj])
                loaded += 1
                valid += sj is not None
            counts[relative] = {"input_rows": len(rows), "loaded_rows": loaded,
                                "valid_numeric_rows": valid}
        relative = "core/subdomain_refs.csv.gz"
        rows = list(csv_rows(source, relative))
        columns = list(rows[0])
        schema = ",".join(f'"{c}" TEXT' for c in columns)
        conn.execute(f"CREATE TABLE subdomain_refs ({schema})")
        conn.executemany(f'INSERT INTO subdomain_refs VALUES ({",".join("?" for _ in columns)})',
                         [[r[c] for c in columns] for r in rows])
        counts[relative] = {"input_rows": len(rows), "loaded_rows": len(rows)}
    return db, counts


def load_original(source, db, output):
    # Do not write into the input checkout or load its pre-existing bytecode.
    sys.dont_write_bytecode = True
    sys.pycache_prefix = str(output / "unused-bytecode-cache")
    sys.path.insert(0, str(source))
    import config
    config.RESULTS_DB = db
    e37 = importlib.import_module("experiments.e37_review_r2_stats")
    e38 = importlib.import_module("experiments.e38_replay_refs")
    e37.OUT_JSON = output / "original-e37.json"
    e38.OUT_JSON = output / "original-e38.json"
    return e37, e38


def replay_keys(db, e38):
    """Use the exact E38 subset, roster and available-case cell aggregation."""
    with sqlite3.connect(db) as conn:
        subset = {s for _, s in e38.pick_subs(conn)}
        models = set(e38.roster(conn))
        replay = e38._seed_cells(conn.execute(
            "SELECT idea_model, subdomain, idea_index, scores_json FROM e38_replay_scores "
            "WHERE scores_json IS NOT NULL"))
        rows = [row for row in conn.execute(
            "SELECT idea_model, subdomain, track, idea_index, scores_json "
            "FROM lit8d_scores_3seed WHERE scores_json IS NOT NULL")
            if row[1] in subset and row[0] in models]
    static = e38._seed_cells([(m, s, i, sj) for m, s, t, i, sj in rows if t == "B"])
    active = e38._seed_cells([(m, s, i, sj) for m, s, t, i, sj in rows if t == "C"])
    shared = set(replay) & set(static) & set(active)
    scored = {(m, s, int(i)) for m, s, t, i, sj in rows if t == "C" and (m, s) in shared}
    return shared, scored


def identifier_trajectories(ref_rows, trace_rows, shared):
    """Identifier join only; preserve distinct model/subfield/idea-index keys."""
    refs = defaultdict(set)
    for row in ref_rows:
        if row["source_table"] == "e38_replay_refs":
            refs[row["idea_model"], row["subdomain"]].add(row["ss_paper_id"])
    traces = defaultdict(list)
    for row in trace_rows:
        if row["source_table"] == "subdomain_ideas" and (row["idea_model"], row["subdomain"]) in shared:
            traces[row["idea_model"], row["subdomain"], int(row["idea_index"])].append(row)
    trajectories = []
    for (model, subfield, index), rows in sorted(traces.items()):
        search, fetch, first_search = set(), set(), None
        for row in sorted(rows, key=lambda r: int(r["iter"])):
            ids = {x for x in json.loads(row["returned_ss_ids"] or "[]") if x}
            if row["tool"] == "search_papers":
                search |= ids
                if first_search is None:
                    first_search = ids
            else:
                fetch |= ids
        active = search | fetch
        replay = refs[model, subfield]
        trajectories.append({
            "idea_model": model, "subdomain": subfield, "idea_index": index,
            "tool_calls": len(rows), "active_unique_ids": len(active),
            "search_unique_ids": len(search), "fetch_unique_ids": len(fetch),
            "replay_ids": len(replay), "active_ids_in_replay": len(active & replay),
            "replay_ids_in_first_search": len(replay & (first_search or set())),
            "replay_coverage_fraction": len(active & replay) / len(active) if active else None,
            "active_ids_absent_from_replay": len(active - replay),
            "fetch_ids_absent_from_replay": len(fetch - replay),
            "entire_active_id_set_replayed": active <= replay if active else None,
        })
    return trajectories


def quantiles(values):
    import numpy as np
    if not values:
        return {"n": 0, **{k: None for k in ("min", "p25", "median", "p75", "max", "mean")}}
    a = np.asarray(values, dtype=float)
    return {"n": len(a), "min": float(a.min()), "p25": float(np.percentile(a, 25)),
            "median": float(np.median(a)), "p75": float(np.percentile(a, 75)),
            "max": float(a.max()), "mean": float(a.mean())}


def summarize_identifiers(trajectories, shared, scored):
    traced = {(r["idea_model"], r["subdomain"], r["idea_index"]) for r in trajectories}
    out = {
        "scope": "Exact E38 shared model/subfield cells. Returned Semantic Scholar paper IDs, "
                 "not abstracts, delivered tokens, useful information or causal effects.",
        "n_shared_cells": len(shared), "n_designed_active_ideas": 3 * len(shared),
        "n_scored_active_ideas": len(scored), "n_active_trajectories": len(trajectories),
        "n_nonempty_identifier_trajectories": sum(r["active_unique_ids"] > 0 for r in trajectories),
        "scored_ideas_without_trace_rows": [list(k) for k in sorted(scored - traced)],
        "trace_trajectories_without_scored_rows": [list(k) for k in sorted(traced - scored)],
        "active_unique_ids": quantiles([r["active_unique_ids"] for r in trajectories]),
        "replay_coverage_fraction": quantiles([r["replay_coverage_fraction"] for r in trajectories
                                               if r["replay_coverage_fraction"] is not None]),
        "active_ids_absent_from_replay": quantiles([r["active_ids_absent_from_replay"] for r in trajectories]),
        "n_nonempty_entire_active_id_set_replayed": sum(r["active_unique_ids"] > 0 and
                                                       r["entire_active_id_set_replayed"] for r in trajectories),
        "n_trajectories_with_fetch_ids_omitted": sum(r["fetch_ids_absent_from_replay"] > 0 for r in trajectories),
        "by_idea_index": {},
    }
    for index in (1, 2, 3):
        rr = [r for r in trajectories if r["idea_index"] == index]
        out["by_idea_index"][str(index)] = {
            "n_trajectories": len(rr),
            "replay_coverage_fraction": quantiles([r["replay_coverage_fraction"] for r in rr
                                                   if r["replay_coverage_fraction"] is not None]),
            "n_replay_set_contained_in_first_search_set": sum(r["replay_ids_in_first_search"] == r["replay_ids"]
                                                            for r in rr),
        }
    return out


def compare_results(source, output, audit):
    original37 = read_json(source / "reports/e37_review_r2_stats.json")
    original38 = read_json(source / "reports/e38_replay_refs.json")
    result37 = read_json(output / "original-e37.json")
    result38 = read_json(output / "original-e38.json")
    checks = {
        "e37_discrimination_matches_pinned": result37["discrimination"] == original37["discrimination"],
        "e37_capability_gate_matches_pinned": result37["gate_split_half"] == original37["gate_split_half"],
        "e38_means_match_pinned": result38["means"] == original38["means"],
        "e38_cell_level_matches_pinned": result38["cell_level"] == original38["cell_level"],
        "e38_model_active_minus_replay_matches_pinned":
            result38["model_level"]["C_minus_Rp"] == original38["model_level"]["C_minus_Rp"],
        "identifier_counts_match_expected": [audit[k] for k in (
            "n_shared_cells", "n_scored_active_ideas", "n_active_trajectories",
            "n_nonempty_identifier_trajectories", "n_nonempty_entire_active_id_set_replayed",
            "n_trajectories_with_fetch_ids_omitted")] == [279, 837, 835, 827, 4, 526],
        "median_identifier_overlap_matches_expected": audit["replay_coverage_fraction"]["median"] == 0.1,
    }
    return {
        "checks": checks, "all_selected_checks_pass": all(checks.values()),
        "secondary_model_replay_minus_static_p": {
            "this_run": result38["model_level"]["Rp_minus_B"]["wilcoxon_p"],
            "pinned": original38["model_level"]["Rp_minus_B"]["wilcoxon_p"],
            "note": "A previous reproduction gave 0.1865 versus pinned 0.1936. The cause "
                    "was not established; do not claim whole-file E38 equality.",
        },
        "interpretation": "These are released-data checks, not a new model trial. The original "
                          "E38 JSON includes the authors' process-effect interpretation; "
                          "reproducing its arithmetic does not validate that causal interpretation.",
    }


def run(source, output, manifest):
    if output == source or output.is_relative_to(source):
        raise ValueError("Output must be outside the source checkout")
    if output.exists() and any(output.iterdir()):
        raise ValueError("Output directory must be new or empty")
    output.mkdir(parents=True, exist_ok=True)
    install_offline_guards()
    db, counts = hydrate(source, output)
    e37, e38 = load_original(source, db, output)
    print("Running unchanged E37 and E38 analyses on the primary-roster numeric input...", flush=True)
    # Upstream stdout includes local output paths. Keep it out of exported
    # files and expose only the structured results and this concise summary.
    with contextlib.redirect_stdout(io.StringIO()):
        e37.main()
        e38.analyze()
    shared, scored = replay_keys(db, e38)
    trajectories = identifier_trajectories(csv_rows(source, "derived/static_refs.csv.gz"),
                                         csv_rows(source, "derived/active_traces.csv.gz"), shared)
    audit = summarize_identifiers(trajectories, shared, scored)
    write_json(output / "replay-identifiers.json", audit)
    with (output / "replay-identifiers-by-trajectory.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(trajectories[0]))
        writer.writeheader()
        writer.writerows(trajectories)
    write_json(output / "provenance.json", {
        "repository": manifest["repository"], "commit": PIN, "sha256": manifest["sha256"],
        "python": sys.version.split()[0],
        "dependencies": {name: importlib.metadata.version(name) for name in ("numpy", "scipy", "openai", "requests")},
        "roster": "reports/primary_roster.json: 30 primary models, then original both-track selection",
        "database": "numeric-primary.db is Reasonance's reconstructed numeric input, not the authors' original DB",
        "input_counts": counts,
        "analysis_calls": ["experiments.e37_review_r2_stats.main", "experiments.e38_replay_refs.analyze"],
        "adapter_changes": ["pack released five numeric score columns as scores_json; incomplete rows are SQL NULL",
                            "filter main score rows to primary roster; redirect only RESULTS_DB and OUT_JSON",
                            "disable Python socket networking, subprocesses and OpenAI SDK client construction"],
        "upstream_code": "Loaded unchanged from the verified external checkout; not vendored",
        "data_attribution": "AgentIdeaBench, The AgentIdeaBench Authors, CC BY 4.0. Semantic Scholar identifiers: Semantic Scholar Academic Graph, ODC-BY 1.0.",
    })
    checks = compare_results(source, output, audit)
    write_json(output / "checks.json", checks)
    print(json.dumps({
        "all_selected_checks_pass": checks["all_selected_checks_pass"],
        "shared_cells": audit["n_shared_cells"], "scored_active_ideas": audit["n_scored_active_ideas"],
        "traced_trajectories": audit["n_active_trajectories"],
        "nonempty_identifier_trajectories": audit["n_nonempty_identifier_trajectories"],
        "median_returned_id_overlap_fraction": audit["replay_coverage_fraction"]["median"],
    }, indent=2))
    print("Wrote structured results, identifier counts per trajectory, provenance and our numeric DB.")
    return 0 if checks["all_selected_checks_pass"] else 1


def main():
    # Bound local linear-algebra parallelism before importing dependencies.
    for name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
        os.environ[name] = "1"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--source", required=True, type=Path, help="Clean local checkout at the documented commit")
    parser.add_argument("--out", type=Path, help="New or empty output directory, outside the source checkout")
    args = parser.parse_args()
    if args.command == "run" and args.out is None:
        parser.error("run requires --out")
    try:
        source = args.source.resolve()
        manifest = verify_source(source)
        if args.command == "verify":
            print(f"Verified pinned HEAD and {len(manifest['sha256'])} required source/data hashes; no analysis run.")
            return 0
        return run(source, args.out.resolve(), manifest)
    except (ValueError, RuntimeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    except ModuleNotFoundError as e:
        print(f"error: missing dependency {e.name}; install requirements.txt", file=sys.stderr)
        return 2
    except OSError as e:
        print(f"error: local I/O or command failed ({e.strerror}); see the acquisition recipe and use a new output directory", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
