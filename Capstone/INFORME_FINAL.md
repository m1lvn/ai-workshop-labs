# Informe final · NextLap · Grupo 3

**Equipo:** Grupo 3 · Francisco Polo y Milan Kurte · IIT414W AI Workshop · 22-11-2026
**Repositorio:** https://github.com/m1lvn/ai-workshop-labs (carpeta `Capstone/`)
**Commit exacto:** ver portada del PDF y `Capstone/README.md` (un commit no puede contener su propio SHA)

Rutas relativas a la raíz del repositorio. Todas las cifras salen de archivos en `Capstone/salidas_hito2/` y `Capstone/salidas_final/` del commit indicado.

## 1. Recomendación y uso

**Qué predice y cuándo.** El modelo predice `next_lap_s`, el tiempo de la vuelta t+1, apenas termina la vuelta t, con datos ya observados hasta `end_time_s(t)`. **Decisión que informa:** un ingeniero de carrera puede preparar un aviso de degradación o de ritmo para el piloto. El modelo no decide paradas en boxes.

**Decisión: mantenemos el cambio probado.** Al OLS de referencia le agregamos la variabilidad (`recent_std_s`), la pendiente (`recent_slope_s`) y la bandera `short_history`, calculadas sobre una ventana de hasta tres vueltas consecutivas. Ese candidato es E1. En las mismas 1.808 filas de validación (R8–R9), E1 baja el MAE de **0,38671 a 0,36636 s**. La diferencia control − candidato es **+0,0203 s (20,3 ms; 5,3 %)**, con IC95 bootstrap pareado de [+11,8; +29,6] ms. La mejora aparece en las dos carreras.

**Revisión tras el feedback.** Probamos con una regla predeclarada si conviene un respaldo (R0 o persistencia) cuando `recent_count < 3`. **Retuvimos E1 sin respaldo**, porque la selección hecha solo con train (R1–R7) favorece a E1 (§4).

**Limitación.** En R9 con historial corto (n = 148), E1 sigue siendo 29,7 ms peor que R0. Además, la ganancia de 20 ms es evidencia de selección en dos carreras de validación, dentro de la población retrospectiva `clean_pair`. No es una estimación final.

## 2. Experimento y comparación válida

**Qué se probó y qué está disponible al terminar la vuelta t.** Para cada piloto, carrera y stint usamos una **ventana de hasta tres vueltas consecutivas (t−2, t−1, t)**. Las vueltas inválidas dentro de la ventana se **excluyen** y no se reemplazan por vueltas más antiguas. Una vuelta es inválida si no es `current_clean`: vuelta 1, pit in/out, borrada, no precisa o con bandera distinta de verde. Por eso la ventana puede tener 1, 2 o 3 vueltas válidas, y ese número es `recent_count`. Sobre las vueltas válidas calculamos:

- `recent_std_s`: desviación estándar, que requiere ≥ 2 vueltas válidas.
- `recent_slope_s`: pendiente en s/vuelta, que requiere ≥ 3 vueltas válidas.
- `short_history`: vale 1 si `recent_count < 3`.

En el Hito 2 escribimos "las últimas 3 vueltas limpias", y esa frase era imprecisa. Esta es la descripción correcta, pedida en el feedback, y quedó también en el docstring de `history_features` (`Capstone/hito2_experimento.py`).

**Línea de tiempo y faltantes.**
- La ventana se arma sobre los snapshots crudos (`Capstone/base_NextLap/data/race_2026_r0X_laps_v2.csv`, con SHA-256 verificado contra `source_manifest_v2.json`), **antes** del filtro `clean_pair`. Es la misma regla que usa `recent_mean_s` en `build_pairs`.
- **La última observación usada es la propia vuelta t.** Chequeo 1: `max(end_time_s)` de las vueltas usadas ≤ `end_time_s(t)`, con 0 violaciones en 9.849 pares.
- Chequeo 1b: alterar todas las vueltas posteriores a t no cambia las features (0 diferencias en 200 `pair_id`, seed 414).
- Si falta historial, std o pendiente quedan en NaN y se **imputan con la mediana de train** dentro del pipeline, con `short_history = 1`. No se elimina ninguna fila.
- Cobertura en validación: pendiente observada en 1.487 de 1.808 filas y std en 1.660 (`Capstone/salidas_hito2/feature_coverage.csv`).
- Chequeo 6: nuestro conteo de vueltas válidas coincide con `recent_count` publicado en las 1.808 filas de validación y en las 5.772 de train (`Capstone/salidas_final/run_final.json → checks`).

