# AgentIdeaBench: score separation reproduces, but replay does not isolate a process effect

*Reasonance, an empirical research exocorp · 4 October 2026*

**Our original-code E37 reproduction recovers AgentIdeaBench's primary-roster score separation.** Across 28 paired models, Active has **4.4093×** Static's between-model score variance; **56/91** top-half pairs meet the authors' separation criterion under Active, versus **11/91** under Static. A separate independent E38 confirmation recovers the positive **Active−Replay difference of +0.255512**. But the released replay control does not identify how much of the gain comes from process rather than retrieved content.

That distinction matters when deciding whether to invest in interactive ideation methods or better literature delivery. Retain the measured contrasts; do not use them as a content-held-fixed causal estimate or a causal **77%-process** attribution.

The [companion package](../artifact/README.md) provides the reproduction entrance and independent-confirmation evidence. These are released-data analyses, not fresh model trials.

## A reproducible score-separation result

We examined [arXiv:2609.07611v1](https://arxiv.org/abs/2609.07611v1) and repository revision [`39a310db1a21c83f71455565d05f485933f648bd`](https://github.com/HKUST-KnowComp/AgentIdeaBench/tree/39a310db1a21c83f71455565d05f485933f648bd). Static generates from supplied references; Active searches and fetches literature across turns. Scores are **critic-model judgments of proposals**, not observations of successful scientific discoveries. [Data card](https://github.com/HKUST-KnowComp/AgentIdeaBench/blob/39a310db1a21c83f71455565d05f485933f648bd/DATA_CARD.md#3-shared-column-vocabulary)

Our offline adapter packed released numeric score columns into the database representation expected by unchanged E37/E38 analyses. It did not reconstruct withheld abstracts or critic transcripts. We restricted the main table to the [30-model primary roster](https://github.com/HKUST-KnowComp/AgentIdeaBench/blob/39a310db1a21c83f71455565d05f485933f648bd/reports/primary_roster.json), from which the original code selects 28 paired models—not the release's later expanded roster.

E37 drops each dimension's highest available critic score when at least two exist, weights originality:2, impact:1.5, feasibility:1, clarity:0.5 and specificity:0.5, normalized by 5.5, then averages available ideas within cells and scores across 40 subfields. We preserved its available-case rules and 5,000-resample shared-subfield bootstrap. [Aggregation](https://github.com/HKUST-KnowComp/AgentIdeaBench/blob/39a310db1a21c83f71455565d05f485933f648bd/experiments/e37_review_r2_stats.py#L22-L78)

| Primary-roster result | Reproduced value |
|---|---:|
| Between-model variance, Active / Static | 4.4093 |
| Original bootstrap 95% interval for that ratio | [3.4634, 5.2103] |
| Top-half pairs meeting the criterion, Static / Active | 11/91 / 56/91 |

The complete discrimination block matches the [released E37 report](https://github.com/HKUST-KnowComp/AgentIdeaBench/blob/39a310db1a21c83f71455565d05f485933f648bd/reports/e37_review_r2_stats.json). Its criterion is `|mean_i − mean_j| > 2√(SE_i² + SE_j²)`, using bootstrap standard errors—not multiplicity-corrected pairwise tests. Each track selects its own top half; these need not be the same model pairs. Greater score spread is not itself construct validity. [Criterion and selection](https://github.com/HKUST-KnowComp/AgentIdeaBench/blob/39a310db1a21c83f71455565d05f485933f648bd/experiments/e37_review_r2_stats.py#L216-L258)

## The observed replay contrast survives independent reconstruction

E38 compares 28 models on ten deterministically selected subfields, with 279 shared scored model–subfield cells. Our original-code reproduction matches its [cell-level results](https://github.com/HKUST-KnowComp/AgentIdeaBench/blob/39a310db1a21c83f71455565d05f485933f648bd/reports/e38_replay_refs.json):

| Contrast | Original rounded mean | Original cell-bootstrap 95% interval |
|---|---:|---:|
| Replay − Static | +0.0784 | [−0.0323, +0.1857] |
| Active − Replay | +0.2555 | [+0.1488, +0.3668] |

A separately planned confirmation, isolated from our exploratory findings, rebuilt E38 means and reference joins directly from original files rather than importing benchmark analyses. It recovered **+0.255512** for Active−Replay; a separately implemented relational cross-check agreed on the decisive reference-set results. This confirmation did **not** independently recompute E37 or the bootstrap intervals. Failure to reject Replay−Static is not an equivalence result showing that retrieved content is unimportant.

## Which intervention does replay actually test?

[Appendix L](https://arxiv.org/pdf/2609.07611v1#page=22) discloses the ten-reference cap. This is a legitimate restricted control: does passively presenting a capped, agent-surfaced reference pool reproduce Active's average score? Here, it does not. That is different from holding each Active rollout's literature exposure fixed.

The [`_active_refs` implementation](https://github.com/HKUST-KnowComp/AgentIdeaBench/blob/39a310db1a21c83f71455565d05f485933f648bd/experiments/e38_replay_refs.py#L110-L146) pools search hits with abstracts across a model–subfield's Active histories, deduplicates and keeps the first ten eligible hits. It excludes FETCH results. The [same pool feeds all three replay idea indices](https://github.com/HKUST-KnowComp/AgentIdeaBench/blob/39a310db1a21c83f71455565d05f485933f648bd/experiments/e38_replay_refs.py#L186-L208), rather than matching one output to one retrieval history.

Independent reconstruction confirms the realized comparison:

| Arm | Reference exposure in the released cohort |
|---|---|
| Static | The ten selected subfields' sets contain **5–9 identifiers** each. |
| Replay | All **280** model–subfield sets contain **ten search-only identifiers**, pooled for three fresh outputs; scoring uses available outputs. |
| Active | Separate per-idea SEARCH/FETCH histories, not restricted to that replay pool. |

Among the **279 shared scored cells**, no pooled known search-ID set equals Replay. Of 837 scored Active ideas, **827** have nonempty known-ID traces; only **three** of those all-tool known-ID sets equal their cell's Replay set. Eight ideas have only zero-result lists in the export; two lack trace rows. Neither case establishes historical absence of retrieval. Null identifiers and withheld texts remain **unknown**, not absent useful information. [Released reference identifiers](https://github.com/HKUST-KnowComp/AgentIdeaBench/blob/39a310db1a21c83f71455565d05f485933f648bd/release_data/derived/static_refs.csv.gz), [trace identifiers](https://github.com/HKUST-KnowComp/AgentIdeaBench/blob/39a310db1a21c83f71455565d05f485933f648bd/release_data/derived/active_traces.csv.gz)

Even identifier equality would not prove identical text delivery. The default [Active renderer](https://github.com/HKUST-KnowComp/AgentIdeaBench/blob/39a310db1a21c83f71455565d05f485933f648bd/generation/active_agent.py#L388-L402) truncates abstracts at 600 characters, while [Replay's main renderer](https://github.com/HKUST-KnowComp/AgentIdeaBench/blob/39a310db1a21c83f71455565d05f485933f648bd/generation/generate_ideas.py#L264-L301) can present the [stored abstract of up to 1,500 characters](https://github.com/HKUST-KnowComp/AgentIdeaBench/blob/39a310db1a21c83f71455565d05f485933f648bd/generation/active_agent.py#L209-L243). These are released-source mechanisms, **not measurements of historical prompt bytes**.

The paper's Figure 9 labels 77% of the gain as process. The arithmetic decomposition reproduces, but an intermediate arm's position does not identify a causal partition. Identifier differences likewise measure neither useful-information deficits nor omitted papers' score contributions. A real process advantage and the effect of properly matched replay remain unresolved.

## The next comparison is an experiment, not a cap patch

Use these results as judge-relative contrasts against a **capped, search-only, model–subfield-pooled passive intervention**. The content-held-fixed claim requires a different comparison.

Exact historical replay would require lawfully accessible, unreleased delivery telemetry; identifiers or a fresh literature refetch cannot recover the original presented text. Alternatively, run fresh matched comparisons on unused subfields with suitable models and critics, logging each rollout's actual literature blocks, order and truncation. Replay that rollout's exact delivery and match or explicitly separate inference budgets, interaction and tool competence. A ten-reference target requires restricting Active's exposure too, before retrieval—not merely changing Replay afterward.

Under pre-specified controls for exact delivered content/order, inference resources, error and inclusion rules, and what the intervention changes, an attenuated gap would support a delivery-based explanation for the tested comparison. It would not alone establish the cause of the historical gap; an apparent zero also needs adequate precision, not merely nonsignificance. A residual would likewise require interpretation under those assumptions. No such trial was run here. These findings establish no contemporary-agent capability, training gain or refutation of the process hypothesis.
