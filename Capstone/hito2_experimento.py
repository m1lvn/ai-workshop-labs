"""Hito 2 · NextLap · Grupo 3 — experimento de historial de ritmo, ablación, errores y SHAP.

Ejecutar desde Capstone/:  ../.venv/bin/python hito2_experimento.py
Escribe todo en salidas_hito2/. No usa ni accede al test reservado (ronda 17).
"""
from pathlib import Path
import sys, json, hashlib, subprocess
import numpy as np
import pandas as pd
import sklearn
import shap
from sklearn.metrics import mean_absolute_error

ROOT = Path(__file__).resolve().parent
BASE = ROOT / 'base_NextLap'
OUT = ROOT / 'salidas_hito2'
OUT.mkdir(exist_ok=True)
sys.path.insert(0, str(BASE))
from nextlap_reference_v1 import (make_model, load_snapshots, build_pairs, NUMERIC,
                                  CATEGORICAL, TARGET, KEYS)

RANDOM_SEED = 414
TRAIN_ROUNDS, VAL_ROUNDS = set(range(1, 8)), {8, 9}
MIN_SLOPE_LAPS = 3          # pendiente requiere >= 3 vueltas limpias en la ventana
MIN_STD_LAPS = 2            # desviación requiere >= 2
SHAP_BACKGROUND_N = 500     # muestra de train para el background de SHAP
rng = np.random.default_rng(RANDOM_SEED)
checks = {}

# ---------------------------------------------------------------- 1. Datos y split
train = pd.read_csv(BASE / 'train_clean_v1.csv', dtype={'driver_number': str})
val = pd.read_csv(BASE / 'validation_clean_v1.csv', dtype={'driver_number': str})
assert len(train) == 5772 and len(val) == 1808
assert set(train['round']) == TRAIN_ROUNDS and set(val['round']) == VAL_ROUNDS
assert train.pair_id.is_unique and val.pair_id.is_unique
assert not set(train.pair_id) & set(val.pair_id)
assert train.clean_pair.all() and val.clean_pair.all()
checks['split'] = {'train_rounds': sorted(int(r) for r in train['round'].unique()),
                   'validation_rounds': sorted(int(r) for r in val['round'].unique()),
                   'train_rows': len(train), 'validation_rows': len(val),
                   'validation_rows_by_round': {int(k): int(v) for k, v in val['round'].value_counts().sort_index().items()},
                   'test_used': False}

# ---------------------------------------------- 2. Features de historial (línea de tiempo original)
raw, manifest = load_snapshots(BASE)          # verifica SHA-256 del manifiesto
assert set(raw['round']) == TRAIN_ROUNDS | VAL_ROUNDS, 'Solo rondas 1-9 en los datos publicados'