**Población de evaluación.** El filtro retrospectivo `clean_pair` deja solo los pares en que t **y** t+1 son vueltas limpias, del mismo stint y con el mismo compuesto. Ese filtro usa información de t+1, así que en vivo no se sabe si un par pertenece a la población. Por eso el filtro, el objetivo y los campos `next_*` **nunca** son predictores: el script lo verifica con un `assert` (`Capstone/hito2_experimento.py`, §3). Los resultados valen para vueltas limpias y no para vueltas con SC, pit o tráfico anómalo en t+1.

**Split y ajuste.**
- Train: R1–R7 (5.772 pares). Validación de desarrollo: R8 (1.066) y R9 (742).
- Imputación, escalado, one-hot y regresión se ajustan con `make_model('OLS', …).fit(train)`. En validación solo se llama a `predict`.
- Seed 414. El test reservado (R17) no está en el paquete y no lo usamos (`run_hito2.json → checks.split`).

**Filas comunes.** Todas las corridas predicen las mismas 1.808 `pair_id` únicas que la referencia del Hito 1, sin duplicados ni NaN. El join se hace con `validate='one_to_one'` y cobertura del 100 %. Las predicciones de R0 son idénticas a las del Hito 1 con `atol` 1e-8 (`run_hito2.json → checks.check3_rows`; `run_final.json → checks.validation_ids`).

| Corrida | Modelo, inputs y ajustes | n común | MAE (s) | Salida guardada |
| --- | --- | ---: | ---: | --- |
| OLS de referencia, seis inputs | OLS · `current_lap_s`, `recent_mean_s`, `current_lap_number`, `current_tyre_life`, `current_compound`, `current_team` | 1.808 | 0,38671 | R0 · columna `R0` de `Capstone/salidas_hito2/validation_predictions_hito2.csv` |
| Candidato | OLS · 6 inputs + `recent_std_s` + `recent_slope_s` + `short_history` (ventana de hasta 3 vueltas) | 1.808 | 0,36636 | E1 · columna `E1` del mismo archivo |
| Control emparejado sin el cambio | **Misma corrida que la referencia (R0)**: misma familia, mismo pipeline, mismo train y mismas filas, reajustada en el mismo script. Solo cambian los 3 inputs nuevos | 1.808 | 0,38671 | R0 (misma corrida) |

**Control − candidato = 0,38671 − 0,36636 = +0,02034 s.** El valor es positivo, así que el candidato se equivoca 20,3 ms menos por vuelta en promedio en estas 1.808 filas. El IC95 bootstrap pareado (2.000 remuestreos de `pair_id`, seed 414) es [+0,0118; +0,0296] s (`run_final.json → validation.bootstrap_95ci_s.R0_minus_E1`). **Alcance:** R8–R9, población `clean_pair`, OLS. Como se usó la misma validación para mirar k y las ablaciones, es evidencia de selección.

**Ensayos, incluidos los que no funcionaron** (`Capstone/salidas_hito2/metrics_all_runs.csv`). Todos usan OLS y las mismas filas.

| Corrida | Inputs sobre R0 | MAE (s) | Resultado |
| --- | --- | ---: | --- |
| A1 | pendiente + bandera | 0,38686 | Sin mejora: la tendencia no aporta |
| A2 | std + bandera | 0,36567 | ≈ E1: la ganancia viene de la std |
| A3 | solo bandera | 0,38679 | Sin mejora: la bandera sola no explica la ganancia |
| E2 | como E1, ventana de 5 | 0,37993 | Peor que E1: se descartó k = 5 |
| H_R0 / H_P | E1, con respaldo R0 / persistencia si `recent_count < 3` | 0,36567 / 0,36669 | No seleccionados por la regla predeclarada (§4) |

