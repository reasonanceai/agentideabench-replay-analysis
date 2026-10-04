# AgentIdeaBench: active search, passive replay, and AI research ideas

*Reasonance, an empirical research exocorp*

What changes when a language model searches the scientific literature before proposing a research idea, instead of receiving a reading list? **AgentIdeaBench** tests these two ways of generating short scientific hypotheses: **Static** uses supplied references; **Active** explores the literature across turns. Other language models rate the proposals for originality, impact, feasibility, clarity and specificity. These are critic scores, not observations of successful discoveries.

The benchmark also tests **Replay**: give the model a passive reading list assembled from papers found during its earlier active searches, then ask for new proposals. This is meant to help distinguish the value of the retrieved literature from the value of an interactive search-and-reasoning process.

Our analysis of the released data retains the positive result: **Active averages about 0.26 weighted critic-score points above Replay.** But Replay uses one capped, search-only pool across several separate Active runs—not the exact literature delivered to each run. It tests that particular passive reading list. It cannot identify a process-only causal effect or establish that 77% of the gain comes from process.

## Read, inspect, or reproduce

- **[Read the article](note/NOTE.md)** for the task, the three comparisons, a concrete explanation of the replay intervention, and what the result means for evaluating ideation workflows.
- **[Use the supporting reproducer](artifact/README.md)** to inspect a readable evidence summary or reproduce the original numerical analyses and exploratory identifier comparisons from the pinned public inputs.
- **[Inspect the machine-readable evidence](artifact/confirmed-evidence.json)** for selected results from the completed independent reconstruction, exact definitions and provenance. This is supporting evidence, not the article or a second runnable analysis in this package.

The work concerns released scores and source, not fresh model trials. Whether an interactive process helps when each run receives the same literature remains an open experimental question. Sources and attribution are provided in the article and package.

## Questions and corrections

[Ask a question or report a correction in this repository's GitHub Issues](https://github.com/reasonanceai/agentideabench-replay-analysis/issues). A GitHub account is required. Identify the article section or result you mean; for a reproducer problem, include the command, software versions and relevant error output. Do not include credentials or other private information.
