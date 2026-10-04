# Supporting reproducer for the AgentIdeaBench article

*Reasonance, an empirical research exocorp*

This package supports [the article on active search and passive replay](../note/NOTE.md). Start there for the benchmark task and interpretation. Here you can inspect the evidence or reproduce the original numerical analyses from the released inputs.

There are **two evidence paths**, not two interchangeable reproductions:

- **Runnable original-code reproduction and exploratory identifier analysis:** the existing `reproduce.py` CLI adapts released numeric rows for the unchanged authors' analyses and reports exploratory paper-ID overlap.
- **Selected independent reconstruction evidence:** `confirmed-evidence.json` supplies retained aggregates, definitions and provenance from a separately completed reconstruction of original released files. **This package does not regenerate that independent reconstruction.** That independent reconstruction did not recompute the score-separation analysis or bootstrap intervals.

No fresh models or critics are run. Choose a next step:

- **[Read the evidence summary](#evidence-summary)** without installing anything.
- **[Run the original-code reproducer](#obtain-the-package-and-run-the-reproducer)** to inspect the original calculations and exploratory outputs locally.
- **[Inspect the JSON evidence](confirmed-evidence.json)** for exact values, cohort definitions, input hashes and attribution. Its score-mean keys `B` and `C` mean **Static** and **Active**; `Replay` means Replay. The JSON is machine-readable support, not a substitute for the article or summary.

## Evidence summary

The separate reconstruction retains a positive Active−Replay score contrast. Replay is a **capped, search-only passive pool across a model/subfield's separate Active runs**, reused for three intended new proposals. It is not a content-matched replay of each individual run.

| Selected independently reconstructed quantity | Result |
|---|---:|
| Active−Replay mean weighted critic-score difference | **+0.255512** on **279 shared model–subfield combinations** |
| Intended Replay pools | **280**, each with **ten** search-sourced IDs |
| Shared combinations whose Replay set equals the pooled Active search-ID set | **0 / 279** |
| Nonempty Active SEARCH-or-FETCH ID sets strictly equal to Replay | **3 / 827** |
| Scored Active proposals: nonempty known IDs / zero exported results / no trace rows | **827 / 8 / 2**, totaling **837** |
| Realized Static reference counts / Replay counts in the selected subfields | **5–9 / 10** |

Strict equality means both sets contain exactly the same IDs. The runnable exploratory CLI instead reports **4/827 containment**: the known Active set is a *subset* of Replay, not necessarily equal. Its median 10% overlap is exploratory too. Neither quantity estimates useful-text coverage. The eight zero-result cases have trace rows; the other two do not. Null IDs, missing traces and withheld text remain unknown, not evidence of absent historical retrieval or absent useful information.

The independent reconstruction used full model/subfield/condition/proposal keys, a separately written standard-library path from original files, and a separate SQLite relational control. The two implementations agreed on the decisive identifier, cohort and count results. Exact rational score point estimates were reconstructed by the standard-library path. **E37 and E38 bootstrap intervals were not independently rerun.** E37 and E38 are the authors' experiment names for score separation and the replay comparison, respectively.

The retained result is a contrast in critic ratings, not an observation of scientific success. The pool is a legitimate restricted intervention, but does not identify a process-only causal effect or a causal **77% process share**. See [the article](../note/NOTE.md) for the explanation and a matched-comparison design.

## Obtain the package and run the reproducer

Requires Git and Python **3.11 or later**; tested with Python 3.11.2 and the four direct dependencies pinned in `requirements.txt`. No model credentials are needed.

First acquire **this Reasonance repository** and enter its package directory:

```bash
git clone https://github.com/reasonanceai/agentideabench-replay-analysis.git
cd agentideabench-replay-analysis/artifact
```

Run the following commands **from `agentideabench-replay-analysis/artifact`**. They acquire the upstream inputs at the required revision, install dependencies, verify the inputs and produce the original-code/exploratory outputs:

```bash
git clone https://github.com/HKUST-KnowComp/AgentIdeaBench.git AgentIdeaBench
git -C AgentIdeaBench checkout --detach 39a310db1a21c83f71455565d05f485933f648bd
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python reproduce.py verify --source AgentIdeaBench
.venv/bin/python reproduce.py run --source AgentIdeaBench --out results
```

On Windows, use `.venv\Scripts\python.exe` instead of `.venv/bin/python`. Clone and installation are acquisition steps and may use the network. After inputs and dependencies are supplied, verification and reproduction need no network. `--source` may point to an existing checkout anywhere; `--out` must be a new or empty directory outside that checkout. **Do not run the upstream generation CLI.**

### What is verified

The verifier requires the exact Git HEAD, no tracked modifications, no `.env` file, and the **36 required SHA-256 hashes** in `source-hashes.json`: analysis imports/configuration, roster, comparison JSONs, license/data-card files, manifest, and these five public tables:

| Input under `release_data/` | Role |
|---|---|
| `core/lit8d_scores_3seed.csv.gz` | Primary Static/Active numeric critic rows |
| `appendix/e38_replay_scores.csv.gz` | Replay numeric critic rows |
| `core/subdomain_refs.csv.gz` | Original deterministic subfield selection |
| `derived/static_refs.csv.gz` | Replay paper identifiers |
| `derived/active_traces.csv.gz` | Active returned paper identifiers |

The five table hashes agree with the authors' pinned `MANIFEST.json`. The package does not vendor original source, full data tables, model text, abstracts or raw execution logs. The independently reconstructed aggregate evidence is supplied separately and attributed in `NOTICES.md`.

## Read the local outputs

`run` prints a short summary and writes:

| Output | What it contains |
|---|---|
| `original-e37.json` | Results from the unchanged original score-separation and related analyses |
| `original-e38.json` | Results from the unchanged original replay arithmetic |
| `replay-identifiers.json` | Exploratory identifier-overlap summary, missing traces and denominators |
| `replay-identifiers-by-trajectory.csv` | Exploratory counts for each model/subfield/proposal-index key |
| `checks.json` | Comparisons with pinned results and expected audit counts |
| `provenance.json` | Source hashes, loaded row counts, software versions and adapter conditions |
| `numeric-primary.db` | **Reasonance's reconstructed numeric input**, not the authors' original database |

The selected CLI checks should pass. The following expectations belong to the **original-code/exploratory path**. Running the CLI does not rerun the independent reconstruction described in the evidence summary.

| Quantity | Expected |
|---|---:|
| Paired primary models / E37 subfields | 28 / 40 |
| Between-model score variance, Active/Static | 4.4093, bootstrap CI [3.4634, 5.2103] |
| Top-half pairs meeting the authors' separation rule, Static / Active | 11/91 / 56/91 |
| E38 shared model/subfield combinations | 279 |
| Active−Replay, original cell analysis | +0.2555, bootstrap CI [+0.1488, +0.3668] |
| Scored Active proposals / traced runs / nonempty known-ID runs | **837 / 835 / 827** |
| Median distinct Active-returned IDs per traced run | 39 |
| Exploratory median fraction of known returned IDs present in Replay, among 827 nonempty runs | **0.10** |
| Exploratory known returned-ID set contained in Replay, not strict equality | **4 / 827 nonempty runs** |
| Traces with FETCH-returned IDs absent from Replay | **526 / 835 traced runs** |

E37's discrimination and capability-gate blocks match the pinned release exactly in the upstream-code reproduction; the independent confirmation did not recompute them. E38's means, cell-level results and model-level Active−Replay block match. Do **not** infer whole-file E38 equality: a previous reproduction's secondary model-level Replay−Static p-value was 0.1865 versus the pinned 0.1936. Its mean, interval and nonsignificant interpretation were unchanged; the difference's cause was not established. `checks.json` records the current value. Values printed as `0.0000` in the original analyses are rounded, not literally zero.

## Method and scope of the runnable path

### Numeric adapter

The adapter first filters the main score table to the **30 models** in `reports/primary_roster.json`; two have Active-only scores. The original code then selects the 28 paired models. Using all released main-score rows would silently select a later expanded roster. The primary input has 20,826 rows, 20,593 with complete numeric scores.

Five released `score_*` columns are packed into the `scores_json` representation the original code expects. Incomplete rows remain SQL NULL. Original available-case aggregation is unchanged: for each dimension, drop the highest available critic score when at least two exist; weight originality:2, impact:1.5, feasibility:1, clarity:0.5 and specificity:0.5, normalized by 5.5. Average available proposals within each model/subfield/condition, then average subfields. E37 uses its original seed, 2,000 split-half repetitions and 5,000 bootstrap repetitions. E38 uses its original deterministic ten-subfield subset, cell selection and bootstrap.

The authors' top-half separation rule is `|mean_i−mean_j| > 2√(SE_i²+SE_j²)`, using bootstrap standard errors, not a multiple-testing-corrected test. Each condition chooses its own top half. Greater between-model spread can distinguish model ratings under this protocol; it is not proof that those ratings capture real scientific quality.

### Offline execution boundary

The package imports the **unchanged** pinned E37 and E38 modules. Only the numeric database and output locations are redirected. Python socket networking, external command execution and OpenAI SDK client construction are blocked before those imports; BLAS thread counts are set to one. `openai` and `requests` are import-only dependencies of the original source's generation modules. The guards protect this verified analysis path, not arbitrary hostile code. The source checkout is not changed or used for output/bytecode writes.

### Exploratory identifier analysis

Replay IDs are selected from `source_table=e38_replay_refs` and joined on the **full model ID and exact subfield**. Active traces are selected from `source_table=subdomain_ideas` in the exact E38 shared scored combinations. Separate `idea_index` values remain separate runs; calls are ordered by `iter`, and repeated IDs count once within a run. SEARCH and other returned-ID sets (FETCH in this release) are unioned. One Replay set is compared with each of the three Active proposal indices, as in the released design.

Eight of the 835 traced runs have no parsed returned IDs. Their overlap fractions are undefined and excluded, not set to zero or counted as complete matches. Both overlap fraction and containment flag are blank for those rows in the CSV. Two scored proposals have no trace rows. No missing traces or abstracts are synthesized. This parser counts known IDs; the independent reconstruction separately retained unknown-ID result occurrences rather than interpreting them as absent papers or absent useful information.

## Interpret the results within the tested intervention

Replay pools eligible SEARCH hits across available Active runs for a model/subfield, deduplicates and caps them at ten, and reuses the pool for three intended new outputs. FETCH results are not selected as such; the same paper ID can appear in SEARCH. Static and Replay share prompt machinery, but their realized reference counts differ in the selected subfields.

Released source also differs in text presentation: Active's default renderer truncates abstracts at **600 characters**, while Replay can present a stored abstract of up to **1,500 characters**. This describes source mechanisms, not the exact historical prompt bytes, fallback choices or useful text delivered in every run. Equal IDs would not establish equal text/order; unequal IDs do not measure omitted papers' usefulness or score impact.

The positive Active−Replay contrast is retained. The arithmetic residual ratio rounds to 77%, but an additive score identity is not a causal partition. `original-e38.json` preserves the authors' causal interpretation in its `note`; reproducing the arithmetic is **not an endorsement** of that interpretation. A genuinely matched delivery control requires lawful historical delivery evidence or fresh specified experiments, not a cap change, silent refetch or another identifier audit. Neither path establishes that process contributes nothing or that matching delivery would close the gap.

No models are run, critics rerated, human annotations reproduced or new subfields evaluated by this package. The selected evidence file does not add a new analysis framework or scientific sensitivity runs.

For a question, correction or reproducer problem, see [the repository's question route](../README.md#questions-and-corrections).

## Software regressions and licensing

To run the software regression tests from the same `artifact` directory:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

The tests use explicitly fictional fixtures for roster filtering, missing score rows, model/subfield/proposal joins, duplicate IDs, empty denominators, offline guards and path portability. They are **software tests**, not an actual-agent trial or an independent scientific confirmation.

Reasonance's adapter and tests are MIT licensed ([`LICENSE`](LICENSE)). Original analysis code remains in the authors' MIT-licensed checkout; its notice is preserved in [`LICENSE-UPSTREAM`](LICENSE-UPSTREAM). Selected confirmation evidence, public inputs and derived numeric/identifier outputs retain the release's CC BY 4.0 attribution and conditions; see [`NOTICES.md`](NOTICES.md) and the upstream data card for exclusions. No license to abstracts, third-party full text or model weights is supplied by this package.

Primary sources: [paper v1](https://arxiv.org/abs/2609.07611v1), [pinned source](https://github.com/HKUST-KnowComp/AgentIdeaBench/tree/39a310db1a21c83f71455565d05f485933f648bd), [data card](https://github.com/HKUST-KnowComp/AgentIdeaBench/blob/39a310db1a21c83f71455565d05f485933f648bd/DATA_CARD.md).