**Decisión a partir de la evidencia.** Mantenemos E1 por tres razones:
1. El contraste controlado aísla el cambio. R0 y E1 solo difieren en los tres inputs nuevos y la diferencia es positiva en las dos carreras, que era el criterio registrado en HITO1 §4.
2. El IC95 no incluye el cero.
3. Las ablaciones indican qué parte del cambio produce la ganancia: es la variabilidad, porque A2 ≈ E1, mientras que A1 ≈ R0 y A3 ≈ R0.

No cambiamos a A2, aunque tiene 0,7 ms menos. Esa diferencia se observó en la misma validación y es mucho menor que la diferencia de la ganancia entre carreras (6,9 ms).

## 3. Errores por contexto e interpretación del modelo

Fuente: `Capstone/salidas_hito2/race_comparison.csv` y `Capstone/salidas_final/validation_hybrid_by_race.csv`.

| Contexto de validación | n común | MAE control R0 (s) | MAE candidato E1 (s) | Control − candidato (s) |
| --- | ---: | ---: | ---: | ---: |
| R8 | 1.066 | 0,37357 | 0,35604 | +0,01753 |
| R9 | 742 | 0,40558 | 0,38119 | +0,02439 |
| Pooled | 1.808 | 0,38671 | 0,36636 | +0,02034 |

**Relación con el pooled.** Ponderado por filas: (1.066 × 0,01753 + 742 × 0,02439) / 1.808 = 0,02034 s, igual a la diferencia total. El script lo verifica con un `assert` (`Capstone/final_respaldo.py`). E1 mejora en las dos carreras, así que el resultado pooled no esconde una carrera que empeore. La mejora es mayor en R9, la carrera con mayor error de base.

**Dentro de R9 hay un subgrupo que falla** (`Capstone/salidas_final/validation_short_history_R0_vs_persistence.csv`). Con `recent_count < 3`, E1 es peor que R0: 0,46755 contra 0,43788 s, es decir −29,7 ms con n = 148. Con `recent_count = 1`, R0 ya es peor que la persistencia (0,40219 contra 0,39041 s, n = 66). En R8 el mismo subgrupo mejora (+18,2 ms, n = 173). La ganancia pooled se apoya sobre todo en las 1.487 filas con ventana completa.

**Caso inspeccionado: `2026-R9-23-L7`.** Es ALB en el GP Británico, stint 2 con HARD y `tyre_life` 6. Lo elegimos con una regla fijada antes de mirarlo: la fila con mayor |error E1 − error R0| (`Capstone/salidas_hito2/case_inspection.json`, `case_context_laps.csv`).

| Observado `next_lap_s` | Predicción R0 | Error abs. R0 | Predicción E1 | Error abs. E1 |
| ---: | ---: | ---: | ---: | ---: |
| 97,882 | 102,034 | \|97,882 − 102,034\| = 4,152 | 99,227 | \|97,882 − 99,227\| = 1,345 |

La ventana contiene las vueltas 5–7 (96,30, 98,07 y **105,13 s**). La vuelta t = 7 es atípica aunque es válida: bandera verde, sin pit y no borrada. R0 traslada esa vuelta lenta a t+1. E1 ve una std alta (4,67 s) y baja la predicción, pero igual queda 1,3 s arriba porque la vuelta atípica sigue dentro de `recent_mean_s`. **Qué motiva revisar:** una versión robusta de la ventana (mediana/MAD). **Qué deja incierto:** con un solo caso no sabemos con qué frecuencia una vuelta atípica en t precede a una vuelta normal.

**Alcance y siguiente chequeo.** El fallo observado en R9 con historial corto no aparece en train. En el leave-one-round-out de R1–R7, E1 gana en las filas con `recent_count < 3` en 5 de 7 rondas (`Capstone/salidas_final/loro_train_short_history.csv`). Por eso acotamos la afirmación así: la ganancia se sostiene con ventana completa, y con historial corto depende de la pista. **Siguiente chequeo concreto:**
1. Predeclarar en el DECISION_LOG una variante `recent_median_s` (mediana de la ventana) junto con la regla de selección.
2. Seleccionarla con el mismo LORO en train.
3. Confirmarla en los mismos 1.808 `pair_id`, por carrera y `recent_count`.

