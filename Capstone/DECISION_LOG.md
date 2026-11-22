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

- **Tras la clínica del 19-11 (worksheet de la semana 11, pregunta 1: "¿OLS sigue ganándole a persistencia en R9 cuando `recent_count = 1`?"):** agregamos al script `slice_recent_count.csv` y el chequeo 6. **Resultado:** nuestro conteo de vueltas limpias coincide con el `recent_count` publicado en las 1.808 filas (0 diferencias). En R9 con `recent_count = 1` (n=66), R0 ya es peor que la persistencia (−0.0118 s) y E1 lo empeora más (−0.0398 s). **Cambio:** el diagnóstico pasa de "falla nuestra imputación" a "los modelos lineales fallan con historial corto en R9, desde la referencia", y el siguiente chequeo (a) agrega la persistencia como respaldo. Las salidas anteriores no cambiaron (md5 idénticos). También agregamos la ganancia en ms y % y la afirmación revisada (HITO2 §4).

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

---

# Informe final (22-11-2026)

## Feedback recibido

- **Hito 2 (feedback del instructor, 22-11, 100/100).** Prioridad: *historial corto en R9*. E1 agrega 29,7 ms de MAE en 148 filas; en las 66 filas con una sola vuelta limpia, el OLS de referencia ya pierde contra la persistencia. Chequeo pedido: predeclarar un respaldo cuando `recent_count < 3`, comparar R0 y persistencia en los mismos IDs por carrera y revisar el MAE pooled antes de congelar la regla; describir la feature como una ventana de hasta tres vueltas consecutivas, excluyendo las inválidas dentro de ella.
- **Demo Day (20-11).** El jurado no dio una prioridad específica. Una sola revisión responde a la prioridad del Hito 2.

## Predeclaración de la regla de respaldo (escrita y commiteada ANTES de ejecutar `final_respaldo.py`)

**Corrección de la descripción.** `recent_std_s`, `recent_slope_s` y `recent_count` se calculan sobre una **ventana de hasta tres vueltas consecutivas (t−2, t−1, t) del mismo piloto, carrera y stint**; las vueltas inválidas (no `current_clean`) dentro de la ventana se excluyen, no se reemplazan por vueltas anteriores. Por eso `recent_count` ∈ {1, 2, 3} y "historial corto" significa `recent_count < 3`. No son "las últimas 3 vueltas limpias".

**Opciones para filas con `recent_count < 3`** (`recent_count` es un input publicado y disponible en t; chequeo 6 confirma que coincide con nuestro conteo):
- `E1`: sin respaldo (el candidato del Hito 2).
- `R0`: usar la predicción del OLS de referencia (6 inputs).
- `P`: persistencia, `next_lap_s` predicho = `current_lap_s`.
En filas con `recent_count = 3` siempre se usa E1.

**Transparencia.** Los MAE de validación de R0, E1 y persistencia por `recent_count` ya se vieron en el Hito 2 (`salidas_hito2/slice_recent_count.csv`). Para no elegir el respaldo mirando la validación otra vez:

1. **Selección solo con train (R1–R7), leave-one-round-out.** Para cada ronda r ∈ {1..7}: se reajustan R0 y E1 con las otras 6 rondas (mismo pipeline, imputación y escalado ajustados en esas 6) y se predicen las filas de r. En las filas de train con `recent_count < 3`, se compara el MAE pooled (ponderado por n) de E1, R0 y P. **La opción con menor MAE LORO es la seleccionada.** Si es E1, no hay respaldo.
2. **Confirmación en validación (mismos 1.808 `pair_id`).** Se reportan, por carrera y pooled: (a) R0 vs persistencia en las filas `recent_count < 3`; (b) el candidato híbrido H = E1 si `recent_count = 3`, si no la opción seleccionada, vs E1 y vs R0 en las 1.808 filas. Se agrega un IC95 bootstrap pareado (2.000 remuestreos de `pair_id`, seed 414) para E1 − H.
3. **Regla de congelamiento.** Se congela H como candidato final **si y solo si** el MAE pooled de H en las 1.808 filas es ≤ el de E1. Si no, se mantiene E1 sin respaldo y se reporta como resultado nulo/negativo. No se eligen umbrales por carrera ni se cambia de opción después de ver la validación.
4. El test reservado (R17) no se usa.

## Resultado de la regla predeclarada (`final_respaldo.py`, ejecutado después de `732988f`)

