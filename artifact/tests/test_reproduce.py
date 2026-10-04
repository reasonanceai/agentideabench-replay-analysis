"""Software regressions using FICTIONAL fixtures, not AgentIdeaBench trials."""

import csv
import gzip
import hashlib
import io
import json
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

PACKAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE))
import reproduce as rep


def write_rows(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def score(model, track="B", index=1, missing=False):
    return {"idea_model": model, "track": track, "subdomain": "fictional subfield",
            "idea_index": str(index), "critic_model": "fictional critic",
            **{f"score_{d}": "" if missing and d == "clarity" else "5.0" for d in rep.DIMS}}


def trace(model="fictional/model-a", index=1, ids=(), iteration=0,
          tool="search_papers", sub="fictional subfield", source="subdomain_ideas"):
    return {"source_table": source, "idea_model": model, "subdomain": sub,
            "idea_index": str(index), "iter": str(iteration), "tool": tool,
            "returned_ss_ids": json.dumps(ids)}


def ref(model, paper, sub="fictional subfield", source="e38_replay_refs"):
    return {"source_table": source, "idea_model": model, "subdomain": sub, "ss_paper_id": paper}


class FictionalFixtureTests(unittest.TestCase):
    def test_primary_roster_filter_keeps_active_only_and_null_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            # Separate locations with spaces; no dependence on a working tree.
            root = Path(tmp)
            source, output = root / "source elsewhere", root / "output elsewhere"
            (source / "reports").mkdir(parents=True)
            output.mkdir()
            rep.write_json(source / "reports/primary_roster.json", {
                "models": ["fictional/paired", "fictional/active-only"]})
            rows = [score("fictional/paired", "B"), score("fictional/paired", "C"),
                    score("fictional/active-only", "C"), score("fictional/late-addition", "B"),
                    score("fictional/paired", "B", index=2, missing=True)]
            write_rows(source / "release_data/core/lit8d_scores_3seed.csv.gz", rows)
            write_rows(source / "release_data/appendix/e38_replay_scores.csv.gz", [score("fictional/paired")])
            write_rows(source / "release_data/core/subdomain_refs.csv.gz", [
                {"subdomain": "fictional subfield", "domain": "fictional domain", "n_refs": "10"}])
            db, counts = rep.hydrate(source, output)
            self.assertEqual(counts["core/lit8d_scores_3seed.csv.gz"], {
                "input_rows": 5, "loaded_rows": 4, "valid_numeric_rows": 3})
            with sqlite3.connect(db) as conn:
                actual = conn.execute("SELECT idea_model, track, scores_json FROM lit8d_scores_3seed").fetchall()
            self.assertEqual([r[:2] for r in actual], [
                ("fictional/paired", "B"), ("fictional/paired", "C"),
                ("fictional/active-only", "C"), ("fictional/paired", "B")])
            self.assertEqual(json.loads(actual[0][2]), dict.fromkeys(rep.DIMS, 5.0))
            self.assertIsNone(actual[-1][2])
            self.assertNotIn(str(root), json.dumps(counts))

    def test_full_join_keys_replicates_duplicates_and_integer_order(self):
        # Same model suffix must not collapse distinct full model identifiers.
        a, b, sub = "fictional/model-a", "other/model-a", "fictional subfield"
        shared = {(a, sub), (b, sub)}
        refs = [ref(a, "fixture-r"), ref(a, "fixture-r"), ref(b, "fixture-q"),
                ref(a, "fixture-z", source="unrelated_table")]
        traces = [trace(a, ids=["fixture-y"], iteration=10),
                  trace(a, ids=["fixture-r", "fixture-r"], iteration=2),
                  trace(a, ids=["fixture-r", "fixture-x"], iteration=3, tool="get_paper_references"),
                  trace(a, index=2, ids=["fixture-z", "", "fixture-z"]),
                  trace(a, index=3), trace(b, ids=["fixture-q"]),
                  trace(a, ids=["outside"], sub=sub + " suffix"),
                  trace(a, ids=["outside"], source="budget_sweep_ideas")]
        result = rep.identifier_trajectories(refs, traces, shared)
        by_key = {(r["idea_model"], r["idea_index"]): r for r in result}
        self.assertEqual(len(result), 4)
        self.assertEqual(by_key[a, 1]["active_unique_ids"], 3)
        self.assertEqual(by_key[a, 1]["replay_ids"], 1)
        self.assertEqual(by_key[a, 1]["active_ids_in_replay"], 1)
        self.assertEqual(by_key[a, 1]["replay_ids_in_first_search"], 1)
        self.assertEqual(by_key[a, 1]["fetch_ids_absent_from_replay"], 1)
        self.assertEqual(by_key[a, 2]["active_unique_ids"], 1)
        self.assertEqual(by_key[a, 2]["replay_coverage_fraction"], 0.0)
        self.assertIsNone(by_key[a, 3]["replay_coverage_fraction"])
        self.assertIsNone(by_key[a, 3]["entire_active_id_set_replayed"])
        self.assertEqual(by_key[b, 1]["replay_coverage_fraction"], 1.0)
        # Scored row without a trace stays missing; empty sets are not matches.
        scored = {(a, sub, i) for i in (1, 2, 3)} | {(b, sub, i) for i in (1, 2)}
        summary = rep.summarize_identifiers(result, shared, scored)
        self.assertEqual(summary["n_scored_active_ideas"], 5)
        self.assertEqual(summary["n_active_trajectories"], 4)
        self.assertEqual(summary["n_nonempty_identifier_trajectories"], 3)
        self.assertEqual(summary["replay_coverage_fraction"]["n"], 3)
        self.assertEqual(summary["n_nonempty_entire_active_id_set_replayed"], 1)
        self.assertEqual(summary["scored_ideas_without_trace_rows"], [[b, sub, 2]])
        self.assertEqual(summary["trace_trajectories_without_scored_rows"], [])

    def test_empty_identifier_denominator_is_not_zero_coverage_or_success(self):
        shared = {("fictional/model-a", "fictional subfield")}
        result = rep.identifier_trajectories([], [trace()], shared)
        summary = rep.summarize_identifiers(result, shared, {("fictional/model-a", "fictional subfield", 1)})
        self.assertEqual(summary["n_active_trajectories"], 1)
        self.assertIsNone(result[0]["entire_active_id_set_replayed"])
        exported = io.StringIO()
        writer = csv.DictWriter(exported, fieldnames=list(result[0]))
        writer.writeheader()
        writer.writerows(result)
        row = next(csv.DictReader(io.StringIO(exported.getvalue())))
        self.assertEqual(row["entire_active_id_set_replayed"], "")
        self.assertEqual(row["replay_coverage_fraction"], "")
        self.assertEqual(summary["replay_coverage_fraction"]["n"], 0)
        self.assertIsNone(summary["replay_coverage_fraction"]["median"])
        self.assertEqual(summary["n_nonempty_entire_active_id_set_replayed"], 0)

    def test_verified_inputs_reject_changed_bytes_and_credentials_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, adapter = Path(tmp) / "source", Path(tmp) / "adapter"
            source.mkdir()
            adapter.mkdir()
            (source / "fictional-input.txt").write_text("fictional bytes\n")
            manifest = {"commit": rep.PIN, "sha256": {
                "fictional-input.txt": hashlib.sha256(b"fictional bytes\n").hexdigest()}}
            rep.write_json(adapter / "source-hashes.json", manifest)
            def local_git(args, **kwargs):
                return SimpleNamespace(returncode=0, stdout=rep.PIN if "rev-parse" in args else "")
            with patch.object(rep, "HERE", adapter), patch.object(rep.subprocess, "run", local_git):
                self.assertEqual(rep.verify_source(source), manifest)
                (source / "fictional-input.txt").write_text("changed bytes\n")
                with self.assertRaisesRegex(ValueError, "differs from the pin"):
                    rep.verify_source(source)
                (source / ".env").write_text("# fictional fixture; no credentials\n")
                with self.assertRaisesRegex(ValueError, "without a .env file"):
                    rep.verify_source(source)

    def test_offline_guards_block_socket_subprocess_and_model_client(self):
        # Separate process: audit hooks are intentionally not removable.
        code = """
import socket, subprocess, reproduce
reproduce.install_offline_guards()
import openai
for attempt in [lambda: socket.getaddrinfo('localhost', 80),
                lambda: socket.socket(),
                lambda: subprocess.run(['never-executed']),
                lambda: openai.OpenAI(api_key='fictional-not-a-key')]:
    try:
        attempt()
    except RuntimeError as error:
        assert 'Offline analysis' in str(error)
    else:
        raise AssertionError('offline guard did not reject the call')
print('four guards rejected without making calls')
"""
        p = subprocess.run([sys.executable, "-c", code], cwd=PACKAGE, capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("four guards rejected", p.stdout)

    def test_cli_and_public_files_are_portable(self):
        public = ["reproduce.py", "requirements.txt", "source-hashes.json", "README.md",
                  "LICENSE", "LICENSE-UPSTREAM", "NOTICES.md", ".gitignore"]
        with tempfile.TemporaryDirectory() as tmp:
            package, elsewhere = Path(tmp) / "portable package", Path(tmp) / "another cwd"
            package.mkdir()
            elsewhere.mkdir()
            for name in public:
                shutil.copyfile(PACKAGE / name, package / name)
                content = (package / name).read_text(encoding="utf-8")
                for forbidden in (str(PACKAGE), str(Path(tmp))):
                    self.assertNotIn(forbidden, content, name)
            p = subprocess.run([sys.executable, str(package / "reproduce.py"), "--help"],
                               cwd=elsewhere, capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn("--source", p.stdout)
            self.assertIn("--out", p.stdout)


if __name__ == "__main__":
    unittest.main()