def history_features(raw, k):
    """std y pendiente de las últimas k vueltas (incluye t) por piloto/carrera/stint.

    Usa la misma regla que build_pairs para recent_mean_s: solo vueltas ya observadas y
    'current_clean' entran al historial; vueltas sucias quedan como NaN dentro de la ventana.
    Se calcula ANTES del filtro clean_pair. Nunca mira filas posteriores a t.
    """
    pairs = build_pairs(raw, history_window=k)  # línea de tiempo completa, antes de clean_pair
    pairs = pairs.sort_values(KEYS + ['stint', 'current_lap_number']).reset_index(drop=True)
    std = np.full(len(pairs), np.nan); slope = np.full(len(pairs), np.nan)
    n_valid = np.zeros(len(pairs), dtype=int); last_end = np.full(len(pairs), np.nan)
    # build_pairs elimina la última vuelta de cada piloto (sin t+1) pero eso no afecta ventanas
    # hacia atrás; igual recalculamos sobre raw para usar exactamente las vueltas observadas.
    data = raw.sort_values(KEYS + ['lap_number']).reset_index(drop=True).copy()
    data['current_clean'] = (data.lap_number.gt(1) & data.lap_time_s.gt(0) & data.is_accurate & ~data.pit_in
                             & ~data.pit_out & ~data.deleted & data.track_status.eq('1'))
    data['history_value'] = data.lap_time_s.where(data.current_clean)
    feats = {}
    for _, g in data.groupby(KEYS + ['stint'], dropna=False, sort=False):
        laps = g.lap_number.to_numpy(float); vals = g.history_value.to_numpy(float)
        ends = g.end_time_s.to_numpy(float); key = g[KEYS].iloc[0].tolist()
        for i in range(len(g)):
            lo = max(0, i - k + 1)
            v, x, e = vals[lo:i + 1], laps[lo:i + 1], ends[lo:i + 1]
            m = ~np.isnan(v)
            s = np.std(v[m], ddof=1) if m.sum() >= MIN_STD_LAPS else np.nan
            b = np.polyfit(x[m], v[m], 1)[0] if m.sum() >= MIN_SLOPE_LAPS else np.nan
            used_end = e[m].max() if m.any() else np.nan
            feats[(key[0], key[1], key[2], laps[i])] = (s, b, int(m.sum()), used_end, ends[i], float(i == 0))
    idx = list(zip(pairs.season, pairs['round'], pairs.driver_number, pairs.current_lap_number))
    arr = np.array([feats[t] for t in idx], dtype=float)
    out = pd.DataFrame({'pair_id': pairs.pair_id,
                        f'recent_std_s': arr[:, 0], f'recent_slope_s': arr[:, 1],
                        'history_valid_laps': arr[:, 2].astype(int),
                        'last_used_end_time_s': arr[:, 3], 't_end_time_s': arr[:, 4],
                        'pairs_end_time_s': pairs.end_time_s.to_numpy(),
                        'recent_mean_s_rebuilt': pairs.recent_mean_s.to_numpy(),
                        'first_lap_of_stint': arr[:, 5].astype(bool)})
    out['short_history'] = (out.history_valid_laps < MIN_SLOPE_LAPS).astype(int)
    return out


def join_features(frame, feats, name):
    merged = frame.merge(feats, on='pair_id', how='left', validate='one_to_one', indicator=True)
    coverage = float((merged._merge == 'both').mean())
    assert coverage == 1.0, f'{name}: pair_id sin features'
    assert len(merged) == len(frame) and merged.pair_id.is_unique
    return merged.drop(columns='_merge')


feat_tables = {k: history_features(raw, k) for k in (3, 5)}

# Chequeo 1 (tiempo) y 2 (fronteras), por k
for k, f in feat_tables.items():
    used_ok = (f.last_used_end_time_s.isna() | (f.last_used_end_time_s <= f.t_end_time_s + 1e-9)).all()
    t_ok = np.allclose(f.t_end_time_s, f.pairs_end_time_s)
    first = f[f.first_lap_of_stint]
    checks[f'check1_time_k{k}'] = {
        'rule': 'max end_time_s de las vueltas usadas <= end_time_s(t)',
        'rows': len(f), 'violations': int((~(f.last_used_end_time_s.isna() | (f.last_used_end_time_s <= f.t_end_time_s + 1e-9))).sum()),
        'passed': bool(used_ok and t_ok)}
    checks[f'check2_boundaries_k{k}'] = {
        'rule': 'primera vuelta de cada piloto/carrera/stint: std y pendiente NaN, short_history=1',
        'first_lap_rows': len(first), 'std_defined': int(first.recent_std_s.notna().sum()),
        'slope_defined': int(first.recent_slope_s.notna().sum()),
        'short_history_0': int((first.short_history == 0).sum()),
        'passed': bool(first.recent_std_s.isna().all() and first.recent_slope_s.isna().all()
                       and (first.short_history == 1).all())}
    assert checks[f'check1_time_k{k}']['passed'] and checks[f'check2_boundaries_k{k}']['passed']

