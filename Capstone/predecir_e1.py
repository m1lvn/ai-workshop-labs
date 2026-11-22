"""Candidato nominado al bonus · NextLap · Grupo 3 — E1 (OLS + recent_std_s + recent_slope_s + short_history).

Uso (desde Capstone/):
  ../.venv/bin/python predecir_e1.py --requests SOLICITUDES.csv --history HISTORIAL.csv --out PREDICCIONES.csv
  ../.venv/bin/python predecir_e1.py --autocheck     # reproduce E1 en validación R8-R9 con el contrato de entrada

- Ajusta E1 SOLO con las rondas 1-7 publicadas (train_clean_v1.csv + snapshots r01..r07). No usa validación ni test.
- SOLICITUDES.csv: pair_id, season, round, driver_number, stint, end_time_s y los 6 inputs de referencia
  (current_lap_s, recent_mean_s, current_lap_number, current_tyre_life, current_compound, current_team).
- HISTORIAL.csv: vista cronológica con el esquema de los snapshots publicados (race_2026_rXX_laps_v2.csv).
  Para cada solicitud solo se usan vueltas del mismo piloto/carrera/stint con end_time_s <= end_time_s de la solicitud.
- Ventana: hasta 3 vueltas consecutivas (t-2, t-1, t) del mismo stint; las inválidas (no current_clean) se excluyen.
  std con >= 2 vueltas válidas, pendiente con >= 3; si faltan -> NaN, imputado con la mediana de train (pipeline) y
  short_history = 1. Si la vuelta t no está en el historial: respaldo = mismas reglas (NaN + short_history = 1), contado.
"""
from pathlib import Path
import sys, json, argparse
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
BASE = ROOT / 'base_NextLap'
sys.path.insert(0, str(BASE))
from nextlap_reference_v1 import make_model, load_snapshots, NUMERIC, CATEGORICAL, TARGET, KEYS, BOOLEAN

K, MIN_STD, MIN_SLOPE = 3, 2, 3
EXTRA = ['recent_std_s', 'recent_slope_s', 'short_history']
FEATS = NUMERIC + EXTRA + CATEGORICAL
REQ_COLS = ['pair_id', 'season', 'round', 'driver_number', 'stint', 'end_time_s'] + NUMERIC + CATEGORICAL


def _clean(h):
    return (h.lap_number.gt(1) & h.lap_time_s.gt(0) & h.is_accurate & ~h.pit_in & ~h.pit_out & ~h.deleted
            & h.track_status.eq('1'))


def window_at(laps, lap_t):
    """laps: historial ya observado de un piloto/carrera/stint, ordenado por lap_number, que termina en t."""
    if len(laps) == 0 or laps.lap_number.iloc[-1] != lap_t:
        return np.nan, np.nan, 0, True                       # vuelta t ausente -> respaldo
    w = laps.iloc[-K:]                                       # hasta 3 vueltas consecutivas (posiciones), incluye t
    v = w.lap_time_s.where(_clean(w)).to_numpy(float); x = w.lap_number.to_numpy(float)
    m = ~np.isnan(v)
    s = np.std(v[m], ddof=1) if m.sum() >= MIN_STD else np.nan
    b = np.polyfit(x[m], v[m], 1)[0] if m.sum() >= MIN_SLOPE else np.nan
    return s, b, int(m.sum()), False


def features_for(requests, history):
    """Calcula las features de cada solicitud usando solo vueltas con end_time_s <= end_time_s(t)."""
    history = history.sort_values(KEYS + ['lap_number'])
    groups = {k: g for k, g in history.groupby(KEYS, sort=False)}
    out = []
    for r in requests.itertuples(index=False):
        g = groups.get((r.season, getattr(r, 'round'), r.driver_number))
        lap_t = float(r.current_lap_number)
        if g is None:
            out.append((np.nan, np.nan, 0, True)); continue
        asof = g[(g.end_time_s <= r.end_time_s + 1e-9) & (g.stint == r.stint)]   # límite as-of + mismo stint
        out.append(window_at(asof, lap_t))
    f = pd.DataFrame(out, columns=['recent_std_s', 'recent_slope_s', 'window_valid_laps', 'lap_t_missing'])
    f['short_history'] = (f.window_valid_laps < MIN_SLOPE).astype(int)
    return f


