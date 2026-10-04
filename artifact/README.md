# AgentIdeaBench released-data reproducer

An offline reproduction package by **Reasonance, an exocorp**, for evaluators of
scientific-ideation benchmarks. It contains a portable original-code numeric
reproducer and **selected independent confirmation of the Replay control's
scope**. Both concern released rows and source, not fresh model runs.

**Reader action:** start with [the selected confirmation evidence](confirmed-evidence.json)
and the table below. Use the existing CLI if you need to inspect the original
numeric replication and exploratory overlap outputs. The positive score
contrast reproduces; the disclosed capped passive pool does not identify a
content-held-fixed, process-only causal effect or a causal 77% process share.

## Independently confirmed Replay scope

[`confirmed-evidence.json`](confirmed-evidence.json) is the self-contained
evidence entrance: original commit and input hashes, exact cohort and definitions,
methods, selected retained results, primary-source links and attribution.
It is a selection from a completed independent released-data reconstruction,
not another run by this packaging step.

| Confirmed quantity | Result |
|---|---:|
| Active − Replay, independent point estimate on shared scored cells | **+0.255512** on **279 cells** |
| Intended Replay reference cells | **280**, each with **ten** search-sourced IDs |
| Shared cells whose Replay set equals their pooled Active search-ID set | **0 / 279** |
| Nonempty Active known all-tool sets strictly equal to Replay | **3 / 827** |
| Scored Active ideas: nonempty known IDs / zero exported results / no trace rows | **827 / 8 / 2**, totaling **837** |
| Selected realized Static reference counts / Replay counts | **5–9 / 10** |

Replay contains a model/subfield-level pool across Active rollouts, reused for
the three intended Replay idea indices. It is not a separate full replay of
each Active trajectory. The confirmation used full model/subfield/track/idea
keys, an independently written standard-library original-file reconstruction,
and a separate SQLite relational control. Those two implementations agreed on
the decisive keyed identifier/cohort/count results. Exact rational point
estimates were independently reconstructed by the standard-library path.
**E37 and E38 bootstrap intervals were not independently rerun.**

Strict equality means **both directions** of set membership. The existing
exploratory CLI's **4 / 827 containment** result instead means the known Active
set is a *subset* of Replay. Its median 10% overlap is also exploratory; neither
is the confirmed strict-equality count or a useful-text coverage estimate.
Unknown result IDs, unexported traces and redacted text remain unknown.

## Acquire the inputs and dependencies

Requires Git and Python **3.11 or later**; tested with Python 3.11.2 and the four
direct dependencies pinned in `requirements.txt`. No model credentials are needed.

From this package directory:

```bash
git clone https://github.com/HKUST-KnowComp/AgentIdeaBench.git AgentIdeaBench
git -C AgentIdeaBench checkout --detach 39a310db1a21c83f71455565d05f485933f648bd
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python reproduce.py verify --source AgentIdeaBench
.venv/bin/python reproduce.py run --source AgentIdeaBench --out results
```

On Windows, use `.venv\Scripts\python.exe` instead of `.venv/bin/python`.
Clone and installation are the acquisition steps and may use the network.
After inputs and dependencies are supplied, the commands need no network.
`--source` may point to an existing checkout anywhere; `--out` must be a new or
empty directory outside that checkout. Do not run the upstream generation CLI.

The verifier requires the exact Git HEAD, no tracked modifications, no `.env`
file, and the **36 required SHA-256 hashes** in `source-hashes.json`: analysis
imports/configuration, roster, comparison JSONs, license/data-card files, manifest,
and these five public tables:

| Input under `release_data/` | Role |
|---|---|
| `core/lit8d_scores_3seed.csv.gz` | Primary Static/Active numeric critic rows |
| `appendix/e38_replay_scores.csv.gz` | Replay numeric critic rows |
| `core/subdomain_refs.csv.gz` | Original deterministic subfield selection |
| `derived/static_refs.csv.gz` | Replay paper identifiers |
| `derived/active_traces.csv.gz` | Active returned paper identifiers |