# Chequeo 1b (perturbación del futuro): para 200 pair_id (seed 414) se alteran TODAS las vueltas > t
# del piloto en esa carrera (+50 s, marcadas como borradas) y se recalculan las features de t.
f3 = feat_tables[3].set_index('pair_id')
sample_ids = rng.choice(f3.index.to_numpy(), size=200, replace=False)
mism = 0
for pid in sample_ids:
    rnd, drv, lap = int(pid.split('-')[1][1:]), pid.split('-')[2], int(pid.split('-L')[1])
    g = raw[(raw['round'] == rnd) & (raw.driver_number == drv)].copy()
    fut = g.lap_number > lap
    g.loc[fut, 'lap_time_s'] += 50.0
    g.loc[fut & (g.lap_number > lap + 1), 'deleted'] = True
    ft = history_features(g, 3).set_index('pair_id')
    a = ft.loc[pid, ['recent_std_s', 'recent_slope_s', 'history_valid_laps']].to_numpy(float)
    b = f3.loc[pid, ['recent_std_s', 'recent_slope_s', 'history_valid_laps']].to_numpy(float)
    mism += int(not np.allclose(np.nan_to_num(a, nan=-999), np.nan_to_num(b, nan=-999)))
checks['check1b_future_perturbation_k3'] = {
    'rule': 'alterar todas las vueltas > t del piloto (+50 s; t+2.. marcadas deleted) no cambia std, pendiente ni conteo de t',
    'sampled_pair_ids': 200, 'seed': RANDOM_SEED, 'mismatches': mism, 'passed': mism == 0}
assert mism == 0

# Chequeo 3 (filas) se evalúa más abajo. Chequeo 4 (orden de construcción), revisado:
tr3, va3 = join_features(train, feat_tables[3], 'train'), join_features(val, feat_tables[3], 'val')
rebuilt_ok = np.allclose(pd.concat([tr3, va3]).recent_mean_s, pd.concat([tr3, va3]).recent_mean_s_rebuilt)
# contraste: std calculada DESPUÉS de filtrar clean_pair (incorrecto) difiere en cuántas filas
allp = pd.concat([train, val]).sort_values(KEYS + ['stint', 'current_lap_number'])
post = allp.groupby(KEYS + ['stint'], sort=False).current_lap_s.transform(lambda s: s.rolling(3, min_periods=2).std())
post = pd.Series(post.to_numpy(), index=allp.pair_id.to_numpy())
pre = pd.concat([tr3, va3]).set_index('pair_id').recent_std_s.reindex(post.index)
differs = int((~np.isclose(pre.fillna(-1), post.fillna(-1))).sum())
checks['check4_construction_order'] = {
    'original_rule_hito1': 'features sobre snapshots completos y luego unidas por pair_id. Falla: valores distintos a calcularlos después de filtrar.',
    'revised_rule': 'recent_mean_s reconstruido desde los snapshots crudos = recent_mean_s publicado en todas las filas unidas; se reporta cuántas filas cambiarían si std se calculara después del filtro clean_pair (incorrecto).',
    'join_coverage_train': 1.0, 'join_coverage_validation': 1.0,
    'recent_mean_s_matches_release': bool(rebuilt_ok),
    'rows_where_post_filter_std_would_differ': differs, 'rows_total': len(post),
    'passed': bool(rebuilt_ok)}
assert rebuilt_ok

# Cobertura / historial corto
cov = []
for k, f in feat_tables.items():
    for name, frame in [('train', train), ('validation', val)]:
        m = join_features(frame, f, name)
        for rnd, g in [('all', m)] + [(int(r), gg) for r, gg in m.groupby('round')] if name == 'validation' else [('all', m)]:
            cov.append({'k': k, 'split': name, 'round': rnd, 'rows': len(g),
                        'std_observed': int(g.recent_std_s.notna().sum()),
                        'slope_observed': int(g.recent_slope_s.notna().sum()),
                        'short_history_1': int(g.short_history.sum()),
                        'slope_coverage': round(float(g.recent_slope_s.notna().mean()), 4)})
pd.DataFrame(cov).to_csv(OUT / 'feature_coverage.csv', index=False)

# ---------------------------------------------------------- 3. Corridas (todas OLS, mismo pipeline)
RUNS = {  # id: (k, numeric extra, descripción)
    'R0': (3, [], 'OLS referencia: 6 inputs publicados (control emparejado de E1)'),
    'E1': (3, ['recent_std_s', 'recent_slope_s', 'short_history'], 'Candidato: R0 + std + pendiente + short_history, k=3'),
    'A1': (3, ['recent_slope_s', 'short_history'], 'Ablación: R0 + pendiente + short_history, k=3'),
    'A2': (3, ['recent_std_s', 'short_history'], 'Ablación: R0 + std + short_history, k=3'),
    'A3': (3, ['short_history'], 'Control: R0 + short_history solamente, k=3'),
    'E2': (5, ['recent_std_s', 'recent_slope_s', 'short_history'], 'Variación: como E1 con k=5'),
}
preds = pd.DataFrame({'pair_id': val.pair_id, 'round': val['round'], 'y_true': val[TARGET],
                      'current_lap_s': val.current_lap_s, 'persistence': val.current_lap_s})