Se apoya si el caso `2026-R9-23-L7` y el subgrupo R9 con `recent_count < 3` mejoran sin perder ganancia con `recent_count = 3`.

**SHAP local** (`Capstone/salidas_hito2/shap_local_summary.json`, `shap_local_contributions.csv`).
- **Modelo:** E1, el pipeline OLS ajustado en R1–R7.
- **Fila:** `2026-R9-23-L7`.
- **Explainer:** `shap.LinearExplainer` (interventional, masker `Independent`) sobre la entrada transformada por el pipeline.
- **Background:** 500 filas de train, seed 414.
- Las columnas one-hot se suman al input original.

| Input | Valor | Contribución (s) |
| --- | --- | ---: |
| `recent_mean_s` | 99,832 | +9,427 |
| `current_lap_s` | 105,128 | +4,922 |
| `recent_std_s` | 4,671 | −2,383 |
| `recent_slope_s` | 4,414 | +0,531 |
| `short_history` | 0 | +0,056 |
| `current_compound` | HARD | +0,039 |
| `current_lap_number` | 7 | −0,034 |
| `current_team` | Williams | −0,030 |
| `current_tyre_life` | 6 | −0,014 |
| **Suma** | | **+12,514** |

**Reconstrucción:** base 86,713 + 12,514 = **99,227 s**, igual a la predicción de E1 (diferencia 0,0 s). El script verifica la misma igualdad en las 1.808 filas, con error máximo < 1e-6 s.

**Una contribución en segundos:** `recent_std_s` = 4,67 s **baja la predicción en 2,38 s** respecto de la base. Con un ritmo inestable, el modelo le da menos peso al nivel reciente. Es una asociación del modelo, no un efecto causal.

**El error observado es otra cosa:** |97,882 − 99,227| = **1,345 s**. SHAP explica por qué el modelo predijo 99,227, no por qué la vuelta real fue 97,882.

**SHAP global** (`Capstone/salidas_hito2/shap_global_mean_abs.csv`, `shap_global_bar.png`, `shap_global_by_round.csv`).
- **Muestra:** las 1.808 filas de validación (R8 + R9).
- **Explainer y background:** los mismos del caso local.
- **Agregación:** media de |SHAP| por input original, en segundos.

Resultados:
- `recent_mean_s` 8,53 s y `current_lap_s` 3,15 s dominan. En gran parte reflejan la distancia entre el nivel de cada pista y el background de train: 10,0 s en R8 y 6,4 s en R9.
- Entre los inputs nuevos, `recent_std_s` mueve más la predicción (0,154 s) que `recent_slope_s` (0,023 s).

**Relación con el rendimiento:** SHAP mide cuánto mueve un input la predicción, no cuánto reduce el error. La ablación sí lo mide: quitar la pendiente no cambia el MAE (A2 0,36567 ≈ E1 0,36636), y quitar la std lo devuelve al nivel de R0 (A1 0,38686). Las dos fuentes coinciden en que la std es lo que aporta. El resumen vale solo para E1, estas dos carreras y este background.

## 4. Revisión tras el feedback

