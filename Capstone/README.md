# Capstone NextLap · Grupo 3 (Francisco Polo, Milan Kurte)

**Repositorio:** https://github.com/m1lvn/ai-workshop-labs (carpeta `Capstone/`)
**Commit de la evidencia Hito 2:** [`9ad3dc3`](https://github.com/m1lvn/ai-workshop-labs/commit/9ad3dc310404d4d2384661505b56784cf3304faf) (`9ad3dc310404d4d2384661505b56784cf3304faf`): código, salidas, HITO2 y DECISION_LOG. El commit siguiente solo agrega este hash y el zip. `run_hito2.json → git_commit_at_run` muestra el commit padre (`b51a780`) porque el script se ejecutó antes de ser commiteado; al ejecutarlo de nuevo desde `9ad3dc3` las salidas CSV son idénticas.

## Hito 2 · mapa de evidencia

| Sección (rúbrica) | Dónde está el texto | Salida que lo respalda (en `salidas_hito2/`) | Código (`hito2_experimento.py`) |
|---|---|---|---|
| C1 Validez: split, ajuste solo en train, disponibilidad en t, filas | [HITO2 §0](HITO2.md#0-validez-de-la-evaluación-c1) | `run_hito2.json` (`checks`), `feature_coverage.csv` | §1 datos y split · §2 `history_features`, chequeos 1/1b/2/4 · §3 chequeo 3 |
| C2/C3 Comparación y ablación | [HITO2 §1](HITO2.md#1-comparación-ejecutada-y-ablación-c2-c3) | `comparison_table.csv`, `metrics_all_runs.csv`, `validation_predictions_hito2.csv` (una fila por `pair_id`, una columna por corrida) | §3 `RUNS`, §4 tabla principal |
| C4 Errores por contexto | [HITO2 §2](HITO2.md#2-errores-por-contexto-c4) | `race_comparison.csv`, `slice_short_history.csv`, `slice_recent_count.csv`, `case_inspection.json`, `case_context_laps.csv` | §4 |
| C5 SHAP local | [HITO2 §3](HITO2.md#3-interpretación-shap-c5-c6) | `shap_local_summary.json`, `shap_local_contributions.csv`, `shap_encoded_mapping.csv` | §5 |
| C6 SHAP global | [HITO2 §3](HITO2.md#global-shap_global_mean_abscsv-shap_global_barpng) | `shap_global_mean_abs.csv`, `shap_global_by_round.csv`, `shap_global_bar.png`, `shap_values_validation.csv` | §5 |
| Afirmación para la demo (ganancia en ms y %) | [HITO2 §4](HITO2.md#4-afirmación-revisada-para-la-demo) | `comparison_table.csv`, `slice_recent_count.csv` | §4 |
| C7 Reproducción | esta página | `run_hito2.json` (versiones, SHA-256, commit) | §6 |
| C8 Decisiones, IA y contribuciones | [DECISION_LOG](DECISION_LOG.md#hito-2-19-11-2026), [HITO2 §6](HITO2.md#6-explicación-individual) | — | — |

Referencia del Hito 1 (reutilizada sin cambios): `probar_referencia_v1.py` → `salidas_referencia/`. R0 en Hito 2 reproduce esas predicciones exactas.

## Datos

Paquete del curso `IIT414W_Capstone_NextLap_StudentData_v1` (versión v2 de snapshots), incluido en `Capstone/base_NextLap/`:
`train_clean_v1.csv` (5.772), `validation_clean_v1.csv` (1.808), `data/race_2026_r01..r09_laps_v2.csv`, `data/source_manifest_v2.json`.
`load_snapshots` verifica el SHA-256 de cada snapshot contra el manifiesto; los hashes de los CSV limpios están en `salidas_hito2/run_hito2.json`. Sin fuentes externas. Test reservado (R17) no incluido ni accedido.

## Entorno y comando

Python 3.12, versiones fijadas en `requirements.txt` (numpy 2.5.5, pandas 2.3.1, scikit-learn 1.9.1, shap 0.54.1, matplotlib 3.10.3).

```bash
# desde la raíz del repositorio
python3 -m venv .venv
.venv/bin/pip install -r Capstone/requirements.txt
cd Capstone
../.venv/bin/python probar_referencia_v1.py     # Hito 1: referencia (opcional)
../.venv/bin/python hito2_experimento.py        # Hito 2: ~10 s, regenera salidas_hito2/
```

Salida esperada: MAE de validación R0 0,38671 · E1 0,36636 · control − candidato +0,0203 s; todos los chequeos con `passed: true`.

## Hito 1

| Archivo | Contenido |
|---|---|
| [`HITO1.md`](HITO1.md) | Framing, referencia reproducida, hipótesis y plan de experimento |
| `probar_referencia_v1.py` | Script del curso (sin modificar) para mediana, persistencia y OLS |
| `base_NextLap/nextlap_reference_v1.py` | Pipeline de referencia del curso (`make_model`, `build_pairs`, `load_snapshots`) |
| `salidas_referencia/` | Salidas de nuestra ejecución de la referencia |