models, metrics, frames = {}, [], {}
for rid, (k, extra, desc) in RUNS.items():
    tr, va = join_features(train, feat_tables[k], 'train'), join_features(val, feat_tables[k], 'val')
    assert (va.pair_id.to_numpy() == val.pair_id.to_numpy()).all()
    numeric = NUMERIC + extra
    feats = numeric + CATEGORICAL
    assert TARGET not in feats and not any(c.startswith('next_') or c == 'clean_pair' for c in feats)
    model = make_model('OLS', numeric=numeric).fit(tr[feats], tr[TARGET])   # solo train
    p = model.predict(va[feats])
    assert np.isfinite(p).all() and len(p) == 1808
    preds[rid] = p
    models[rid], frames[rid] = (model, feats), (tr, va)
    for label, mask in [('all_validation', np.ones(len(va), bool)), ('round_8', va['round'].eq(8).to_numpy()),
                        ('round_9', va['round'].eq(9).to_numpy())]:
        metrics.append({'run': rid, 'description': desc, 'k': k, 'inputs': '+'.join(feats),
                        'population': label, 'n': int(mask.sum()),
                        'MAE_s': float(mean_absolute_error(va.loc[mask, TARGET], p[mask]))})
preds['short_history_k3'] = frames['E1'][1].short_history.to_numpy()
preds['history_valid_laps_k3'] = frames['E1'][1].history_valid_laps.to_numpy()
for rid in RUNS:
    preds[f'abs_err_{rid}'] = (preds.y_true - preds[rid]).abs()
preds.to_csv(OUT / 'validation_predictions_hito2.csv', index=False)
met = pd.DataFrame(metrics); met.to_csv(OUT / 'metrics_all_runs.csv', index=False)

# Chequeo 3 (filas idénticas) + reproducción de Hito 1
ref = pd.read_csv(ROOT / 'salidas_referencia' / 'validation_reference_predictions.csv')
same_ids = set(ref.pair_id) == set(preds.pair_id) == set(val.pair_id) and len(ref) == len(preds) == 1808
r0_matches_hito1 = np.allclose(ref.set_index('pair_id').OLS_reference.reindex(preds.pair_id).to_numpy(), preds.R0.to_numpy(), atol=1e-8)
checks['check3_rows'] = {'rule': 'mismo conjunto de 1.808 pair_id en todas las corridas, sin duplicados ni NaN',
                         'validation_ids': int(preds.pair_id.nunique()), 'duplicates': int(preds.pair_id.duplicated().sum()),
                         'ids_equal_hito1_reference_file': bool(same_ids),
                         'nan_predictions': int(preds[list(RUNS)].isna().sum().sum()),
                         'R0_equals_hito1_OLS_predictions_atol_1e-8': bool(r0_matches_hito1),
                         'passed': bool(same_ids and r0_matches_hito1 and not preds.pair_id.duplicated().any())}
assert checks['check3_rows']['passed']

# ------------------------------------------------------------ 4. Tabla principal y por carrera
def mae(rid, pop='all_validation'):
    return float(met.query('run == @rid and population == @pop').MAE_s.iloc[0])

main = pd.DataFrame([
    {'version': 'OLS reference', 'run': 'R0', 'model_inputs': 'OLS · 6 inputs publicados', 'n': 1808, 'MAE_s': mae('R0'),
     'output': 'salidas_hito2/validation_predictions_hito2.csv:R0 (= salidas_referencia/validation_reference_predictions.csv:OLS_reference)'},
    {'version': 'Candidate', 'run': 'E1', 'model_inputs': 'OLS · 6 inputs + recent_std_s + recent_slope_s + short_history (k=3)', 'n': 1808,
     'MAE_s': mae('E1'), 'output': 'salidas_hito2/validation_predictions_hito2.csv:E1'},
    {'version': 'Matched control', 'run': 'R0 (misma corrida que OLS reference)', 'model_inputs': 'E1 sin el cambio = OLS · 6 inputs', 'n': 1808,
     'MAE_s': mae('R0'), 'output': 'salidas_hito2/validation_predictions_hito2.csv:R0'},
])
main.to_csv(OUT / 'comparison_table.csv', index=False)
diff_pooled = mae('R0') - mae('E1')