def read_history(path):
    h = pd.read_csv(path, dtype={'driver_number': str, 'track_status': str})
    for c in BOOLEAN:
        h[c] = h[c].astype(str).str.lower().eq('true')
    return h


def fit_e1():
    raw, _ = load_snapshots(BASE)                                  # verifica SHA-256 del manifiesto
    raw_tr = raw[raw['round'].between(1, 7)]
    train = pd.read_csv(BASE / 'train_clean_v1.csv', dtype={'driver_number': str})
    assert set(train['round']) == set(range(1, 8))
    f = features_for(train[REQ_COLS], raw_tr)
    assert not f.lap_t_missing.any()
    tr = pd.concat([train.reset_index(drop=True), f], axis=1)
    model = make_model('OLS', numeric=NUMERIC + EXTRA).fit(tr[FEATS], tr[TARGET])
    return model, raw


def predict(model, requests, history):
    requests = requests[REQ_COLS].reset_index(drop=True)
    assert requests.pair_id.is_unique, 'pair_id duplicados en las solicitudes'
    assert not any(c == TARGET or c.startswith('next_') for c in requests.columns)
    f = features_for(requests, history)
    X = pd.concat([requests, f], axis=1)
    p = model.predict(X[FEATS])
    assert np.isfinite(p).all() and len(p) == len(requests)
    res = pd.DataFrame({'pair_id': requests.pair_id, 'prediction_s': p,
                        'recent_count_window': f.window_valid_laps, 'short_history': f.short_history,
                        'lap_t_missing_fallback': f.lap_t_missing})
    return res


def autocheck():
    model, raw = fit_e1()
    val = pd.read_csv(BASE / 'validation_clean_v1.csv', dtype={'driver_number': str})
    hist = raw[raw['round'].isin([8, 9])]
    res = predict(model, val, hist)
    ref = pd.read_csv(ROOT / 'salidas_hito2' / 'validation_predictions_hito2.csv').set_index('pair_id')
    e1 = ref.E1.reindex(res.pair_id).to_numpy()
    mae = float(np.mean(np.abs(val[TARGET].to_numpy() - res.prediction_s.to_numpy())))
    out = {'rule': 'predecir_e1.py con el contrato de entrada (solicitudes sin next_*, historial as-of) = E1 de salidas_hito2',
           'n': len(res), 'max_abs_diff_vs_E1_s': float(np.max(np.abs(e1 - res.prediction_s.to_numpy()))),
           'equal_atol_1e-8': bool(np.allclose(e1, res.prediction_s, atol=1e-8)),
           'recent_count_window_equals_released': bool((res.recent_count_window.to_numpy() == val.recent_count.to_numpy()).all()),
           'fallback_lap_t_missing': int(res.lap_t_missing_fallback.sum()),
           'short_history_rows': int(res.short_history.sum()), 'validation_MAE_s': mae}
    (ROOT / 'salidas_final').mkdir(exist_ok=True)
    (ROOT / 'salidas_final' / 'bonus_autocheck.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
    print(json.dumps(out, indent=2))
    assert out['equal_atol_1e-8'] and out['recent_count_window_equals_released']


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--requests'); ap.add_argument('--history'); ap.add_argument('--out')
    ap.add_argument('--autocheck', action='store_true')
    a = ap.parse_args()
    if a.autocheck:
        autocheck()
    else:
        model, _ = fit_e1()
        req = pd.read_csv(a.requests, dtype={'driver_number': str})
        res = predict(model, req, read_history(a.history))
        res.to_csv(a.out, index=False)
        print(f'{len(res)} predicciones · respaldo por vuelta t ausente: {int(res.lap_t_missing_fallback.sum())} · '
              f'short_history: {int(res.short_history.sum())}')