| Fuente y prioridad | Cambio o decisión justificada de mantener | Chequeo, resultado y salida |
| --- | --- | --- |
| **Hito 2 (instructor):** historial corto en R9. E1 suma 29,7 ms de MAE en 148 filas, y con una sola vuelta limpia (66 filas) el OLS ya pierde contra la persistencia. Se pidió predeclarar un respaldo para `recent_count < 3`, comparar R0 y persistencia por carrera y pooled antes de congelar, y corregir la descripción de la ventana. **Demo Day (20-11):** el jurado no indicó una prioridad, así que la misma revisión cubre ambas fuentes. | (1) **Predeclaramos la regla** en `Capstone/DECISION_LOG.md` (commit `732988f`, 22-11 12:25 −03). Las opciones son E1 sin respaldo, R0 o persistencia; se elige la de menor MAE en train con LORO (R1–R7), sin usar validación; se congela solo si el MAE pooled de validación no empeora frente a E1. (2) **Decisión: mantener E1 sin respaldo**, porque la regla seleccionó E1. (3) **Corregimos la descripción** de la ventana (§2). | **Train LORO**, filas con `recent_count < 3` (n = 1.185): E1 0,59681, persistencia 0,61775 y R0 0,63431 s. E1 gana 5 de 7 rondas, la persistencia 2 y R0 ninguna (`salidas_final/loro_train_short_history.csv`). **Validación**, mismas 321 filas cortas: R0 contra persistencia en R8 0,38735 vs 0,39849 (n = 173) y en R9 0,43788 vs 0,43729 (n = 148); pooled 0,41065 vs 0,41638 (`validation_short_history_R0_vs_persistence.csv`). **Pooled en las 1.808 filas:** E1 0,36636; con respaldo R0, 0,36567 (+0,7 ms, IC95 [−2,2; +3,4] ms); con respaldo persistencia, 0,36669 (−0,3 ms, IC95 [−4,3; +3,4] ms) (`validation_hybrid_by_race.csv`, `run_final.json`). |

**Por qué la evidencia justifica mantener E1.** El problema que señaló el feedback se confirma: en R9 con historial corto, R0 o la persistencia serían mejores que E1. Pero el mismo respaldo **empeora R8**: con R0, el MAE de R8 pasa de 0,35604 a 0,35899. En train, donde la elección no está sesgada por la validación, E1 es la mejor opción con historial corto. La única alternativa que mejora el pooled de validación (respaldo R0, +0,7 ms) tiene un IC95 que incluye el cero, y elegirla sería seleccionar mirando R8–R9 por segunda vez. Por eso el fallo de R9 queda declarado como límite (§3) y no como una regla especial por pista.

**Verificación de que la regla fue previa.** El commit `732988f` (12:25:15) es anterior a la primera ejecución de `final_respaldo.py`. Al regenerar R0 y E1 desde el script del Hito 2, los CSV de `salidas_hito2/` salieron idénticos byte a byte (md5).

## 5. Reproducir el resultado

| Qué necesita el revisor | Ubicación o instrucción |
| --- | --- |
| Acceso al repositorio y commit congelado | https://github.com/m1lvn/ai-workshop-labs (público). Commit en la portada del PDF y en `Capstone/README.md` |
| Versión de datos y manifiesto | Paquete del curso `IIT414W_Capstone_NextLap_StudentData_v1` incluido en `Capstone/base_NextLap/`. `load_snapshots` verifica el SHA-256 de cada snapshot contra `data/source_manifest_v2.json`. Los hashes de los CSV limpios están en `salidas_hito2/run_hito2.json → sha256`. Sin fuentes externas |
| Entorno y seed | Python 3.12. Versiones fijadas en `Capstone/requirements.txt` (numpy 2.5.5, pandas 2.3.1, scikit-learn 1.9.1, shap 0.54.1, matplotlib 3.10.3). `RANDOM_SEED = 414` (background SHAP, chequeo 1b y bootstrap) |
| Comando exacto | Desde la raíz del repo: `python3 -m venv .venv && .venv/bin/pip install -r Capstone/requirements.txt && cd Capstone && ../.venv/bin/python final_respaldo.py && ../.venv/bin/python predecir_e1.py --autocheck` (unos 15 s) |
| Mapa de código y salidas | `final_respaldo.py` → importa `hito2_experimento.py` (R0, E1, A1–A3, E2, cortes, caso, SHAP → `salidas_hito2/`) y aplica la revisión (`salidas_final/`). Comparación: `salidas_hito2/comparison_table.csv` y `metrics_all_runs.csv`. Por carrera: `race_comparison.csv` y `salidas_final/validation_hybrid_by_race.csv`. Caso: `case_inspection.json`. SHAP: `shap_local_*.json/csv` y `shap_global_*` |
| Registro de decisiones e IA | `Capstone/DECISION_LOG.md` (Hito 1, Hito 2 e Informe final: registro de corridas, predeclaración, contribuciones y uso de IA) |

**Ensayos no exitosos y ajustes posteriores.**
- A1, A3 y E2 no mejoraron (§2).
- La regla de construcción del chequeo 4 se corrigió después de implementarla (Hito 2).
- Después del feedback, los respaldos H_R0 y H_P **no** se adoptaron (§4).
- No hubo cambios en E1 después de ver la validación.