race = []
for rnd in (8, 9):
    m = preds['round'] == rnd
    c, e = preds.loc[m, 'abs_err_R0'].mean(), preds.loc[m, 'abs_err_E1'].mean()
    race.append({'round': rnd, 'n': int(m.sum()), 'MAE_control_R0_s': c, 'MAE_candidate_E1_s': e, 'control_minus_candidate_s': c - e})
race = pd.DataFrame(race)
w = race.n / race.n.sum()
race = pd.concat([race, pd.DataFrame([{'round': 'pooled (weighted by n)', 'n': int(race.n.sum()),
                                       'MAE_control_R0_s': float((race.MAE_control_R0_s * w).sum()),
                                       'MAE_candidate_E1_s': float((race.MAE_candidate_E1_s * w).sum()),
                                       'control_minus_candidate_s': float((race.control_minus_candidate_s * w).sum())}])])
race.to_csv(OUT / 'race_comparison.csv', index=False)
assert abs(race.iloc[-1].control_minus_candidate_s - diff_pooled) < 1e-12

# Regla de decisión declarada en Hito 1: se apoya si E1 < R0 en R8 y R9
supported = bool((race.iloc[:2].control_minus_candidate_s > 0).all())
explained_run = 'E1' if supported else 'R0'

# Corte declarado: short_history (k=3) 0/1, por carrera
sl = []
for rnd in ['all', 8, 9]:
    for sh in (0, 1):
        m = (preds.short_history_k3 == sh) & ((preds['round'] == rnd) if rnd != 'all' else True)
        sl.append({'round': rnd, 'short_history_k3': sh, 'n': int(m.sum()),
                   'MAE_R0_s': preds.loc[m, 'abs_err_R0'].mean(), 'MAE_E1_s': preds.loc[m, 'abs_err_E1'].mean(),
                   'control_minus_candidate_s': preds.loc[m, 'abs_err_R0'].mean() - preds.loc[m, 'abs_err_E1'].mean()})
pd.DataFrame(sl).to_csv(OUT / 'slice_short_history.csv', index=False)

# Corte por recent_count publicado (pregunta 1 del worksheet de la semana 11): persistencia, R0 y E1
rc = preds.merge(val[['pair_id', 'recent_count']], on='pair_id', validate='one_to_one')
checks['check6_valid_laps_equal_released_recent_count'] = {
    'rule': 'history_valid_laps (k=3, reconstruido desde los crudos) = recent_count publicado en las 1.808 filas',
    'mismatches': int((rc.history_valid_laps_k3 != rc.recent_count).sum()),
    'passed': bool((rc.history_valid_laps_k3 == rc.recent_count).all())}
assert checks['check6_valid_laps_equal_released_recent_count']['passed']
rc['abs_err_persistence'] = (rc.y_true - rc.persistence).abs()
rcs = rc.groupby(['round', 'recent_count']).agg(n=('pair_id', 'size'), MAE_persistence_s=('abs_err_persistence', 'mean'),
                                                 MAE_R0_s=('abs_err_R0', 'mean'), MAE_E1_s=('abs_err_E1', 'mean')).reset_index()
rcs['persistence_minus_R0_s'] = rcs.MAE_persistence_s - rcs.MAE_R0_s
rcs['R0_minus_E1_s'] = rcs.MAE_R0_s - rcs.MAE_E1_s
rcs.to_csv(OUT / 'slice_recent_count.csv', index=False)

