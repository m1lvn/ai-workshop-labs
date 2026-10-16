# Lab 1 · Assessment rubric

Pairs · 100 points · 6% of NP · Due 24 September 2026 at 12:30, Santiago.

Score each criterion independently at the highest anchor supported by the evidence. Anchors are Full = 100%, Solid = 80%, Basic = 60%, Limited = 30%, No assessable evidence = 0% of that criterion. Provide an evidence reference and a next step. Predictive performance, plot styling and code volume are not grading criteria.

## C1 · Technical correctness · 40 points

| Level | Points | Evidence |
|---|---:|---|
| Full | 40 | Correct target and population; verified join/keys/coverage/missingness; three distinct question–evidence–interpretation–decision analyses, including a trap check; both specified baselines and metrics are correct and conclusions reflect their limits. |
| Solid | 32 | All core components are present and technically sound. A minor explanation or audit detail is incomplete without changing the population, baseline comparison or main conclusion. |
| Basic | 24 | A coherent audit and comparison can be inspected, but one analysis is absent/weak or a substantive interpretation/check needs correction. The essential target and comparison remain identifiable. |
| Limited | 12 | Some own analysis is evidenced, but a wrong join/target/rule/metric or major omissions prevent a defensible comparison. Credit the correctly demonstrated parts. |
| No evidence | 0 | No assessable technical work beyond the uncompleted supplied scaffold. |

## C2 · Temporal validation · 30 points

| Level | Points | Evidence |
|---|---:|---|
| Full | 30 | Train 2019–2021, calibration 2022 and test 2023–2024 are correctly separated with whole races; majority and EDA use train only; predictors are available at the stated moment; decisions/code are frozen before test; calibration changes and test interpretation are traceable. |
| Solid | 24 | The temporal procedure is correct and no material leakage is evidenced; a minor freeze/evidence reference or limitation is incomplete. |
| Basic | 18 | Correct partitions and train-only majority are evidenced, but freeze chronology or the prediction-moment explanation is insufficiently supported. Test inspection/corrections are disclosed where relevant. |
| Limited | 9 | Some temporal reasoning exists, but random splitting, fitting on future labels, using post-race predictors or undisclosed test-based decisions invalidates the claimed evaluation. |
| No evidence | 0 | No assessable temporal procedure or account of data use is provided. |

## C3 · Reproducibility · 20 points

| Level | Points | Evidence |
|---|---:|---|
| Full | 20 | Submitted commit, notebook outputs, dependencies, local data/manifest and concise runbook support a coherent restart/run-all. Paths are portable; output provenance is truthful; both members' contributions are identified. Seed 414 is used if randomness is introduced. |
| Solid | 16 | Core execution is reproducible with all essential files; a minor environment or entry-point detail is missing without requiring substantive reconstruction. |
| Basic | 12 | Own execution is evidenced, but incomplete dependencies, run instructions or version references require clarification to repeat it. |
| Limited | 6 | Some files/results are inspectable, but missing runtime files, unsupported execution claims or unclear provenance prevent a repeatable run. |
| No evidence | 0 | No usable execution/package evidence is available. |

## C4 · AI-use documentation and verification · 10 points

| Level | Points | Evidence |
|---|---:|---|
| Full | 10 | Use/no use is explicit. If used, meaningful assistance, tool/purpose and acceptance or changes are described. A concrete own decision is linked to an actual verification result and limitation. The no-use route supplies the same decision/check evidence. |
| Solid | 8 | Disclosure, decision and observed check are traceable, with a minor omission in rationale, assistance detail or limitation. |
| Basic | 6 | Disclosure and a specific decision/check are present, but the result or reasoning is incomplete. |
| Limited | 3 | Disclosure exists but the account is generic, an unchanged template or an unexamined transcript. |
| No evidence | 0 | No assessable disclosure or decision/verification account. |

## Scoring practice

Assess the available evidence, not an inferred intention. Supplied code alone does not demonstrate a student's reasoning. A weak predictive score can earn full marks; live API access, extra plots/models and paid AI tools earn no additional points. Record leakage under C2; do not automatically duplicate the same deduction under C1 if its calculations are otherwise correct. Assess execution under C3 and substantive calculations under C1. Apply no undeclared global caps or automatic sanctions. An honest correction is evidence to review, not a reason for an invented penalty.

These are points out of 100. The course's applicable grade-conversion policy governs the recorded grade; this rubric introduces no new conversion formula.