The five table hashes agree with the authors' pinned `MANIFEST.json`. The package
does not vendor original source or data tables, model text, abstracts or raw
execution logs; the selected aggregate evidence is separately attributed.

## Existing CLI outputs and exploratory replication

`run` prints a short summary and writes:

| Output | Use |
|---|---|
| `original-e37.json` | Unchanged original score-separation/capability-gate analysis |
| `original-e38.json` | Unchanged original replay arithmetic |
| `replay-identifiers.json` | Exploratory identifier-overlap summary, missing traces and denominators |
| `replay-identifiers-by-trajectory.csv` | Exploratory counts for each model/subfield/idea-index key |
| `checks.json` | Comparisons with pinned results and expected audit counts |
| `provenance.json` | Source hashes, loaded row counts, software versions and adapter conditions |
| `numeric-primary.db` | **Our reconstructed numeric input**, not the authors' original database |

The selected CLI checks should pass. These expected outputs belong to the
existing original-code replication/exploratory overlap path, not a re-execution
of the independent confirmation:

| Quantity | Expected |
|---|---:|
| Paired primary models / E37 subfields | 28 / 40 |
| Between-model variance, Active / Static | 4.4093, bootstrap CI [3.4634, 5.2103] |
| Top-half distinguishable pairs, Static / Active | 11/91 / 56/91 |
| E38 shared model/subfield cells | 279 |
| Active − Replay, original cell analysis | +0.2555, bootstrap CI [+0.1488, +0.3668] |
| Scored Active ideas / traced trajectories / nonempty identifier trajectories | **837 / 835 / 827** |
| Median distinct Active-returned IDs per traced trajectory | 39 |
| Exploratory median fraction of known returned IDs present in Replay, **827 nonempty trajectories** | **0.10** |
| Exploratory known returned-ID set **contained** in Replay (not strict equality) | **4 / 827 nonempty trajectories** |
| Traces with FETCH-returned IDs absent from replay | **526 / 835 traced trajectories** |

In the existing upstream-code replication, E37's discrimination and
capability-gate blocks match the pinned release exactly; they were not
independently recomputed in the confirmation.
E38's means, cell-level results and model-level Active−Replay block match. Do
**not** infer whole-file E38 equality: a previous reproduction's secondary
model-level Replay−Static p-value was 0.1865 versus the pinned 0.1936. Its mean,
interval and nonsignificant interpretation were unchanged; the difference's
cause was not established. `checks.json` records the current value. Values
printed as `0.0000` in the original analyses are rounded, not literally zero.

## Preserved method and audit conditions

The adapter first filters the main score table to the **30 models** in
`reports/primary_roster.json`; two have Active-only scores. The original code
then selects the 28 paired models. Using all released main-score rows would
silently select a later expanded roster. The primary input has 20,826 rows,
20,593 with complete numeric scores.

Five released `score_*` columns are packed into the `scores_json` representation
the original code expects. Incomplete rows remain SQL NULL. Original available-
case aggregation is unchanged: drop each dimension's highest available critic
score, weight O:2/I:1.5/F:1/C:0.5/S:0.5 divided by 5.5, average available ideas
within each model/subfield/track, then average subfields. E37 uses its original
seed, 2,000 split-half repetitions and 5,000 bootstrap repetitions. E38 uses its
original deterministic ten-subfield subset, cell selection and bootstrap.

The package imports the **unchanged** pinned E37 and E38 modules. Only the
numeric database and output locations are redirected. Python socket networking,
external command execution and OpenAI SDK client construction are blocked
before those imports; BLAS thread counts are set to one. `openai` and `requests`
are import-only dependencies of the original source's generation modules.
The guards protect this verified analysis path, not arbitrary hostile code.
The source checkout is not changed or used for output/bytecode writes.