| Fecha | Decisión | Evidencia | Quién |
|---|---|---|---|
| 22-11-2026 | Respaldo seleccionado **solo con train** (LORO R1–R7, filas `recent_count < 3`, n = 1.185): **E1** (0,59681 s) frente a persistencia (0,61775) y R0 (0,63431). E1 gana 5/7 rondas, P 2/7, R0 0/7 | `salidas_final/loro_train_short_history.csv`, `run_final.json → selection_train_loro` | Francisco Polo, Milan Kurte (lidera: Francisco Polo) |
| 22-11-2026 | Confirmación en validación, mismas 321 filas cortas: R0 vs persistencia R8 0,38735/0,39849 (n=173), R9 0,43788/0,43729 (n=148), pooled 0,41065/0,41638. En 1.808 filas: E1 0,36636; H_R0 0,36567 (E1−H_R0 +0,7 ms, IC95 [−2,2; +3,4] ms); H_P 0,36669 (−0,3 ms, IC95 [−4,3; +3,4] ms) | `salidas_final/validation_short_history_R0_vs_persistence.csv`, `validation_hybrid_by_race.csv`, `run_final.json` | Francisco Polo, Milan Kurte (lidera: Milan Kurte) |
| 22-11-2026 | **Regla aplicada: se mantiene E1 sin respaldo** (selected = E1). No se adopta H_R0 aunque mejore 0,7 ms en validación: no fue seleccionado en train, empeora R8 (0,35604 → 0,35899) y su IC95 incluye 0. El fallo de R9 con historial corto queda como límite declarado | `run_final.json → frozen_candidate = E1` | Francisco Polo, Milan Kurte |
| 22-11-2026 | Descripción corregida de la ventana (hasta 3 vueltas consecutivas, inválidas excluidas) en el informe y en el docstring de `history_features`; las salidas no cambian (CSV de `salidas_hito2/` con md5 idéntico) | `INFORME_FINAL.md` §2 | Francisco Polo, Milan Kurte (lidera: Francisco Polo) |
| 22-11-2026 | Nominar **E1** al bonus. `predecir_e1.py` implementa el contrato de entrada (solicitudes sin `next_*`, historial as-of por `end_time_s`) y reproduce E1 en R8–R9 (máx. diferencia 1,4e-14 s, 0 respaldos) | `salidas_final/bonus_autocheck.json` | Francisco Polo, Milan Kurte |

### Registro de corridas (informe final)

| Corrida | Fecha | Features / regla | n validación | MAE (s) | Nota |
|---|---|---|---|---|---|
| LORO-E1/R0/P | 22-11-2026 | R1–R7, cada ronda predicha con modelo ajustado en las otras 6; filas `recent_count < 3` | 1.185 (train) | 0,59681 / 0,63431 / 0,61775 | Selección del respaldo: E1 |
| H_R0 | 22-11-2026 | E1 si `recent_count = 3`, R0 si < 3 | 1808 | 0,36567 | **No adoptado** (no seleccionado en train; R8 empeora) |
| H_P | 22-11-2026 | E1 si `recent_count = 3`, persistencia si < 3 | 1808 | 0,36669 | **No adoptado** (peor que E1 pooled) |
| E1 (final) | 22-11-2026 | Sin cambios respecto del Hito 2 | 1808 | 0,36636 | Candidato final y nominado al bonus |

## Contribuciones (informe final)

Igual que en los hitos anteriores, trabajamos en persona y las decisiones se tomaron en conjunto; cada uno puede explicarlas todas. Lideró la implementación/verificación:
- **Francisco Polo:** selección LORO en train y corrección de la descripción de la ventana (docstring + informe §2).
- **Milan Kurte:** predeclaración de la regla, confirmación por carrera y pooled en validación, bootstrap pareado e informe final.

## Uso de IA (informe final)

- **Herramienta:** Claude Code (Anthropic), sesión del 22-11-2026.
- **Prompt representativo:** *"Tengo que hacer mi última entrega para el ramo […]"* + el feedback del Hito 2 pegado.
- **Sugerencias adoptadas:** elegir el respaldo con LORO en train en vez de la validación (porque los cortes por `recent_count` ya se habían visto en el Hito 2) y commitear la predeclaración antes de correr; `final_respaldo.py` con bootstrap pareado; `predecir_e1.py` para el bonus; borradores de `INFORME_FINAL.md` y de esta sección.
- **Cómo se verificó:** (1) los CSV de `salidas_hito2/` regenerados son idénticos (md5) a los del Hito 2 y R0 = referencia Hito 1 (atol 1e-8); (2) `predecir_e1.py --autocheck` = E1 en 1.808 filas (máx. 1,4e-14 s) con el mismo `recent_count`; (3) el pooled ponderado por carrera se verifica con `assert` en el script; (4) `git log` confirma que `732988f` (predeclaración) es anterior a la ejecución.
- **Lo que no se delegó:** aceptar el resultado nulo de la revisión y mantener E1; participar en el bonus; la defensa oral.
