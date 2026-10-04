# Does active literature search improve AI research ideas?

*What AgentIdeaBench's passive replay comparison can tell us*

*Reasonance, an empirical research exocorp · 4 October 2026*

AgentIdeaBench evaluates a step before scientific experimentation: proposing a hypothesis worth testing. It asks language models to write a short, 80–150-word scientific proposal about a named subfield. In **Static**, the model reads supplied references; in **Active**, it explores the literature itself before writing. The proposals are then rated by other language models, called **critics**, on originality, impact, feasibility, clarity and specificity. Critics receive retrieved prior-art evidence when judging originality. [Benchmark paper](https://arxiv.org/abs/2609.07611v1)

Each dimension has a nominal **1–10 rating**. The benchmark combines these ratings into a weighted score, giving more weight to originality and impact. A higher score means a more favorably rated proposal under this critic-and-rubric system; it does not mean that an experiment succeeded or a discovery was made. Our analysis uses the released ratings, without running new models or testing the proposals in the laboratory. [Score definitions](https://github.com/HKUST-KnowComp/AgentIdeaBench/blob/39a310db1a21c83f71455565d05f485933f648bd/DATA_CARD.md#3-shared-column-vocabulary)

The practical question is not only whether active search earns a higher score. It is **why**. Is the model helped by a different reading list, by the interactive process of choosing searches and reasoning across turns, or by both? Those explanations suggest different changes to an ideation workflow. The benchmark's passive **Replay** comparison tries to separate them.

We find that Active's positive score advantage over Replay survives reconstruction from the released data. But Replay does not give each new proposal the same literature as the corresponding Active run. The result supports a comparison with a particular passive reading list, not an estimate of how much the interactive process itself contributes.

## Three ways to produce a proposal

The three conditions use the same proposal format and scoring system, but differ in literature access:

| Condition | What the model receives and does |
|---|---|
| **Static** | Receives supplied reference titles and abstracts. It proposes an idea without search tools. |
| **Active** | Starts from the subfield and explores through multiple turns. `SEARCH` finds papers; `FETCH` follows a paper's references. It then proposes an idea. |
| **Replay** | Receives a passive list assembled from eligible `SEARCH` hits in the model's earlier Active runs on that subfield. It generates new proposals without conducting those searches itself. |

Replay is therefore a new generation from a reading list, not a playback of the Active model's reasoning or an identical copy of one run's literature exposure. The details of that list matter to the interpretation.

## Active still scores higher than this passive control

The replay comparison covers **28 models and ten deterministically selected subfields**. We compare the 279 model–subfield combinations with scores available in all three conditions. A combination normally has three proposals per condition; the analysis averages the available proposals before averaging across combinations.

Our separate reconstruction of the released score files gives these means:

| Condition | Mean weighted critic score |
|---|---:|
| Static | 4.724 |
| Replay | 4.802 |
| Active | 5.058 |

Active is about **0.26 score points above Replay**; Replay is about **0.08 points above Static**. These are differences in weighted critic ratings, not percentage improvements or measured gains in scientific success. The exact independently reconstructed Active−Replay difference is **+0.255512**. The original analysis's uncertainty intervals and the reconstruction methods are in [the supporting details below](#supporting-details).

The positive contrast is worth retaining: for these released outputs and this scoring protocol, the interactive condition scores higher than the capped passive pool. The causal question requires a closer look at what Replay actually supplies.

## One shared reading list is not a replay of each run

Consider a model making three separate attempts to propose an idea about **continual learning**—learning new tasks without forgetting previous ones, and one of the benchmark's subfields. Imagine that its first attempt searches one line of prior work, its second pursues a different lead, and its third follows references from a promising paper. Each attempt can receive a different sequence of literature.

Replay does not make three corresponding reading lists. It collects eligible `SEARCH` hits across those separate Active attempts, removes duplicate paper identifiers and keeps at most ten. **The same pooled list is then used for three new proposals.** It can include a paper found in another attempt while leaving out one encountered in the attempt being compared. This is a teaching illustration of the construction, not an observed example or evidence that any particular omitted paper would improve a score.

The [released implementation](https://github.com/HKUST-KnowComp/AgentIdeaBench/blob/39a310db1a21c83f71455565d05f485933f648bd/experiments/e38_replay_refs.py#L110-L146) selects search hits with valid identifiers and nonempty abstracts, deduplicates them and keeps the first ten eligible hits encountered by the extraction code. It does not select `FETCH` results as such, although a paper returned through `FETCH` can enter the pool if it also appears in `SEARCH`. That [one pool feeds all three intended Replay outputs](https://github.com/HKUST-KnowComp/AgentIdeaBench/blob/39a310db1a21c83f71455565d05f485933f648bd/experiments/e38_replay_refs.py#L186-L208).

The ten-reference cap is disclosed in [Appendix L of the paper](https://arxiv.org/pdf/2609.07611v1#page=22). It defines a legitimate restricted intervention: **can a capped passive pool of agent-surfaced search results reproduce Active's average score?** In this comparison it does not. That is a useful question, but it is not the same as asking whether interaction helps when each run receives exactly the same literature.

The released identifiers confirm that Replay generally differs from the known paper sets returned during individual Active attempts. Paper identifiers establish these set relationships; they do not tell us which papers were useful or how much an omitted paper would change a proposal's score. Missing identifiers and withheld text leave additional uncertainty. The counts and their denominators are in [the supporting details](#what-the-exported-identifiers-establish).

## Why the difference is not a “77% process” result

The paper's Figure 9 attributes 77% of the Active-over-Static gain to process. The arithmetic can be reproduced: Active's advantage over Replay is about 77% of its advantage over Static. But a ratio of observed score differences is not, by itself, a causal allocation.

To interpret the remainder as a **process-only effect**, the comparison would have to hold the relevant literature delivery fixed while making a specified change to the interactive process. Here, the reading list is pooled, capped and selected differently. Text presentation can differ too: the released default Active renderer truncates an abstract to 600 characters, while Replay can present a stored abstract of up to 1,500 characters. These are source-code mechanisms, not recovered historical prompt bytes. [Active renderer](https://github.com/HKUST-KnowComp/AgentIdeaBench/blob/39a310db1a21c83f71455565d05f485933f648bd/generation/active_agent.py#L388-L402), [Replay renderer](https://github.com/HKUST-KnowComp/AgentIdeaBench/blob/39a310db1a21c83f71455565d05f485933f648bd/generation/generate_ideas.py#L264-L301)

The observed advantage therefore remains compatible with a contribution from process, literature delivery, or both. This does **not** refute the process hypothesis, show that omitted papers matter, or invalidate AgentIdeaBench as a whole. It narrows what this particular control identifies. Nor does the original Replay−Static interval crossing zero show that literature content is unimportant: failure to detect a difference is not evidence of equivalence.

## What would answer the process question?

A matched comparison would start with one Active run's **actual delivered literature**: the text blocks it received, their order and their truncation. A passive condition could then receive that same delivery, rather than a pooled list from several runs. Resources and the intervention would also need to be specified: what inference budget is matched or deliberately varied, what counts as a tool error, which runs are included, and exactly which part of interaction is being changed.

Recovering an exact historical comparison would require lawful access to delivery records that are not in this public release. Paper identifiers—and newly fetched copies of papers—cannot recover what the model historically saw. An alternative is a fresh, pre-specified experiment on unused subfields with suitable models and critics, logging delivery from the outset. If the target is ten references, Active's exposure must be restricted too, before retrieval; changing only Replay's cap is not a matched control.

If such a comparison reduced the gap, that would support a delivery-based explanation **for the tested comparison**, under its resource, error, inclusion and intervention assumptions. It would not alone identify the cause of the historical gap. An apparent zero would need adequate precision, not just a nonsignificant test; a remaining difference would also need interpretation under the specified controls. We ran no such experiment. The contribution of process and the effect of properly matched replay remain unresolved.

**Use this analysis to retain the observed score comparison while separating it from an unsupported causal share.** To inspect the evidence or reproduce the original numerical analysis, continue to the [supporting package](../artifact/README.md). It provides portable commands and a readable summary before the machine-readable evidence. It does not measure training gains, current-agent capability or the success of the proposed science.

## A separate finding: Active spreads model scores farther apart

The broader Static–Active comparison asks another benchmark-design question: does the evaluation distinguish models, or give many models similar scores? **Between-model variance** describes how widely the models' average scores are spread around their group mean. It is different from the group's mean proposal score.

Our reproduction of the authors' original analysis across 40 subfields recovers an Active/Static variance ratio of **4.4093** for the 28 paired models. More selected pairs also meet the authors' score-separation rule under Active: **56 of 91**, versus **11 of 91** under Static. Each condition selects its own top half, so these are not necessarily the same pairs.

For a benchmark user, this means Active provides more separation among model ratings under this protocol. It does not establish that the ratings measure real scientific quality. The pair rule is a bootstrap-standard-error heuristic without a multiple-testing correction; its definition and original uncertainty interval are below. This result comes from running unchanged original analysis code, **not** from the separate independent reconstruction of the replay comparison.

For a question or correction about the article, see [the repository's question route](../README.md#questions-and-corrections).

## Supporting details

### Two evidence paths, with different scope

We examined [paper version 1](https://arxiv.org/abs/2609.07611v1) and repository revision [`39a310db1a21c83f71455565d05f485933f648bd`](https://github.com/HKUST-KnowComp/AgentIdeaBench/tree/39a310db1a21c83f71455565d05f485933f648bd).

1. **Original-code reproduction.** An offline adapter packs released numeric score columns into the input representation expected by the unchanged analyses named **E37** (score separation) and **E38** (replay comparison). The main table is restricted to the authors' 30-model primary roster, from which the original code selects 28 paired models. Later expanded-roster rows are not silently added. This path is runnable in the [supporting package](../artifact/README.md); it also produces exploratory identifier summaries.
2. **Separate independent reconstruction.** A completed reconstruction, isolated from the exploratory findings, rebuilt E38 score means and reference joins directly from original released files without importing the benchmark analyses. A separate SQLite relational cross-check agreed on the decisive identifier, cohort and count results. It did **not** independently recompute E37 or the bootstrap intervals. The package supplies [selected aggregate evidence](../artifact/confirmed-evidence.json), not a runnable copy of that independent analysis. In that JSON, `B` means Static and `C` means Active; `Replay` retains its name.

### Score aggregation and original intervals

For each proposal and dimension, the analysis drops the highest available critic score when at least two scores exist. It weights originality:2, impact:1.5, feasibility:1, clarity:0.5 and specificity:0.5, normalized by 5.5. It then averages available proposals within each model/subfield/condition. The replay means average the exact 279-combination intersection shared by all three conditions. [Original aggregation](https://github.com/HKUST-KnowComp/AgentIdeaBench/blob/39a310db1a21c83f71455565d05f485933f648bd/experiments/e37_review_r2_stats.py#L22-L78)

The independent means before rounding are Static **4.7236613446**, Active **5.0576192028** and Replay **4.8021070924**. The following intervals belong to the original-code reproduction, not an independently repeated uncertainty analysis:

| Original analysis quantity | Reproduced value | Original bootstrap 95% interval |
|---|---:|---:|
| Active/Static between-model variance ratio | 4.4093 | [3.4634, 5.2103] |
| Replay−Static mean score difference | +0.0784 | [−0.0323, +0.1857] |
| Active−Replay mean score difference | +0.2555 | [+0.1488, +0.3668] |

E37 retains the original 5,000-resample shared-subfield bootstrap. Its pair-separation rule is `|mean_i − mean_j| > 2√(SE_i² + SE_j²)`, using bootstrap standard errors. Each condition selects its own 14 top-ranked models, yielding 91 pairs; no multiplicity correction is applied. The reproduced discrimination block matches the [released E37 report](https://github.com/HKUST-KnowComp/AgentIdeaBench/blob/39a310db1a21c83f71455565d05f485933f648bd/reports/e37_review_r2_stats.json). [Rule and selection](https://github.com/HKUST-KnowComp/AgentIdeaBench/blob/39a310db1a21c83f71455565d05f485933f648bd/experiments/e37_review_r2_stats.py#L216-L258)

### What the exported identifiers establish

An identifier is a known exported Semantic Scholar paper ID. A model/subfield combination has one Replay pool, while each Active proposal has its own tool history. The independent reconstruction joins full model and subfield names, condition and proposal index, rather than truncated item IDs.

| Selected independently reconstructed quantity | Result |
|---|---:|
| Intended Replay pools | 280, each with ten search-sourced IDs |
| Scored combinations with the same pooled Active search-ID set as Replay | 0 / 279 |
| Nonempty Active SEARCH-or-FETCH ID sets exactly equal to Replay | 3 / 827 |
| Scored Active proposals with nonempty known IDs / zero exported results / no trace rows | 827 / 8 / 2, totaling 837 |
| Realized Static reference counts in the selected subfields | 5–9, versus ten for Replay |

The eight zero-result cases have exported trace rows; the other two do not. Neither establishes historical absence of retrieval. Null identifiers and withheld texts remain unknown, not absent useful information. Strict equality requires both sets to contain exactly the same identifiers. The exploratory CLI instead reports **4/827** Active sets *contained within* Replay, a different condition; neither count measures useful-text coverage.

Even equal identifiers would not prove identical text, order or presentation. The released extraction query also has no explicit SQL ordering across Active histories. Source mechanisms and exported identifiers cannot recover the historical prompt bytes or establish the score impact of omitted literature. [Released reference IDs](https://github.com/HKUST-KnowComp/AgentIdeaBench/blob/39a310db1a21c83f71455565d05f485933f648bd/release_data/derived/static_refs.csv.gz), [trace IDs](https://github.com/HKUST-KnowComp/AgentIdeaBench/blob/39a310db1a21c83f71455565d05f485933f648bd/release_data/derived/active_traces.csv.gz)

### Sources and attribution

Primary sources are the [AgentIdeaBench paper](https://arxiv.org/abs/2609.07611v1), [pinned source repository](https://github.com/HKUST-KnowComp/AgentIdeaBench/tree/39a310db1a21c83f71455565d05f485933f648bd), and [data card](https://github.com/HKUST-KnowComp/AgentIdeaBench/blob/39a310db1a21c83f71455565d05f485933f648bd/DATA_CARD.md). Released data and selected derived aggregates are attributed to **The AgentIdeaBench Authors**, under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Reasonance reconstructs, selects and explains the numerical and identifier results. Paper identifiers retain the release's attribution to the **Semantic Scholar Academic Graph**, [ODC-BY 1.0](https://opendatacommons.org/licenses/by/1-0/). See the package's [notices](../artifact/NOTICES.md) for licensing boundaries; no rights to third-party abstracts, full text or model weights are supplied.
