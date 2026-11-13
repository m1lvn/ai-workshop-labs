# Capstone NextLap · Hito 1

Problem framing, decision value and experiment plan
IIT414W · Brief for 6 November 2026 · v2

Due Thursday 12 November 2026, 23:59, Santiago time. Weight: 5% of NP. Work with your existing capstone team. The Hito 1 rubric totals 100 points. The pass requirement is 60%: 60 points correspond to grade 4.0. For a rubric score p between 0 and 100:

- If p <= 60: grade = 1 + 3 × p / 60.
- If p > 60: grade = 4 + 3 × (p - 60) / 40.

Reference values: 0 points = 1.0; 50 = 3.5; 60 = 4.0; 80 = 5.5; 100 = 7.0. Keep full precision until applying the course's established final rounding rule. Authorised individual arrangements continue to apply. The competitive +0.2 bonus applies only to the final capstone report, not to Hito 1.

## The task

At the end of a driver's lap t, predict the same driver's next lap duration t+1 in seconds. The target is `next_lap_s`. Explain who could use this estimate, what decision it could inform and what it cannot establish. Predicting lap time alone does not establish when a car should pit or how many positions a strategy will gain.

Your Hito 1 must show a reproduced reference and a feasible plan for investigating additional information or a justified new representation. You do not need to have improved MAE yet. A sound experiment that later finds no improvement can earn full academic credit. The separate competitive bonus does not change this rubric.

## Common data and comparison

Use the released `IIT414W_Capstone_NextLap_StudentData_v1.zip`. `START_HERE.md` describes the files. Training contains 5,772 clean pairs from rounds 1–7 of 2026; validation contains 1,808 clean pairs from rounds 8–9. Keep `RANDOM_SEED = 414`. Reserved final-evaluation data are not for choosing features, parameters or models. Disclose any previous access.

Reference inputs: `current_lap_s`, `recent_mean_s`, `current_lap_number`, `current_tyre_life`, `current_compound`, `current_team`. Reproduce training-median, persistence and the supplied OLS reference on the same validation rows. Fit preprocessing only on training data. Report MAE in seconds and row counts; preserve `pair_id` so comparisons are traceable.

`clean_pair` defines a retrospective, conditional population using some t+1 information. It is not a predictor or a rule that identifies future clean laps in advance. Future-known `next_*` columns must not enter the model. Build history from the original timeline, within driver/race/stint, before retrospective filtering; otherwise future-based filtering can change which past rows remain available.

## Choose a manageable direction

| Direction | Possible investigation | Check before committing |
| --- | --- | --- |
| Recent pace history | Variability or trend beyond the supplied recent mean. | Only observations through t; correct driver/race/stint boundaries; rule for short histories. |
| Tyre/context representation | A justified transformation or interaction of tyre life and compound. | Explain what differs from the reference and compare with/without it using the same model and rows. |
| Traffic | An observable proximity measure at the prediction moment. | Verify source, timestamp and coverage. Do not use a later gap, final race position or future outcome. |
| Weather | An observed weather measurement available by the end of t. | Weather is not included in the timing release. Verify access and alignment; do not use a future race average. Have a fallback using released data. |

One clear primary hypothesis is enough. The directions have equal academic standing. A complicated external source is not required. Model comparisons may complement your feature investigation; switching algorithms alone does not test the contribution of added information. Report broader-population analyses separately from the fixed common comparison.

## Submit one coherent package

Prepare `Hito1_<team>.zip` with a short README linking these parts. Include the repository URL and exact commit in the submission text. Use the Hito 1 assignment in the course Canvas when its link is announced. If that destination is not yet enabled, save the exact final commit and attach Hito1_<team>.zip to a GitHub release named Hito1 in your existing team repository by the same deadline; retain the timestamp and commit as submission evidence. The later Canvas copy must identify that unchanged version and does not require a new analysis. The repository release is the announced fallback, not an extension of the deadline. Do not create a new repository to hide the history.

1. `HITO1.md` or a PDF: a concise framing and experiment plan using the sections below. Tables and short sentences are sufficient.
2. An executable notebook or script reproducing the three references; environment and run instructions; generated metric table with units, populations and counts. The class helper can be reused with attribution and your own interpretation. Include a data location or manifest; there is no need to duplicate the entire released dataset in every repository.
3. `DECISION_LOG.md`: actual decisions, evidence, changes after feedback and next steps. Record AI use or no use, adopted suggestions and how you checked them. Identify what each actual member did and can explain.