# Caso inspeccionado: mayor |abs_err_E1 - abs_err_R0|
preds['err_gap'] = preds.abs_err_E1 - preds.abs_err_R0
case_id = preds.loc[preds.err_gap.abs().idxmax(), 'pair_id']
cv = frames['E1'][1].set_index('pair_id').loc[case_id]
cp = preds.set_index('pair_id').loc[case_id]
case = {'pair_id': case_id, 'selection_rule': 'máximo |abs_err_E1 - abs_err_R0| en validación',
        'round': int(cp['round']), 'event': cv.event_name, 'driver_number': cv.driver_number,
        'current_lap_number': int(cv.current_lap_number), 'stint': float(cv.stint), 'compound': cv.current_compound,
        'tyre_life': float(cv.current_tyre_life), 'current_lap_s': float(cv.current_lap_s),
        'recent_mean_s': float(cv.recent_mean_s), 'recent_std_s': float(cv.recent_std_s),
        'recent_slope_s': float(cv.recent_slope_s), 'history_valid_laps': int(cv.history_valid_laps),
        'short_history': int(cv.short_history), 'observed_next_lap_s': float(cp.y_true),
        'pred_R0_s': float(cp.R0), 'abs_err_R0_s': float(abs(cp.y_true - cp.R0)),
        'pred_E1_s': float(cp.E1), 'abs_err_E1_s': float(abs(cp.y_true - cp.E1))}
# Contexto del caso: vueltas del mismo piloto/stint alrededor de t (t+1 solo como observación del objetivo)
ctx = raw[(raw['round'] == case['round']) & (raw.driver_number == case['driver_number'])
          & raw.lap_number.between(case['current_lap_number'] - 4, case['current_lap_number'] + 1)]
ctx[['round', 'driver', 'lap_number', 'lap_time_s', 'stint', 'compound', 'tyre_life', 'track_status',
     'is_accurate', 'pit_in', 'pit_out', 'deleted']].to_csv(OUT / 'case_context_laps.csv', index=False)
(OUT / 'case_inspection.json').write_text(json.dumps(case, ensure_ascii=False, indent=2), encoding='utf-8')

# --------------------------------------------------------------------------- 5. SHAP
model, feats = models[explained_run]
tr, va = frames[explained_run]
prep, reg = model.named_steps['prepare'], model.named_steps['regression']
enc_names = list(prep.get_feature_names_out())
bg_idx = rng.choice(len(tr), size=SHAP_BACKGROUND_N, replace=False)
X_bg = prep.transform(tr.iloc[bg_idx][feats]); X_val = prep.transform(va[feats])
explainer = shap.LinearExplainer((reg.coef_, reg.intercept_), shap.maskers.Independent(X_bg, max_samples=SHAP_BACKGROUND_N))
sv = explainer(X_val)
values, base = sv.values, float(np.ravel(sv.base_values)[0])


def original_input(enc):
    for c in CATEGORICAL:
        if enc.startswith('category__' + c + '_'):
            return c
    return enc.split('__', 1)[1]


mapping = pd.DataFrame({'encoded_input': enc_names, 'original_input': [original_input(n) for n in enc_names],
                        'coefficient': reg.coef_})
mapping.to_csv(OUT / 'shap_encoded_mapping.csv', index=False)
grouped = pd.DataFrame(values, columns=enc_names).T.groupby(mapping.original_input.to_numpy()).sum().T
recon = base + grouped.sum(axis=1).to_numpy()
pred = model.predict(va[feats])
max_recon_err = float(np.max(np.abs(recon - pred)))
assert max_recon_err < 1e-6

# Local: misma fila que el caso inspeccionado
i = int(np.where(va.pair_id.to_numpy() == case_id)[0][0])
local = pd.DataFrame({'original_input': grouped.columns,
                      'input_value': [va.iloc[i][c] for c in grouped.columns],
                      'shap_contribution_s': grouped.iloc[i].to_numpy()}).sort_values('shap_contribution_s', key=np.abs, ascending=False)
