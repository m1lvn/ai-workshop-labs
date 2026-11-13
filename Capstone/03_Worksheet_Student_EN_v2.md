# NextLap kickoff · working sheet

Friday 6 November 2026 · 11:10–13:40 · v2
Team: __________   Actual members: ____________________

Today's work is formative. Save one TEAM_PLAN.md per team by 13:28; the instructor can inspect it on screen or collect it on paper. Hand in your own exit response at 13:40. It prepares Hito 1 (12 November, 23:59; 5% NP). Use your existing team. A person working alone follows the same core and asks a neighbouring team for review.

## Re-entry card

Predict the same driver's next lap duration in seconds at the end of the current lap. Train: 2026 rounds 1–7; validation: rounds 8–9. Use the released local data. The six supplied inputs describe current/recent pace, lap number, tyre life, compound and team. Final evaluation stays separate. Your job is to investigate additional information or representation and explain what the evidence supports.

Success today: a precise problem; one feasible hypothesis; a comparison with fixed controls; a check written before building; a revision after feedback. AI can support code, ideas or debugging under the course policy. Record suggestions actually used and their checks. Write the individual reasoning first and explain it yourself.

## 1. Individual opening · 11:10–11:20

Fictional example: a reference has MAE 0.40 s on 1,000 rows. A candidate has MAE 0.25 s on only 600 rows after dropping missing weather values. Does this establish an improvement? Think silently for one minute before talking.

My answer and reason: __________________________________________

A comparison I would need: _____________________________________

## 2. Predict, then observe · 11:20–11:38

Which reference do you expect to perform best: one training median for every lap, persistence of the current lap, or OLS with the supplied inputs? Why?

Prediction before seeing results: ______________________________

Observed MAE and evaluated population: _________________________

What changed in my explanation: _________________________________

What the result does not establish: ____________________________

During the modelling example, keep the same five headings for a complete experiment card: hypothesis / availability / control / prior check / limit. The instructor will reveal a worked design about current_tyre_life after asking which comparison would isolate its contribution. No feature-improvement result is assumed. Its reduced model is a teaching comparison, not a replacement for the official prize reference.

You may record team tables directly in TEAM_PLAN.md and refer to them here. Do not copy the same table twice. Opening, individual prior checks and exit answers must still identify each student's own reasoning.

## 3. Complete the experiment · 11:38–11:50

Proposed hypothesis: recent pace variability may contain information not captured by the recent mean. A teammate proposes using three observed lap times through t. Another proposes using `next_lap_s` because it is strongly associated with the target.

| Missing step | Your completion |
| --- | --- |
| Hypothesis: what contribution will you test? | |
| Availability: admissible proposal, time, grouping boundaries and short-history rule | |
| Control: what stays fixed, and what will you remove in the comparison? | |
| Prior check: evidence and failure condition before building | |
| Limit: what conclusion would remain unsupported? | |

Each member writes before building or changing code:

Member ______: “I will check ______ using ______. A failure would look like ______.”

Member ______: “I will check ______ using ______. A failure would look like ______.”

## 4. Investigate the base before changing it · 11:50–12:10

Locate `TARGET`, `NUMERIC`, `CATEGORICAL`, `make_model` and `.fit` in the supplied files. Explain which rows teach the imputer and scaler. Check train/validation rounds and `pair_id` uniqueness. Write what you expect before executing `python probar_referencia_v1.py` from this package, or run the minimal example in `base_NextLap/START_HERE.md` from the base folder.

At 12:00 have counts plus a reference metric and its population ready; show your status: own run / supplied fallback / blocked. The instructor visits from 12:00 to 12:06. If blocked, write the first error, switch to the labelled instructor reference and continue planning. Do not wait for debugging to start the plan or claim supplied evidence as your own run.

| Check | Expected | Observed / file | Own run or supplied evidence? |
| --- | --- | --- | --- |
| Training / validation rows | | | |
| Rounds and disjoint pair IDs | | | |
| Preprocessing fit population | | | |
| Reference MAE and units | | | |

Break 12:10–12:20. Return at 12:20.

## 5. Diagnose and revise · 12:20–12:43

Anonymous difficulty discussed: __________________________________

Likely cause and evidence needed: _______________________________

My correction: __________________________________________________

Complete an experiment table. “Same” must name a specific control, not mean “roughly similar”. No extension result is required yet.

| Experiment | Information / representation | Model | Rows and split | Check / metric | What does it isolate? |
| --- | --- | --- | --- | --- | --- |
| Fixed reference | | | | | |
| One proposed change | | | | | |
| Remove the added information | | | | | |

From 12:28 to 12:34 the instructor checks a short piece of evidence, prioritising blocked teams and changing the spokesperson. Use feedback from 12:34 to 12:38. From 12:38 to 12:43, confirm the Hito 1 delivery instructions and the bonus rule. Keep the written rubric available.

## 6. Team challenge · 12:43–13:28

Choose one primary direction: pace history, tyre/context representation, traffic or weather. Start from the common data and Hito 1 brief. All directions use the same target and assessment criteria. An external source is optional. Before building, update each member's prior check for the hypothesis your team actually chose: what to inspect, expected evidence and a failure condition. The shared-example check is enough only if it applies to this hypothesis. Keep the original plan entry; revise your conclusion after checking rather than rewriting the prior prediction. The instructor's short monitoring round is 12:55–13:01.

| Work step | Minimum record |
| --- | --- |
| Clarify | Target/time, intended decision and scope limit. |
| Plan | Hypothesis, source, availability, 2–3 actions and prior check. |
| Build | One completed plan entry or small verifiable implementation; do not run an uncontrolled search. |
| Verify | Compare evidence against your declared check; retain negative results. |
| Review | One concrete change after the peer review, or a reason to reject the suggestion. |
| Explain | A supported conclusion, a remaining limit and the next action of each member. |

Peer review, 13:08–13:16: exchange with the next team in the room; the last team reviews the first. Check (1) availability at t, (2) same evaluation rows, (3) isolation of the change, (4) a test written before implementation. Give feedback in this form: “I see ___; the criterion is ___; before 13:23 you can ___.”

Give one priority correction. Keep the earlier and revised plan entry, or explain why you retained it.

Feedback received: ______________________________________________

Change made, or reason not to change: ____________________________

Member 1 decision and evidence: _________________________________

Member 2 decision and evidence: _________________________________

Optional extension, without extra marks: propose one context where the global MAE could hide an error and explain how you would count and compare it. The extension is not required for Hito 1 and does not by itself qualify for the competitive bonus.

Save your revised `TEAM_PLAN.md` by 13:28. Identify any blocker that Ángel should help you resolve next week.

## 7. Individual exit · 13:28–13:40

Name: ___________________   Team: __________

1. What decision can you now justify, and what observed result or check supports it?

________________________________________________________________

2. What did you change after feedback, and why?

________________________________________________________________

3. What limitation remains, and what will you check next?

________________________________________________________________

Explain one answer to your partner and listen to their explanation. Hand in your own response. This is formative evidence, not a new graded submission or an automatic attendance bonus.
