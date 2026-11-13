# NextLap · justified MAE improvement bonus

Rules prepared for announcement on 6 November 2026 · v2

The winning eligible team receives +0.2 on its final capstone report grade, capped at 7.0. This does not alter assessment weights, Hito 1/Hito 2 grades, exam grades or ICA. It is separate from any exit-ticket policy. The final report retains its 10% NP weight.

## Common comparison

The reference is the supplied OLS pipeline with the six released inputs, fitted on the released rounds 1–7. All teams use the same target (`next_lap_s`), MAE in seconds and evaluation rows. Median and persistence remain useful checks; teams cannot choose a weaker private baseline to inflate their improvement.

Validation rounds 8–9 can guide selection and must be reported honestly as selection evidence. Ranking uses a common final-evaluation population held by the instructor, after candidates are frozen. This population must not have been used by teams to select features, settings or models. A validation leaderboard alone does not determine the winner.

The instructor will document the final-evaluation protocol, data provenance and prior-access check before scoring. The known oral-case reserve is not automatically considered untouched for this competition. Any prior access must be disclosed. If an independent common evaluation cannot be established, award adjudication waits for a common valid evaluation; it does not silently switch to training or validation performance.

## Input contract for the common evaluation

This contract is fixed before teams complete their extensions. The instructor will prepare prediction requests containing pair_id, season, round, driver_number, stint, end_time_s and the six reference inputs. Each request represents the end of lap t; it does not contain next_lap_s, next_* fields or future outcome labels. The instructor retains the target and computes MAE.

For history-based features, the evaluation must provide a chronological history view containing only laps already ended by that request time, with driver/race/stint keys and the timing-snapshot schema used in the released package (lap number/time, end time, tyre life, compound, team and already-observed status fields). A complete future race table is not an admissible predictor input. Grouping by driver/race/stint does not by itself remove future observations; the as-of time limit still applies.

Tyre/context representations can use the current fields above. Traffic and weather extensions must declare their extra source and timing conversion, source coverage, the last available observation used and an executable fallback. External-source retrieval must be reproducible from recorded snapshots/provenance rather than an unrecorded live request during scoring. A feature requiring information unavailable at t must be rejected, not silently imputed as if it were observable.

The candidate must return one finite prediction in seconds per requested pair_id, with no missing or duplicated IDs. Use one shared evaluation row set. A frozen training-derived missing-data rule or declared OLS fallback can preserve coverage; report fallback counts. Expanded-population studies remain separate.

Before final scoring the instructor will audit prior access, record the common dataset version and confirm that this input contract can be supplied to every candidate. If a source cannot be made available fairly, use the announced fallback and retain all rows. No feature-dependent schema restriction may be introduced after the candidate freeze. Any necessary protocol correction must be communicated equally before that freeze; it cannot be designed after inspecting candidate test scores.

## Candidate and freeze

Submit one nominated candidate with the final report and repository by Sunday 22 November, 23:59, Santiago time. Use the same existing final-report deadline, not an additional earlier submission. Identify the commit, environment, exact run command, feature-generation procedure, trial log and any required source snapshots. Changes made after the demo may be included before this freeze and must be logged.

For this comparison, both OLS and the nominated candidate train only on rounds 1–7. Validation selects settings; it is not added to training for the prize run. Fit imputation, scaling and learned transformations on train only. Use seed 414 wherever a random state applies and record other nondeterminism.

The instructor runs each frozen candidate once against the same eligible final rows. No interim test scores are returned for tuning. Predictions must be finite and cover every evaluated `pair_id`. If a feature is unavailable, a documented training-derived imputation or frozen reference fallback may be used; its predictions count in the MAE and fallback counts are reported. Do not drop difficult or missing-feature rows to improve a score. An unresolved non-executable submission cannot establish eligibility; any technical repair must leave the nominated model and selection decisions unchanged and be documented under an equal rule for all teams.

## Eligibility before ranking

An eligible team must provide:

1. A reproducible reference, candidate and comparison, with a positive overall validation improvement over the fixed OLS reference on identical rows.
2. Evidence that each added feature is available at t, with no target/future leakage and no test-based selection. Keep the clean-pair population fixed; report expanded-population studies separately.
3. A controlled comparison with and without the added information or representation. If the model family also changes, include the same candidate model without the added information so its contribution is not confused with the model change. A failed feature hypothesis must be reported honestly; a model gain must not be attributed to that feature.
4. A log of tried configurations, MAE by validation race with counts, and a bounded explanation of improvements and failures. These are checks against overfitting, not a mathematical proof that overfitting is impossible. A train–validation gap alone is neither automatic exclusion nor proof of validity.
5. Explanations of decisions by the actual team members, supported by the capstone evidence and existing demo. No additional surprise oral examination is created. Existing authorised absence arrangements remain applicable.

The final held-out MAE must also improve on the fixed reference. A valid negative result can still earn an excellent project grade but does not win this improvement bonus. A winning score does not establish causal effects or generalisation to every future race.

## Ranking and ties

For the common final rows:

`gain_s = MAE_OLS_reference − MAE_candidate`

The eligible team with the largest positive `gain_s` wins. Because the reference and rows are shared, this is equivalent to the smallest candidate MAE. The percentage reduction can be reported as `100 × gain_s / MAE_OLS_reference`, but ranking uses unrounded MAE in seconds.

Eligible candidates no more than 0.001 seconds above the best candidate MAE share the award. This is an announced administrative tie tolerance, not a statistical significance threshold. Every tied eligible team receives the same +0.2, capped at 7.0. If no eligible candidate beats the reference, no improvement bonus is awarded; ordinary assessment still follows the published rubric.

The award is determined after the final-report freeze and verification, not during the 20 November demo. Publish the reference MAE, candidate MAE, common n, gain, eligibility decision and any tie explanation. Apply the bonus to each eligible member's final-report grade after ordinary marking: `min(7.0, report_grade + 0.2)`. Do not reinterpret it as +0.2 in NP or as compensation in an individual control.
