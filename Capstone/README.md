# Hito 1 · NextLap · Grupo 3 (Francisco Polo, Milan Kurte)

| Archivo | Contenido |
|---|---|
| [`HITO1.md`](HITO1.md) | Framing, referencia reproducida, hipótesis y plan de experimento |
| [`DECISION_LOG.md`](DECISION_LOG.md) | Decisiones, contribuciones, uso de IA, revisión y próximos pasos |
| `probar_referencia_v1.py` | Script del curso (IIT414W, sin modificar) que reproduce mediana, persistencia y OLS |
| `base_NextLap/nextlap_reference_v1.py` | Pipeline de referencia del curso (`make_model`, `build_pairs`) |
| `salidas_referencia/` | Salidas generadas por **nuestra** ejecución: `reference_metrics.csv`, `validation_reference_predictions.csv` (con `pair_id`), `reference_run.json` (versiones y SHA-256) |

## Datos

`IIT414W_Capstone_NextLap_StudentData_v1.zip` / paquete del curso v2. Los CSV van en `Capstone/base_NextLap/` (`train_clean_v1.csv`, `validation_clean_v1.csv`, `data/race_2026_r01..r09_laps_v2.csv`, `data/source_manifest_v2.json`). Están en el repositorio. El zip de entrega no los duplica; se verifican con los SHA-256 de `reference_run.json`.

## Cómo ejecutar

```bash
python3 -m venv .venv
.venv/bin/pip install -r Capstone/requirements.txt   # numpy, pandas, scikit-learn
cd Capstone
../.venv/bin/python probar_referencia_v1.py
```

Salida esperada: 5.772 filas de train y 1.808 de validación; MAE en validación de 11,376 s (mediana), 0,409 s (persistencia) y 0,387 s (OLS). No se usa el test.