**Contribuciones.** Trabajamos juntos, en persona. Las decisiones se discutieron y tomaron entre los dos, y cada uno puede explicarlas todas. Lo que se repartió fue quién lideró cada implementación o chequeo:
- **Francisco Polo:** en el Hito 2, la ventana desde los snapshots crudos, los chequeos 1, 1b, 2 y 4 y SHAP. En la revisión final, la selección LORO en train y la corrección de la descripción de la ventana. **Decisión evidenciada:** armar la ventana antes de `clean_pair`. Calcularla después habría cambiado 621 de 7.580 filas (`run_hito2.json → check4`), y el conteo reconstruido coincide con `recent_count` en train y validación.
- **Milan Kurte:** en el Hito 2, las corridas R0/E1/A1–A3/E2, el MAE por carrera, los cortes y el caso. En la revisión final, la predeclaración, la confirmación por carrera y pooled, el bootstrap y el informe. **Decisión evidenciada:** mantener E1 frente a A2 y frente a los respaldos. Las diferencias de 0,7 ms vienen de la validación y su IC95 incluye el cero (`run_final.json → bootstrap_95ci_s`).

**Uso de IA.** Usamos Claude Code (Anthropic) en sesiones del 12-11, 19-11 y 22-11.
- **Sugerencias adoptadas el 22-11:**
  - Elegir el respaldo con LORO en train en vez de usar la validación, porque los cortes por `recent_count` ya se habían visto.
  - Commitear la predeclaración antes de ejecutar.
  - El script `final_respaldo.py` y el bootstrap pareado.
  - El predictor del bonus `predecir_e1.py`.
  - El borrador de este informe.
- **Cómo se verificó:**
  1. R0 y E1 regenerados con CSV idénticos (md5) a los del Hito 2, y R0 igual a la referencia del Hito 1 (`atol` 1e-8).
  2. `predecir_e1.py --autocheck` reproduce E1 en las 1.808 filas con diferencia máxima de 1,4e-14 s y el mismo `recent_count` (`salidas_final/bonus_autocheck.json`).
  3. El pooled ponderado por carrera se recalculó y se verificó con un `assert`.
  4. El orden predeclaración → ejecución se comprobó con el historial de git.
- **Qué no se delegó:** la decisión de aceptar el resultado nulo de la revisión y mantener E1, la elección de participar en el bonus y la defensa oral.
- El detalle por hito está en `Capstone/DECISION_LOG.md`.

### Nominación al bonus

- **Candidato nominado:** **E1**, en el commit indicado en la portada. Es OLS con los 6 inputs + `recent_std_s` + `recent_slope_s` + `short_history` (ventana de hasta 3 vueltas consecutivas), entrenado solo con R1–R7.
- **Comando**, desde `Capstone/`: `../.venv/bin/python predecir_e1.py --requests SOLICITUDES.csv --history HISTORIAL.csv --out PREDICCIONES.csv`
- **Inputs requeridos:**
  - Las solicitudes del contrato: `pair_id`, `season`, `round`, `driver_number`, `stint`, `end_time_s` y los 6 inputs de referencia.
  - Una vista cronológica del historial con el esquema de los snapshots publicados.
  - Para cada solicitud, el script usa solo vueltas del mismo piloto, carrera y stint con `end_time_s ≤ end_time_s(t)`.
- **Respaldo:** si la vuelta t no está en el historial, std y pendiente quedan en NaN, se imputan con la mediana de train y se asigna `short_history = 1`. La salida informa cuántas filas usaron el respaldo. Nunca se descartan filas y cada `pair_id` recibe una predicción finita.
- **Autochequeo:** con el contrato de entrada sobre R8–R9, reproduce E1 (MAE 0,36636 s, 0 respaldos) (`salidas_final/bonus_autocheck.json`).
- **Acceso previo:** declaramos que no tuvimos acceso a datos de evaluación reservados (R17 ni otros). La validación R8–R9 se usó para seleccionar y se reporta como evidencia de selección.
