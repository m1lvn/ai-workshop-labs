"""Run only the released NextLap reference. No held-out test is accessed."""
from pathlib import Path
import sys, json, hashlib
import numpy as np
import pandas as pd
import sklearn
from sklearn.metrics import mean_absolute_error

ROOT = Path(__file__).resolve().parent
BASE = ROOT / 'base_NextLap'
sys.path.insert(0, str(BASE))
from nextlap_reference_v1 import make_model, NUMERIC, CATEGORICAL, TARGET

train = pd.read_csv(BASE / 'train_clean_v1.csv')
val = pd.read_csv(BASE / 'validation_clean_v1.csv')
assert len(train) == 5772 and len(val) == 1808
assert set(train['round']) == set(range(1, 8)) and set(val['round']) == {8, 9}
assert train.pair_id.is_unique and val.pair_id.is_unique
assert not set(train.pair_id) & set(val.pair_id)
features = NUMERIC + CATEGORICAL
assert TARGET not in features and not any(c.startswith('next_') for c in features)
model = make_model('OLS').fit(train[features], train[TARGET])
preds = {
    'train_median': np.full(len(val), train[TARGET].median()),
    'persistence': val.current_lap_s.to_numpy(),
    'OLS_reference': model.predict(val[features]),
}
rows = []
for name, pred in preds.items():
    assert np.isfinite(pred).all()
    for label, mask in [('all_validation', np.ones(len(val), dtype=bool)),
                        ('round_8', val['round'].eq(8).to_numpy()),
                        ('round_9', val['round'].eq(9).to_numpy())]:
        rows.append({'model': name, 'population': label, 'n': int(mask.sum()),
                     'MAE_s': float(mean_absolute_error(val.loc[mask, TARGET], pred[mask]))})
out = ROOT / 'salidas_referencia'; out.mkdir(exist_ok=True)
pd.DataFrame(rows).to_csv(out / 'reference_metrics.csv', index=False)
pd.DataFrame({'pair_id': val.pair_id, 'round': val['round'], 'y_true': val[TARGET],
              **preds}).to_csv(out / 'validation_reference_predictions.csv', index=False)
report = {'train_rows': len(train), 'validation_rows': len(val), 'test_used': False,
          'seed': 414, 'features': features, 'results': rows,
          'versions': {'numpy': np.__version__, 'pandas': pd.__version__, 'sklearn': sklearn.__version__},
          'sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in
                     [BASE/'train_clean_v1.csv', BASE/'validation_clean_v1.csv', BASE/'nextlap_reference_v1.py']}}
(out / 'reference_run.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(pd.DataFrame(rows).to_string(index=False))
print('No test data used. These are reference results, not a feature-extension solution.')