Suggested `HITO1.md` sections:

| Section | Evidence to include |
| --- | --- |
| Problem and decision value | Target, unit, prediction time, intended reader/decision and one limit of the clean-pair setting. |
| Reproduced reference | Data version, split, features, fit/transform separation, command, counts and MAE for median, persistence and OLS; explain one comparison. |
| Primary hypothesis | Proposed feature or representation, expected mechanism, source, availability at t and missing-data/short-history rule. If relying on an unverified external source, specify a feasible fallback. |
| Experiment plan | What stays fixed; reference vs extension; extension vs version without the added information; what would support or contradict the hypothesis; how validation is used and test protected. |
| Traceability and next steps | Actual contributions, AI record, one revision after feedback, responsibilities before Hito 2 and a known blocker if any. |

Write the planned checks before implementing the extension. An appropriate check might inspect the last timestamp used by a feature, ensure the validation `pair_id` set is unchanged, or compare both models on the same rows after applying a documented preprocessing rule. “The notebook runs” alone is not an improvement check.

For the experiment plan, identify the candidate and a modest, explicit search plan. Log all trials, including unsuccessful ones. A large unexplained search on validation is not stronger evidence. Include MAE by validation race with counts in your planned robustness checks. At Hito 1 this is a plan; the executed extension, ablation, contextual errors and SHAP belong to Hito 2.

## Hito 1 rubric

Award demonstrated component points. Complete evidence earns the component maximum; incomplete but valid evidence earns partial credit; absent, contradicted or invalid evidence earns no credit for that component. Explain deductions. A negative result is not a deduction by itself.

| Criterion | Points and components | Complete evidence | Partial / insufficient evidence |
| --- | --- | --- | --- |
| Problem and decision value | 20: target/unit/time 8; intended use 8; conditional-population limit 4. | Defines who predicts what and when, connects it to an informed decision, and limits the claim. | Generic benefit, unclear timing, or treating clean-pair performance as all-race/live evidence leaves the corresponding component incomplete. |
| Reproduced reference | 25: actual reproducible run 15; three-model metric comparison 5; counts and common evaluation rows 5. | Submitted code reproduces median, persistence and OLS with training-only preprocessing; results, units and row identities agree. | A supplied output clearly labelled as such is useful preparation but does not by itself prove the team's reproduction. Incorrect or incomparable numbers do not earn their evidence points. |
| Feature hypothesis and feasibility | 20: defined change and rationale 8; source and availability check 8; missing-data/short-history rule and feasible fallback where needed 4. | A specific implementable hypothesis with an inspectable time rule and handling of unavailable data. | “Add weather” without a source/time check is incomplete. A future-known input is not an admissible feature. |
| Experiment and verification plan | 25: fixed controls 8; contribution/ablation comparison 6; selection vs final evaluation 6; prior support/refutation checks 5. | Holds target, rows, split, preprocessing protocol and metric fixed; isolates the change and states what would count against it. | Uncontrolled model-and-feature changes, no ablation, test tuning, or “lower MAE is better” without a comparable protocol leaves components unmet. |
| Reproducibility and responsibility | 10: portable files/run instructions 4; truthful AI/no-use and checks 3; actual member decisions and contributions 3. | Another reader can locate and run the evidence, and every member can explain a documented decision. | File names alone, generic AI verification or copied numbers without traceable outputs are insufficient. Honest no-use can earn all AI-record points. |

Do not double-penalise the same omission under several labels unless it causes distinct demonstrated failures. The execution itself is assessed in criterion 2; portable delivery is assessed in criterion 5. Do not infer authorship or AI use from writing style. The bonus is not a substitute for completing Hito 1.

## What follows

| Milestone | Due date | NP weight | Main evidence |
| --- | --- | ---: | --- |
| Hito 1 | Thu 12 Nov, 23:59 | 5% | Framing, reproduced reference, hypothesis, experiment plan. |
| Hito 2 | Thu 19 Nov, 23:59 | 5% | Executed comparison, contribution of added information, contextual errors and SHAP. |
| Demo | Fri 20 Nov, in class | 5% | Defence of decisions, results and limits. |
| Final report + repository | Sun 22 Nov, 23:59 | 10% | Reproducible evidence and revision after feedback. |

On 12 and 13 November, Ángel will support technical work, final Hito 1 questions and progress toward Hito 2. Bring the actual error, output or plan you need help with. No advanced regression-calibration procedure, new classification target or operational pit-stop simulator is added to Hito 1.
