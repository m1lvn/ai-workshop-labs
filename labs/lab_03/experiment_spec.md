# Expectation for one additional candidate

The five base results are supplied. This expectation concerns YOUR additional run.

- Base model: `forest_sqrt` (random forest, 150 trees, `max_depth=6`, `min_samples_leaf=30`, `max_features='sqrt'`, `class_weight='balanced_subsample'`). It is the best base system on development: 140/370 eligible entries caught with 945 alerts, precision 340/945 = 0.360, threshold 0.608.
- Parameter and old → new value (one allowed tuple): `forest_sqrt / min_samples_leaf / 100` (old value 30).
- Conditions held fixed:
  - The same CSV (hash checked by `load_learning`), seed 414 and the nine `FEATURES`.
  - Train 2018–2021 and development = first 11 rounds of 2022.
  - The same preprocessing pipeline, fitted on train only.
  - All other forest settings: `n_estimators=150`, `max_depth=6`, `max_features='sqrt'`, `class_weight='balanced_subsample'`, `random_state=414`. `run_one_change` clones the parent and asserts that only `model__min_samples_leaf` changes.
  - The same alert policy: a threshold reselected on dev only, at most 10% of dev windows (≤ 945 alerts), maximising distinct entries caught, then reused unchanged on train.
- Have you already run this additional candidate? **No.** This expectation was written (drafted with Claude Code, reviewed and accepted by us) before the first run of this candidate. We only re-ran the five base systems to check that they reproduce the supplied table.
- Expected effect and mechanism, written before the first additional run:
  - **Mechanism.** Raising the minimum leaf size from 30 to 100 training windows means each leaf's score averages at least 100 historical windows. Leaves that described small, very specific situations (for example a circuit/compound/tyre-age corner) can no longer be created. Scores should become smoother and less specific to 2018–2021.
  - **Expected observations.**
    1. A smaller train/dev gap in event recall than the parent's 0.520 → 0.378, mainly because train scores become less in-sample-optimistic.
    2. Development event recall roughly similar to the parent, about 140 ± 10 of 370 entries, with alerts still close to the 945 limit. We do **not** expect a clear improvement: with 63,165 training windows and `max_depth=6`, many leaves are probably already larger than 100. A loss of some specific high-score leaves could also cost a few entries.
    3. The selected dev threshold may move, because smoother scores create more ties near the cutoff. Part of any change could therefore come from the threshold reselection rather than the model alone.
- Other trials already made, if any, and how the final candidate was chosen: **None.** Before any additional run, we chose this tuple because it changes the best base system (so the recommendation concerns the model that would actually be used) and directly targets the observed train/dev gap. We did not run the other two allowed tuples.

Keep this record after running, even if wrong. Explain actual results in “4. Explain your additional result”.
Do not rewrite an expectation as if it predicted a result already seen.