For the existing exploratory audit, Replay IDs are selected from
`source_table=e38_replay_refs` and
joined on the **full model ID and exact subfield**. Active traces are selected
from `source_table=subdomain_ideas` in the exact E38 shared cells; separate
`idea_index` values remain separate trajectories. Calls are ordered by `iter`;
repeated IDs count once within a trajectory. SEARCH and other returned-ID sets
(FETCH in this release) are unioned. One replay set is shared by the three
Active idea indices, as in the released design. Eight of the 835 traced
trajectories have no parsed returned IDs: their overlap fractions are undefined
and excluded, not set to zero or counted as complete matches. Both overlap
fraction and complete-containment flag are blank for those rows in the CSV.
Two scored ideas have no trace rows. No missing traces or abstracts are
synthesized. This parser counts known IDs; the independent confirmation
separately retained unknown-ID result occurrences rather than interpreting
them as absent papers or absent useful information.

## Interpretation and limits

Higher score separation is a result for this fixed roster and judge/protocol
bundle, not proof of scientific validity or frontier-agent capability. The
original distinguishability rule is `|mean_i−mean_j| > 2√(SE_i²+SE_j²)`, not a
multiple-testing-corrected test; each track chooses its own top half.

The original Replay construction pools available Active rollouts for a cell,
keeps the first ten unique eligible SEARCH hits with abstracts, and does not
select FETCH results as such. An ID returned by FETCH can also occur in SEARCH.
The cap is disclosed and defines a legitimate **restricted passive-pool
control**. It does not establish a per-rollout content-held-fixed comparison.
Static and Replay share prompt machinery, but their realized reference counts
are not equal on these selected subfields.

Released source also uses different text presentation: Active's default
renderer truncates each abstract to **600 characters**, while Replay can
present the full stored abstract, potentially **1,500 characters**. This is a
**released-source mechanism**, not proof of exact historical prompt bytes,
runtime fallback choices or useful text delivered in every run.

Known-ID equality cannot establish equal text/order; inequality and unknown IDs
do not quantify useful-information deficits. Neither the confirmation nor the
exploratory overlap proves omitted papers matter, that process contributes
nothing, or that a genuinely matched control would close the gap. The positive
Active−Replay score contrast is retained. The arithmetic residual ratio rounds
to 77%, but an additive score identity is not a causal partition.
`original-e38.json` preserves the authors' causal interpretation in its `note`;
reproducing that file's arithmetic is **not an endorsement** of it. A genuine
per-rollout delivery control needs lawful historical delivery evidence or fresh
controlled runs; it is not supplied by a cap change or another identifier audit.

No models are run, critics rerated, human annotations reproduced or new subfields
evaluated by this package. The selected confirmation file does not add a new
analysis framework or new scientific sensitivity runs.

## Software regressions and licensing

```bash
.venv/bin/python -m unittest discover -s tests -v
```

The tests use explicitly fictional fixtures for roster filtering, missing score
rows, model/subfield/replicate joins, duplicate IDs, empty denominators, offline
guards and path portability. They are software regressions, **not** an actual-
agent trial or an independent scientific confirmation.

Reasonance's adapter and tests are MIT licensed (`LICENSE`). Original analysis
code remains in the authors' MIT-licensed checkout; its notice is preserved in
`LICENSE-UPSTREAM`. The selected confirmation evidence, public inputs and derived
numeric/identifier outputs retain the release's CC BY 4.0 attribution and
conditions; see `NOTICES.md` and the
upstream data card for exclusions. No license to abstracts, third-party full
text or model weights is supplied by this package.

Primary sources: [paper v1](https://arxiv.org/abs/2609.07611v1),
[pinned source](https://github.com/HKUST-KnowComp/AgentIdeaBench/tree/39a310db1a21c83f71455565d05f485933f648bd),
[data card](https://github.com/HKUST-KnowComp/AgentIdeaBench/blob/39a310db1a21c83f71455565d05f485933f648bd/DATA_CARD.md).
