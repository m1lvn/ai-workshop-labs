# DECISION_LOG · NextLap · Grupo 3

Integrantes: Francisco Polo, Milan Kurte.

## Decisiones

| Fecha | Decisión | Evidencia | Quién |
|---|---|---|---|
| 12-11-2026 | Reproducir la referencia con el script del curso `probar_referencia_v1.py` (sin modificar, con atribución) en un entorno propio (`.venv`) | Salida regenerada en `salidas_referencia/`: 1.808 filas de validación, MAE OLS 0,387 s; coincide con los valores del paquete | Milan Kurte |
| 12-11-2026 | Dirección: historial de ritmo (std y pendiente de las últimas k vueltas) en vez de clima o tráfico | Usa solo datos publicados: no depende de una fuente externa sin verificar | Francisco Polo, Milan Kurte |
| 12-11-2026 | Usuario: ingeniero de carrera; decisión: avisar al piloto o preparar una alerta de degradación. Se declara explícitamente que no decide paradas en boxes | Brief del Hito 1 (límite de `clean_pair`) | Francisco Polo, Milan Kurte |
| 12-11-2026 | Historial corto: imputar con la mediana de train + bandera `short_history`; no se eliminan filas | Se evita comparar sobre menos filas (ejemplo de la hoja de trabajo: 600 vs. 1.000 filas) | Francisco Polo, Milan Kurte |
| 12-11-2026 | Búsqueda limitada a k ∈ {3, 5} + 3 ablaciones (6 corridas) | Evita una búsqueda grande sobre validación | Francisco Polo, Milan Kurte |

## Contribuciones (cada integrante puede explicar lo suyo)

Todas las decisiones de la tabla anterior (dirección, usuario y decisión, regla de historial corto, búsqueda acotada) se tomaron **en conjunto**, en una sesión de trabajo con ambos presentes. El trabajo se dividió en partes iguales:

- **Milan Kurte:** preparó el entorno (`.venv`), ejecutó la referencia y verificó conteos, rondas, `pair_id` disjuntos y que el preprocesamiento se ajusta solo en train. Armó el README, el paquete y la entrega en GitHub.
- **Francisco Polo:** co-definió la hipótesis de historial de ritmo, la regla `short_history` y la decisión del ingeniero de carrera. Revisó el plan de experimento (controles fijos, ablaciones A1–A3, chequeos 1–5) y comparó los MAE reportados en HITO1 con las salidas de `salidas_referencia/`.

## Uso de IA

- **Herramienta:** Claude Code (Anthropic), sesión del 12-11-2026.
- **Para qué se usó:** listar las decisiones pendientes del Hito 1, correr el script de referencia en nuestro entorno, proponer la hipótesis de historial de ritmo y redactar borradores de `HITO1.md`, `DECISION_LOG.md` y `README.md`.
- **Sugerencias adoptadas:** la dirección de historial de ritmo con la regla de mediana de train + `short_history`; la estructura de ablaciones (A1–A3).
- **Cómo se verificó:** comparamos la tabla de MAE y los conteos con `reference_run.json` del paquete del curso (idénticos). Confirmamos en `nextlap_reference_v1.py` (`build_pairs`) que `recent_mean_s` usa `rolling(3)` por piloto/carrera/stint e incluye la vuelta t, lo que respalda la regla de disponibilidad propuesta. Revisamos que ninguna feature propuesta use columnas `next_*`.
- **Lo que no se delegó:** la elección final de la dirección, del usuario y la decisión, y la responsabilidad de explicar cada punto en la demo.

## Revisión tras feedback

- Feedback de la sesión del 6-11 (hoja de trabajo): un candidato evaluado en menos filas no demuestra una mejora. **Cambio:** la regla original de "descartar vueltas sin historial suficiente" se reemplazó por imputación con la mediana de train + bandera, y se agregó el chequeo de un conjunto de `pair_id` idéntico.

## Próximos pasos y responsables (antes del Hito 2, 19-11)

| Tarea | Responsable |
|---|---|
| Implementar `recent_std_s`, `recent_slope_s`, `short_history` desde los snapshots crudos + chequeos 1–4 | Francisco Polo |
| Correr R0, E1, A1–A3, E2 y registrar todas las corridas aquí | Milan Kurte |
| MAE por carrera, errores contextuales y SHAP | Ambos (Milan: MAE por carrera y errores contextuales; Francisco: SHAP) |

## Registro de corridas

