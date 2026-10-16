# Lab 1 · EDA and simple prediction rules

IIT414W · T3 2026 · Pairs · 6% of NP · Due Thursday 24 September 2026, 12:30, Santiago.

## Question and prediction moment

After qualifying and before the Grand Prix, can we anticipate whether a driver will be classified in the final top ten? Use one driver in one race as the observation. For this lab, target = 1 when the source's numeric final race position is 1–10, and 0 otherwise. This is final classification, not necessarily completing the race, receiving points or winning a constructor contest.

The population is the set of driver/race records available in the supplied race-results snapshots. Keep retirements, non-finishers and entries with missing qualifying records. This retrospective population is not a complete pre-race entry list. Discuss that limitation. Use qualifying position from the qualifying table, not grid from the results table. Sprint results are not part of the task; qualifying position and Grand Prix starting grid need not coincide. Current historical records can include later corrections, so this is not a reconstruction of everything known at an exact historical timestamp.

## Required work

1. Audit the qualifying/results join: row counts, keys, duplicates, missingness, unmatched records and coverage by season. Start from results and use a left join on season, round and driver_id. Explain why an inner join could change the evaluated population. The supplied helper performs the join; your task is to verify and interpret it.
2. Develop three distinct EDA questions using training data only. For each, provide a table or graph, an answer supported by observed values and a consequence for using or trusting the prediction. Include at least one explicit check for a trap from Friday: selection, misleading accumulation/correlation or graphical framing. More plots are not required.
3. Compare the two fixed baselines below. Explain their assumptions and why a trivial reference is useful. No model training or tuning is required.
4. Follow the temporal procedure below and interpret confusion matrices, accuracy and balanced accuracy on calibration and final test. Explain false positives and false negatives in this task. Report the evaluation population and missing-qualifying coverage.
5. Conclude which rule the evidence supports, where it fails and what you would investigate next. A disappointing result can receive full credit when the procedure and interpretation are correct. No minimum predictive score is required.

## Fixed baselines

| Baseline | Rule |
|---|---|
| Training majority | Predict the most frequent target in 2019–2021 for every row. An exact tie predicts 0. Never recompute the majority on calibration or test. |
| Qualifying top ten | Predict 1 when qualifying_position ≤ 10; otherwise 0. If qualifying position is missing, use the training majority and report how many rows used that fallback. |

The threshold of ten and the missing-value fallback are fixed for comparability. Explain the missingness and limitations; do not drop these rows or replace the fallback using outcomes. Position, points, status and laps from race results are post-race information: they can support training-data audit/EDA, but cannot be predictors. The label is only available after the race.

## Temporal procedure

| Role | Years provided | Permitted use |
|---|---|---|
| Train/development | 2019–2021, within the course's train ≤ 2021 rule | Audit, EDA and compute the majority. |
| Calibration/check | 2022 | Check implementation, describe errors and document corrections before freezing. This lab does not perform probability calibration. |
| Final test | 2023–2024 | Evaluate the frozen procedure. No new threshold, feature, filtering or fallback decisions based on test outcomes. |

All drivers in a race stay together. Do not shuffle rows or use a random split. Before opening test, record the two rules, target, join, missing-value policy, prediction moment, code version and any changes after the 2022 check. Commit that record with your code. The notebook has an explicit test switch; it is a learning aid, not a secure access barrier.

A restart/run-all may reproduce an already frozen test evaluation. If a genuine code error is discovered after opening test, document the original result, error, correction and new result; acknowledge that the test was already inspected. Do not hide this history or silently tune to improve the score.

## Submission

Submit your GitHub repository URL and the final commit identifier through Canvas. Include both members' names and a clear entry point. The repository must contain the executed notebook, the supplied local data and manifest, the support module, a dependency file, a short runbook and PROMPTS/contribution notes. Use relative paths. An additional report, video or oral defence is not required by this lab.

The notebook holds the audit, three analyses, metrics and conclusions. The runbook records the actual environment and restart/run-all steps. PROMPTS records AI use or explicitly states no use, one concrete decision and its verification, and each member's contribution. Cross-reference notebook evidence rather than duplicating it. AI assistance is permitted and must be documented; neither paid tools nor a prompt quota are required.

The marking criteria are technical correctness 40%, temporal validation 30%, reproducibility 20%, and AI-use documentation 10%; see the accompanying rubric. API access, extra models, telemetry and hyperparameter search are outside the required scope. The supplied real-data snapshots are sufficient. Synthetic mode is practice only and must not be submitted as real-data evidence.

## Start on Friday

Open the starter, load train and verify its row counts. Agree on your three questions and divide the work. Read the calibration/test instructions before beginning. There are no classes during 14–20 September; the lab is due at the beginning of the 24 September session, before its detailed validation lesson.