local.to_csv(OUT / 'shap_local_contributions.csv', index=False)
local_summary = {'model': explained_run, 'pair_id': case_id, 'explainer': 'shap.LinearExplainer (interventional, Independent masker)',
                 'background': f'{SHAP_BACKGROUND_N} filas de train (rondas 1-7) muestreadas con seed {RANDOM_SEED}, transformadas por el pipeline ajustado en train',
                 'base_value_s': base, 'sum_contributions_s': float(grouped.iloc[i].sum()),
                 'base_plus_contributions_s': float(base + grouped.iloc[i].sum()),
                 'model_prediction_s': float(pred[i]), 'reconstruction_abs_diff_s': float(abs(base + grouped.iloc[i].sum() - pred[i])),
                 'tolerance_s': 1e-6, 'observed_next_lap_s': float(va.iloc[i][TARGET]),
                 'abs_error_s': float(abs(va.iloc[i][TARGET] - pred[i]))}
(OUT / 'shap_local_summary.json').write_text(json.dumps(local_summary, ensure_ascii=False, indent=2), encoding='utf-8')

# Global: media de |SHAP| sobre las 1.808 filas de validación, inputs originales (one-hot sumado por fila)
glob = pd.DataFrame({'original_input': grouped.columns, 'mean_abs_shap_s': grouped.abs().mean().to_numpy(),
                     'mean_signed_shap_s': grouped.mean().to_numpy()}).sort_values('mean_abs_shap_s', ascending=False)
glob['sample'] = 'todas las 1808 filas de validación (R8+R9)'
glob.to_csv(OUT / 'shap_global_mean_abs.csv', index=False)
glob_r = pd.concat([pd.DataFrame({'round': r, 'original_input': grouped.columns,
                                  'mean_abs_shap_s': grouped[va['round'].to_numpy() == r].abs().mean().to_numpy()})
                    for r in (8, 9)])
glob_r.to_csv(OUT / 'shap_global_by_round.csv', index=False)
pd.concat([va[['pair_id', 'round']].reset_index(drop=True), grouped.add_prefix('shap_').reset_index(drop=True),
           pd.Series(pred, name='prediction_s'), pd.Series(base, index=range(len(va)), name='base_value_s')],
          axis=1).to_csv(OUT / 'shap_values_validation.csv', index=False)
try:
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    g = glob.iloc[::-1]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.barh(g.original_input, g.mean_abs_shap_s, color='#3b6ea5')
    ax.set_xlabel('media |SHAP| (s) · 1.808 filas de validación'); ax.set_title(f'SHAP global · {explained_run} (OLS)')
    fig.tight_layout(); fig.savefig(OUT / 'shap_global_bar.png', dpi=130)
except ImportError:
    pass

# ----------------------------------------------------------------------- 6. Registro de corrida
try:
    commit = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True).stdout.strip()
except Exception:
    commit = None
run = {'script': 'hito2_experimento.py', 'git_commit_at_run': commit, 'seed': RANDOM_SEED, 'test_used': False,
       'decision_rule': 'E1 se apoya si control_minus_candidate > 0 en R8 y en R9 (pre-registrado en HITO1 §4)',
       'hypothesis_supported': supported, 'pooled_control_minus_candidate_s': diff_pooled,
       'shap_explained_run': explained_run, 'shap_max_reconstruction_error_s': max_recon_err,
       'checks': checks,
       'versions': {'python': sys.version.split()[0], 'numpy': np.__version__, 'pandas': pd.__version__,
                    'sklearn': sklearn.__version__, 'shap': shap.__version__},
       'sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in
                  [BASE / 'train_clean_v1.csv', BASE / 'validation_clean_v1.csv', BASE / 'nextlap_reference_v1.py',
                   BASE / 'data' / 'source_manifest_v2.json']}}
(OUT / 'run_hito2.json').write_text(json.dumps(run, ensure_ascii=False, indent=2, default=str), encoding='utf-8')

pd.set_option('display.width', 200)
print(met.pivot(index='run', columns='population', values='MAE_s').round(4))
print(main[['version', 'run', 'n', 'MAE_s']].round(4).to_string(index=False))
print(f'control - candidate (pooled) = {diff_pooled:+.4f} s')
print(race.round(4).to_string(index=False))
print(pd.DataFrame(sl).round(4).to_string(index=False))
print(json.dumps(case, ensure_ascii=False, indent=1))
print(json.dumps(local_summary, ensure_ascii=False, indent=1))
print(local.round(4).to_string(index=False))
print(glob.round(4).to_string(index=False))
print(json.dumps(checks, ensure_ascii=False, indent=1))
print('No test data used.')