| Corrida | Fecha | Features | n validación | MAE (s) | Nota |
|---|---|---|---|---|---|
| R0 | 12-11-2026 | 6 de referencia | 1808 | 0.3867 | Reproducción propia |
| R0 | 19-11-2026 | 6 de referencia (OLS) | 1808 | 0.38671 | Reajustada en `hito2_experimento.py`; predicciones idénticas a Hito 1 (atol 1e-8). Control emparejado de E1 |
| E1 | 19-11-2026 | R0 + std + pendiente + short_history, k=3 | 1808 | 0.36636 | **Candidato.** R8 0.35604 / R9 0.38119; control − candidato = +0.0203 s |
| A1 | 19-11-2026 | R0 + pendiente + short_history, k=3 | 1808 | 0.38686 | **Sin mejora** (peor que R0 por 0.0002 s): la tendencia no aporta |
| A2 | 19-11-2026 | R0 + std + short_history, k=3 | 1808 | 0.36567 | Mejor MAE en validación: la ganancia viene de la variabilidad |
| A3 | 19-11-2026 | R0 + short_history, k=3 | 1808 | 0.38679 | **Sin mejora**: la bandera sola no explica la ganancia |
| E2 | 19-11-2026 | Como E1 con k=5 | 1808 | 0.37993 | **Peor que E1**: se descarta k=5 |

Todas las corridas: OLS, mismo pipeline `make_model` ajustado solo en train, mismas 1.808 `pair_id`, seed 414. Salidas: `salidas_hito2/metrics_all_runs.csv` y `validation_predictions_hito2.csv`.

---

# Hito 2 (19-11-2026)

## Decisiones

| Fecha | Decisión | Evidencia | Quién |
|---|---|---|---|
| 19-11-2026 | Hipótesis sin cambios respecto del Hito 1. k=3 fijado como candidato **antes** de correr; k=5 solo como prueba adicional | HITO1 §4 | Francisco Polo, Milan Kurte |
| 19-11-2026 | Candidato OLS con los 6 inputs + el cambio, de modo que R0 sea también el control emparejado (misma familia, pipeline, filas y métrica) | `comparison_table.csv` | Francisco Polo, Milan Kurte |
| 19-11-2026 | Ventana con la misma regla de historial que `recent_mean_s` en `build_pairs` (solo vueltas `current_clean` ya observadas, por piloto/carrera/stint, antes de `clean_pair`) | Chequeos 1, 1b, 2 y 4 en `run_hito2.json` | Francisco Polo, Milan Kurte (lidera implementación: Francisco Polo) |
| 19-11-2026 | **Mantener E1** (control − candidato = +0.0203 s; positivo en R8 +0.0175 y R9 +0.0244, el criterio pre-registrado). No cambiar a A2 aunque tenga 0.0007 s menos: esa diferencia se eligió sobre validación | `race_comparison.csv`, `metrics_all_runs.csv` | Francisco Polo, Milan Kurte |
| 19-11-2026 | Descartar k=5 (E2 0.37993 > E1 0.36636) y declarar que la tendencia no está respaldada (A1 ≈ R0) | `metrics_all_runs.csv` | Francisco Polo, Milan Kurte (lidera implementación: Milan Kurte) |
| 19-11-2026 | Caso inspeccionado: la fila con mayor \|error E1 − error R0\| (`2026-R9-23-L7`). Corte declarado: `short_history` por carrera | `case_inspection.json`, `slice_short_history.csv` | Francisco Polo, Milan Kurte (lidera implementación: Milan Kurte) |
| 19-11-2026 | SHAP sobre E1 (el modelo retenido) con LinearExplainer, background de 500 filas de train (seed 414) y one-hot sumado al input original | `shap_local_summary.json`, `shap_global_mean_abs.csv` | Francisco Polo, Milan Kurte (lidera implementación: Francisco Polo) |

## Chequeo definido antes de implementar y resultado

- **Criterio registrado (HITO1 §4):** la hipótesis se apoya si E1 baja el MAE frente a R0 en las mismas filas **en ambas carreras**, y si A1/A2 muestran que la mejora viene de la información nueva y no de la bandera (A3). **Resultado:** se cumple (R8 +0.0175 s, R9 +0.0244 s). A3 ≈ R0, así que la bandera sola no explica la ganancia. A2 ≈ E1 y A1 ≈ R0, así que la mejora es de la **std** y **no de la pendiente**. La hipótesis queda respaldada solo en parte: la variabilidad sí, la tendencia no.
- **Chequeos 1–3 y 5:** se aplicaron tal como se escribieron. Todos pasaron (`run_hito2.json`).

## Revisión tras chequeo

