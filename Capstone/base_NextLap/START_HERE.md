# Capstone NextLap — student data release v1

IIT414W, 30 October 2026. At the end of lap t, predict the same driver's next lap duration t+1 in seconds. Target: next_lap_s. RANDOM_SEED = 414. Real 2026 timing snapshots; no synthetic targets or target imputation.

## Files and fixed reference

- train_clean_v1.csv: 5,772 clean same-stint pairs, rounds 1–7.
- validation_clean_v1.csv: 1,808 clean same-stint pairs, rounds 8–9.
- observed_pairs_train_validation_v1.csv: broader observed consecutive pairs from those same races, including the retrospective clean_pair audit flag.
- data/: nine original lap snapshots and a SHA-256 source manifest, with no reserved-test race.
- nextlap_reference_v1.py: existing generic data and model functions, with no stored model results, private questions or interview guidance.

The reference numeric inputs are current_lap_s, recent_mean_s, current_lap_number and current_tyre_life. Categories are current_compound and current_team. recent_mean_s uses at most three current/past laps in the same driver, race and stint. Compare median and persistence references and suitable regression models using MAE in seconds. Extend information under common conditions, preserving race separation and fitting preprocessing only on training data.

Identifiers, event fields and the target are not automatically model inputs. clean_pair is retrospective: it uses next-lap conditions and cannot route a live prediction in advance. The main clean population is conditional; report broader-population limits explicitly. Future-known next_* columns must not become predictors. Weather was not loaded in the provided timing extraction, so any weather or traffic extension requires source, coverage and time-alignment checks.

Reserved final-evaluation data stay with the instructor and are not included. Do not tune on a final test. The split above is the approved 2026 NextLap case exception; it does not replace the historical split used by Rival Pit Window.

## Minimal reference run

Use Python with pandas, numpy and scikit-learn (the reference was verified with scikit-learn 1.8.0). No FastF1 download is needed to read these CSVs. SHAP is used in later project interpretation work.

```python
import pandas as pd
from sklearn.metrics import mean_absolute_error
from nextlap_reference_v1 import make_model, NUMERIC, CATEGORICAL, TARGET

train = pd.read_csv('train_clean_v1.csv')
validation = pd.read_csv('validation_clean_v1.csv')
features = NUMERIC + CATEGORICAL
model = make_model('OLS')
model.fit(train[features], train[TARGET])
predicted = model.predict(validation[features])
print('Validation MAE (s):', mean_absolute_error(validation[TARGET], predicted))
```

The helper also supports make_model('Ridge', alpha=...) and make_model('Lasso', alpha=...). Select settings from appropriate validation evidence. A smaller alpha alone is not evidence of a better model.

Today's team plan records a variable hypothesis, availability at t, controlled comparison and next action per member. See the Canvas launch page for the milestone roadmap. This data package does not contain a new grading rubric or change assessment weights. Record actual AI use and verification of adopted suggestions under the course policy.
