"""Informe final · NextLap · Grupo 3 — revisión tras el feedback del Hito 2: respaldo con historial corto.

Ejecutar desde Capstone/:  ../.venv/bin/python final_respaldo.py
1) Ejecuta hito2_experimento.py (import) para regenerar R0, E1, ablaciones, SHAP y salidas_hito2/.
2) Aplica la regla PREDECLARADA en DECISION_LOG.md (commit 732988f, antes de esta ejecución):
   - selección del respaldo para recent_count < 3 SOLO con train (leave-one-round-out en R1-R7);
   - confirmación en validación (mismos 1.808 pair_id), por carrera y pooled, + bootstrap pareado;
   - congelar H solo si MAE pooled(H) <= MAE pooled(E1).
Escribe todo en salidas_final/. No usa ni accede al test reservado (ronda 17).
"""
from pathlib import Path
import json, subprocess
import numpy as np
import pandas as pd

import hito2_experimento as h2   # regenera salidas_hito2/ (determinista)
from nextlap_reference_v1 import make_model, NUMERIC, CATEGORICAL, TARGET

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'salidas_final'
OUT.mkdir(exist_ok=True)
SEED = h2.RANDOM_SEED  # 414
FULL = 3               # ventana de hasta 3 vueltas consecutivas (t-2, t-1, t)
N_BOOT = 2000
E1_EXTRA = ['recent_std_s', 'recent_slope_s', 'short_history']
OPTIONS = ['E1', 'R0', 'P']   # P = persistencia (current_lap_s)
checks = {}

# ------------------------------------------------ 1. Selección del respaldo SOLO con train (LORO R1-R7)
tr = h2.join_features(h2.train, h2.feat_tables[3], 'train')
assert (tr.history_valid_laps == tr.recent_count).all(), 'conteo de la ventana = recent_count publicado (train)'
checks['train_window_count_equals_recent_count'] = {'rows': len(tr), 'mismatches': int((tr.history_valid_laps != tr.recent_count).sum())}
f_r0 = NUMERIC + CATEGORICAL
f_e1 = NUMERIC + E1_EXTRA + CATEGORICAL
loro = []
for r in sorted(h2.TRAIN_ROUNDS):
    fit, hold = tr[tr['round'] != r], tr[tr['round'] == r]
    p = {'R0': make_model('OLS').fit(fit[f_r0], fit[TARGET]).predict(hold[f_r0]),
         'E1': make_model('OLS', numeric=NUMERIC + E1_EXTRA).fit(fit[f_e1], fit[TARGET]).predict(hold[f_e1]),
         'P': hold.current_lap_s.to_numpy()}
    loro.append(pd.DataFrame({'pair_id': hold.pair_id, 'round': r, 'recent_count': hold.recent_count,
                              'y_true': hold[TARGET], **{f'pred_{o}': p[o] for o in OPTIONS}}))
loro = pd.concat(loro, ignore_index=True)
assert len(loro) == len(tr) and loro.pair_id.is_unique
for o in OPTIONS:
    loro[f'abs_err_{o}'] = (loro.y_true - loro[f'pred_{o}']).abs()
loro.to_csv(OUT / 'loro_train_predictions.csv', index=False)
short_tr = loro[loro.recent_count < FULL]
rows = []
for label, g in [*[(f'R{r}', g) for r, g in short_tr.groupby('round')], ('pooled R1-R7', short_tr)]:
    rows.append({'held_out': label, 'n_recent_count_lt3': len(g),
                 **{f'MAE_{o}_s': g[f'abs_err_{o}'].mean() for o in OPTIONS}})
loro_tab = pd.DataFrame(rows)
loro_tab.to_csv(OUT / 'loro_train_short_history.csv', index=False)
pooled_loro = loro_tab.iloc[-1]
selected = min(OPTIONS, key=lambda o: pooled_loro[f'MAE_{o}_s'])   # regla predeclarada
# misma tabla para recent_count = 3 (contexto: ¿E1 gana a R0 con historial completo en train?)
full_tr = loro[loro.recent_count == FULL]
loro_full = {o: float(full_tr[f'abs_err_{o}'].mean()) for o in OPTIONS}
per_round = loro_tab.iloc[:-1]
loro_wins = {o: int((per_round[[f'MAE_{x}_s' for x in OPTIONS]].idxmin(axis=1) == f'MAE_{o}_s').sum()) for o in OPTIONS}