- **Chequeo 4 (orden de construcción), revisado.** La entrada original decía: *"Features calculadas sobre los snapshots completos y luego unidas por `pair_id` a los pares limpios. Falla: valores distintos a calcularlos después de filtrar."* Al implementarlo vimos que esa condición de falla está al revés: calcular **después** del filtro `clean_pair` es justamente lo incorrecto, y es esperable que dé valores distintos. **Regla revisada:** (a) `recent_mean_s` reconstruido desde los snapshots crudos debe coincidir con el `recent_mean_s` publicado en todas las filas unidas (cumple: confirma la misma línea de tiempo que la referencia); (b) reportar cuántas filas cambiarían con el cálculo incorrecto post-filtro: 621 de 7.580. La entrada original se conserva en `run_hito2.json → check4_construction_order.original_rule_hito1`.
- **Chequeo 1b agregado:** perturbar todas las vueltas > t (+50 s, marcadas como borradas) en 200 `pair_id` (seed 414) no cambia las features de t (0 diferencias). Es más fuerte que comparar solo marcas de tiempo.
- **Entorno:** al instalar `shap` se actualizaron numpy (2.0.2 → 2.5.5) y scikit-learn (1.8.0 → 1.9.1). Verificamos que las predicciones de R0 son idénticas a las del Hito 1 (`check3_rows.R0_equals_hito1_OLS_predictions_atol_1e-8 = true`) y fijamos las versiones en `requirements.txt`.

## Siguiente chequeo

En las filas `short_history = 1` de R9 (n=148), E1 empeora a R0 en 0.030 s. Siguiente prueba, con las mismas 1.808 `pair_id` y separada por carrera: (a) usar R0 como respaldo cuando `short_history = 1`; (b) reemplazar `recent_mean_s` y std por versiones robustas (mediana/MAD), por el caso `2026-R9-23-L7`, donde una vuelta atípica en t sigue contaminando la media. Además, confirmar si se puede quitar la pendiente (A2 vs E1) sin seleccionar sobre validación.

## Contribuciones Hito 2

Igual que en el Hito 1, trabajamos **en persona y en conjunto**: todas las decisiones de la tabla (ventana antes de `clean_pair`, mantener E1 frente a A2, descartar k=5, caso inspeccionado, configuración de SHAP) se discutieron y tomaron entre los dos, así que no corresponde adjudicar ninguna a una sola persona. Lo que se repartió fue quién **lideró la implementación y la verificación** de cada parte, y cada uno puede explicar todas las decisiones:

- **Francisco Polo:** implementación de `recent_std_s`, `recent_slope_s` y `short_history` desde los snapshots crudos; chequeos 1, 1b, 2 y la revisión del chequeo 4; análisis SHAP local y global. Puede explicar: por qué la ventana se arma antes de `clean_pair` y la regla de historial corto.
- **Milan Kurte:** corridas R0, E1, A1–A3 y E2, tabla de comparación, MAE por carrera con ponderación, corte `short_history`, caso inspeccionado, entorno y paquete de entrega. Puede explicar: la decisión de mantener E1 y no A2, y el diagnóstico de R9 con historial corto.

## Uso de IA (Hito 2)

- **Herramienta:** Claude Code (Anthropic), sesión del 19-11-2026.
- **Prompt representativo:** *"Necesito ayuda para completar el hito 2 del capstone […] Dime qué decisiones debo tomar para terminarlo."* Después: *"leímos tus recomendaciones y seguiremos con eso"*.
- **Sugerencias adoptadas:** la lista de decisiones D1–D17 (candidato OLS con R0 como control emparejado, k=3 fijo, caso = mayor diferencia de error, LinearExplainer con background de train); el script `hito2_experimento.py`; los borradores de `HITO2.md`, de esta sección y del README.
- **Qué cambiamos o rechazamos:** al ver que A2 (solo std + bandera) tenía un MAE algo menor que E1 (0.36567 vs. 0.36636 s), consideramos reemplazar el candidato por A2. Lo **rechazamos** y mantuvimos E1, el candidato fijado antes de correr: la diferencia (0.0007 s) se observó en la misma validación y es unas diez veces menor que la variación de la mejora entre carreras (R8 +0.0175, R9 +0.0244). Retirar la pendiente queda como siguiente chequeo, sin usar R8–R9.
- **Cómo se verificó:** (1) R0 reajustado reproduce exactamente las predicciones del Hito 1; (2) chequeos 1, 1b, 2, 3 y 4 en `run_hito2.json`; (3) la reconstrucción SHAP base + contribuciones = predicción en las 1.808 filas (error máx. < 1e-6 s) y a mano para `2026-R9-23-L7` (86,713 + 12,514 = 99,227); (4) recalculamos a mano el pooled ponderado (1066·0,01753 + 742·0,02439)/1808 = 0,02034; (5) revisamos en `case_context_laps.csv` que la vuelta 7 de ALB (105,13 s) tenga bandera verde y no sea pit ni borrada.
- **Lo que no se delegó:** la decisión de mantener E1, las explicaciones individuales en HITO2 §5 y la defensa en la demo.