# ------------------------------------------------ 2. Confirmación en validación (mismos 1.808 pair_id)
pr = h2.preds.merge(h2.val[['pair_id', 'recent_count']], on='pair_id', validate='one_to_one')
assert len(pr) == 1808 and pr.pair_id.is_unique and pr[['R0', 'E1', 'persistence']].notna().all().all()
pr['P'] = pr.persistence
short = pr.recent_count < FULL
fallback_col = {'E1': 'E1', 'R0': 'R0', 'P': 'P'}[selected]
pr['H'] = np.where(short, pr[fallback_col], pr.E1)
# variantes de respaldo (para reportar las dos opciones, no para elegir)
pr['H_R0'] = np.where(short, pr.R0, pr.E1)
pr['H_P'] = np.where(short, pr.P, pr.E1)
for c in ['R0', 'E1', 'P', 'H', 'H_R0', 'H_P']:
    pr[f'ae_{c}'] = (pr.y_true - pr[c]).abs()
ref_ids = pd.read_csv(ROOT / 'salidas_referencia' / 'validation_reference_predictions.csv').pair_id
checks['validation_ids'] = {'rule': 'mismos 1.808 pair_id únicos que la referencia del Hito 1 y que salidas_hito2',
                            'n': int(pr.pair_id.nunique()), 'duplicates': int(pr.pair_id.duplicated().sum()),
                            'equal_to_reference_ids': bool(set(ref_ids) == set(pr.pair_id) and len(ref_ids) == len(pr)),
                            'nan_predictions': int(pr[['R0', 'E1', 'P', 'H']].isna().sum().sum()),
                            'fallback_rows': int(short.sum())}
assert checks['validation_ids']['equal_to_reference_ids'] and checks['validation_ids']['duplicates'] == 0

# (a) R0 vs persistencia en filas recent_count < 3, por carrera y pooled
a = []
for label, m in [('R8', short & pr['round'].eq(8)), ('R9', short & pr['round'].eq(9)), ('pooled', short)]:
    g = pr[m]
    a.append({'context': label, 'n': len(g), 'MAE_R0_s': g.ae_R0.mean(), 'MAE_persistence_s': g.ae_P.mean(),
              'MAE_E1_s': g.ae_E1.mean(), 'persistence_minus_R0_s': g.ae_P.mean() - g.ae_R0.mean()})
for rc in (1, 2):
    for rd in (8, 9):
        g = pr[(pr.recent_count == rc) & pr['round'].eq(rd)]
        a.append({'context': f'R{rd} recent_count={rc}', 'n': len(g), 'MAE_R0_s': g.ae_R0.mean(),
                  'MAE_persistence_s': g.ae_P.mean(), 'MAE_E1_s': g.ae_E1.mean(),
                  'persistence_minus_R0_s': g.ae_P.mean() - g.ae_R0.mean()})
pd.DataFrame(a).to_csv(OUT / 'validation_short_history_R0_vs_persistence.csv', index=False)

# (b) H vs E1 vs R0 en las 1.808 filas, por carrera y pooled
b = []
for label, m in [('R8', pr['round'].eq(8)), ('R9', pr['round'].eq(9)), ('pooled', pd.Series(True, index=pr.index))]:
    g = pr[m]
    b.append({'context': label, 'n': len(g), 'n_fallback': int((short & m).sum()),
              **{f'MAE_{c}_s': g[f'ae_{c}'].mean() for c in ['R0', 'E1', 'H', 'H_R0', 'H_P']},
              'E1_minus_H_s': g.ae_E1.mean() - g.ae_H.mean(), 'R0_minus_H_s': g.ae_R0.mean() - g.ae_H.mean(),
              'R0_minus_E1_s': g.ae_R0.mean() - g.ae_E1.mean()})
btab = pd.DataFrame(b)
btab.to_csv(OUT / 'validation_hybrid_by_race.csv', index=False)
# ponderación por n: pooled = suma ponderada de carreras
w = btab.set_index('context')
recomputed = (w.loc['R8', 'n'] * w.loc['R8', 'E1_minus_H_s'] + w.loc['R9', 'n'] * w.loc['R9', 'E1_minus_H_s']) / w.loc['pooled', 'n']
assert abs(recomputed - w.loc['pooled', 'E1_minus_H_s']) < 1e-12

# bootstrap pareado (remuestreo de pair_id, seed 414)
rng = np.random.default_rng(SEED)
d_e1_h = (pr.ae_E1 - pr.ae_H).to_numpy(); d_r0_e1 = (pr.ae_R0 - pr.ae_E1).to_numpy()
d_r0_h = (pr.ae_R0 - pr.ae_H).to_numpy()
d_e1_hr0 = (pr.ae_E1 - pr.ae_H_R0).to_numpy(); d_e1_hp = (pr.ae_E1 - pr.ae_H_P).to_numpy()
idx = rng.integers(0, len(pr), size=(N_BOOT, len(pr)))
boot = {name: np.percentile(d[idx].mean(axis=1), [2.5, 97.5]).tolist()
        for name, d in [('E1_minus_H', d_e1_h), ('R0_minus_E1', d_r0_e1), ('R0_minus_H', d_r0_h),
                        ('E1_minus_H_R0_not_selected', d_e1_hr0), ('E1_minus_H_P_not_selected', d_e1_hp)]}

# ------------------------------------------------ 3. Regla de congelamiento (predeclarada)
mae_h, mae_e1 = float(pr.ae_H.mean()), float(pr.ae_E1.mean())
frozen = 'H' if (selected != 'E1' and mae_h <= mae_e1) else 'E1'
pr[['pair_id', 'round', 'recent_count', 'y_true', 'R0', 'E1', 'P', 'H', 'H_R0', 'H_P',
    'ae_R0', 'ae_E1', 'ae_P', 'ae_H']].to_csv(OUT / 'validation_predictions_final.csv', index=False)

commit = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True).stdout.strip()
summary = {
    'script': 'final_respaldo.py', 'git_commit_at_run': commit, 'seed': SEED, 'test_used': False,
    'predeclaration': 'DECISION_LOG.md, sección "Informe final", commit 732988f (antes de esta ejecución)',
    'window': 'hasta 3 vueltas consecutivas (t-2, t-1, t) del mismo piloto/carrera/stint; inválidas excluidas; recent_count en {1,2,3}',
    'selection_train_loro': {'population': 'filas de train con recent_count < 3, cada ronda predicha por un modelo ajustado en las otras 6',
                             'n': int(pooled_loro['n_recent_count_lt3']),
                             'MAE_s': {o: float(pooled_loro[f'MAE_{o}_s']) for o in OPTIONS},
                             'rounds_won_of_7': loro_wins,
                             'selected_fallback': selected,
                             'context_recent_count_eq_3_MAE_s': loro_full},
    'validation': {'MAE_pooled_s': {c: float(pr[f'ae_{c}'].mean()) for c in ['R0', 'E1', 'P', 'H', 'H_R0', 'H_P']},
                   'E1_minus_H_s': mae_e1 - mae_h, 'bootstrap_95ci_s': boot, 'n_boot': N_BOOT},
    'freeze_rule': 'congelar H si selected != E1 y MAE_pooled(H) <= MAE_pooled(E1); si no, mantener E1',
    'frozen_candidate': frozen, 'checks': checks,
}
(OUT / 'run_final.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=float), encoding='utf-8')

pd.set_option('display.width', 200)
print('\nLORO train (recent_count < 3):\n', loro_tab.round(5).to_string(index=False))
print('LORO train (recent_count = 3):', {k: round(v, 5) for k, v in loro_full.items()})
print('Rondas ganadas (de 7):', loro_wins)
print('Respaldo seleccionado (solo train):', selected)
print('\nValidación, filas recent_count < 3:\n', pd.DataFrame(a).round(5).to_string(index=False))
print('\nValidación, 1.808 filas:\n', btab.round(5).to_string(index=False))
print('Bootstrap IC95 (s):', {k: [round(x, 5) for x in v] for k, v in boot.items()})
print('Candidato congelado:', frozen)
