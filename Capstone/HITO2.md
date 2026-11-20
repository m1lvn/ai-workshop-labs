# Hito 2 · NextLap · Grupo 3

**Equipo:** Francisco Polo, Milan Kurte · **Curso:** IIT414W · **Fecha:** 19-11-2026
**Repositorio y commit:** ver [`README.md`](README.md) · **Código:** [`hito2_experimento.py`](hito2_experimento.py) · **Salidas:** [`salidas_hito2/`](salidas_hito2/)

**Cambios en la hipótesis desde el Hito 1:** ninguno. Probamos el historial de ritmo planeado: `recent_std_s` (variabilidad) y `recent_slope_s` (tendencia) de las últimas k = 3 vueltas, con la bandera `short_history`. k = 3 se fijó como candidato antes de correr y k = 5 (E2) se reporta como prueba adicional.

## 0. Validez de la evaluación (C1)

| Aspecto | Qué hicimos | Evidencia |
|---|---|---|
| Split | Train: rondas 1–7 (5.772 pares). Validación: R8 (1.066) y R9 (742). Seed 414. Test reservado (R17): no está en el paquete, no se usó y no tuvimos acceso previo. | `run_hito2.json` → `checks.split` |
| Ajuste solo en train | `make_model('OLS', numeric=…)`. El imputador (mediana), el escalador, el one-hot y la regresión se ajustan con `.fit(tr[feats], tr[TARGET])`; en validación solo se aplica `predict`. | `hito2_experimento.py`, sección 3 |
| Disponibilidad en t | La ventana contiene las vueltas t−k+1 … t del mismo piloto, carrera y stint, armada sobre los snapshots crudos **antes** del filtro `clean_pair`. Solo entran al historial vueltas `current_clean` ya observadas (misma regla que `recent_mean_s` en `build_pairs`). No se usa ningún `next_*` ni `clean_pair`. | Chequeos 1, 1b y 2 |
| Faltantes / historial corto | std necesita ≥ 2 vueltas limpias en la ventana y la pendiente ≥ 3. Si faltan, el valor queda NaN, se imputa con la **mediana de train** dentro del pipeline y `short_history = 1`. No se elimina ninguna fila. | `feature_coverage.csv` |
| Cobertura (k = 3, validación) | Pendiente observada en 1.487 de 1.808 filas (82,3 %): R8 893/1.066 y R9 594/742. std observada en 1.660/1.808 (R8 984, R9 676). `short_history = 1` en 321 filas = 1.808 − 1.487, es decir, toda fila sin pendiente. De ellas, 148 tienen 1 vuelta limpia (std y pendiente imputadas) y 173 tienen 2 (solo pendiente imputada). | `feature_coverage.csv` |
| Identidad de filas | Las 6 corridas predicen las mismas 1.808 `pair_id`, sin duplicados ni NaN. El join es `validate='one_to_one'` con cobertura 100 %. Las predicciones R0 coinciden con las del Hito 1 (`atol 1e-8`). | `checks.check3_rows` |

**Chequeos definidos en el Hito 1 y resultado observado** (`salidas_hito2/run_hito2.json`):

| Chequeo | Resultado |
|---|---|
| 1. Tiempo: `max(end_time_s)` de las vueltas usadas ≤ `end_time_s(t)` | 0 violaciones en 9.849 pares (k = 3 y k = 5) ✅ |
| 1b. Agregado: alterar todas las vueltas > t (+50 s, borradas) no cambia las features de t | 0 diferencias en 200 `pair_id` (seed 414) ✅ |
| 2. Fronteras: en la primera vuelta de cada stint, std y pendiente son NaN y `short_history = 1` | 311 filas, 0 definidas ✅ |
| 3. Filas: mismas 1.808 `pair_id` y sin NaN | ✅ |
| 4. Orden de construcción (**revisado**, ver DECISION_LOG): `recent_mean_s` reconstruido desde los crudos = publicado | ✅. Además, calcular std **después** del filtro habría cambiado 621 de 7.580 filas. |
| 5. MAE por carrera | Sección 2 |

## 1. Comparación ejecutada y ablación (C2, C3)

| Versión | Modelo e inputs | n validación | MAE (s) | Salida / corrida |
|---|---|---|---|---|
| OLS referencia | OLS · 6 inputs publicados | 1808 | **0,38671** | R0 · `validation_predictions_hito2.csv:R0` (= `salidas_referencia/…:OLS_reference`) |
| Candidato | OLS · 6 inputs + `recent_std_s` + `recent_slope_s` + `short_history` (k = 3) | 1808 | **0,36636** | E1 · `validation_predictions_hito2.csv:E1` |
| Control emparejado | Candidato sin el cambio = OLS · 6 inputs | 1808 | **0,38671** | **Misma corrida R0** que la referencia: misma familia, mismo pipeline y mismas filas, reajustado en el script |

**Control − candidato = 0,38671 − 0,36636 = +0,0203 s** (≈ 5,3 %). Como la diferencia es positiva, el candidato tiene menor MAE en estas 1.808 filas.

Corridas adicionales (todas con OLS, el mismo pipeline y las mismas 1.808 filas; `metrics_all_runs.csv`):

| Corrida | Inputs extra sobre R0 | MAE total | R8 | R9 |
|---|---|---|---|---|
| A1 | pendiente + bandera | 0,38686 | 0,37117 | 0,40940 |
| A2 | std + bandera | **0,36567** | 0,35579 | 0,37988 |
| A3 | solo bandera | 0,38679 | 0,37117 | 0,40923 |
| E2 | std + pendiente + bandera, k = 5 | 0,37993 | 0,37151 | 0,39204 |

**Qué apoya el resultado:** se cumple el criterio que registramos en el Hito 1 (E1 < R0 en R8 **y** en R9). Las ablaciones muestran que la mejora viene de la **variabilidad** (`recent_std_s`). A2 consigue lo mismo que E1, mientras que la pendiente (A1) y la bandera sola (A3) no mejoran a R0. La parte de "tendencia" de la hipótesis **no** queda respaldada. Con k = 5 la mejora es menor.

**Límite:** la afirmación vale para OLS con k = 3, en dos carreras (R8 y R9) y dentro de la población retrospectiva `clean_pair`. Elegimos k y miramos las ablaciones usando la misma validación, así que la ganancia de 0,02 s es evidencia de selección, no una estimación final. No se probó en vivo ni en carreras con SC o vueltas de pit.

**Decisión:** **mantener** el cambio (E1) como candidato. No cambiamos a A2 aunque tenga 0,0007 s menos, porque esa diferencia se eligió en validación y es menor que el ruido entre carreras. Retirar la pendiente queda como siguiente chequeo.

## 2. Errores por contexto (C4)

| Carrera | n | MAE control R0 (s) | MAE candidato E1 (s) | Control − candidato (s) |
|---|---|---|---|---|
| R8 | 1066 | 0,37357 | 0,35604 | +0,01753 |
| R9 | 742 | 0,40558 | 0,38119 | +0,02439 |
| Pooled (ponderado por n) | 1808 | 0,38671 | 0,36636 | **+0,02034** |

Ponderación: (1066·0,01753 + 742·0,02439) / 1808 = 0,02034, que coincide con la diferencia total. El patrón **es consistente con el resultado total**: E1 mejora en las dos carreras, y algo más en R9, que es la carrera con mayor error base.

**Corte declarado: `short_history`** (k = 3; 1 = menos de 3 vueltas limpias en la ventana; `slice_short_history.csv`):

| Carrera | short_history | n | MAE R0 | MAE E1 | Control − candidato |
|---|---|---|---|---|---|
| R8 | 0 | 893 | 0,3709 | 0,3535 | +0,0174 |
| R8 | 1 | 173 | 0,3874 | 0,3692 | +0,0182 |
| R9 | 0 | 594 | 0,3975 | 0,3597 | +0,0379 |
| R9 | 1 | 148 | 0,4379 | 0,4676 | **−0,0297** |

**Caso inspeccionado: `2026-R9-23-L7`** (ALB, Gran Premio Británico, stint 2 con HARD, `tyre_life` 6). Lo elegimos por ser la fila con mayor |error E1 − error R0| (`case_inspection.json`, `case_context_laps.csv`).

| Observado `next_lap_s` | Pred. R0 | Error abs. R0 | Pred. E1 | Error abs. E1 |
|---|---|---|---|---|
| 97,882 | 102,034 | \|97,882 − 102,034\| = **4,152** | 99,227 | \|97,882 − 99,227\| = **1,345** |

Las vueltas 4–6 fueron 96,46, 96,30 y 98,07, y la vuelta t = 7 fue **105,13**, un valor atípico con bandera verde, sin pit y no borrado. R0 traslada buena parte de esa vuelta lenta a t+1. E1 ve una std alta (4,67 s) y baja la predicción unos 2,8 s. Aun así queda 1,3 s por encima del valor real, porque la vuelta atípica sigue dentro de `recent_mean_s`.

**Diagnóstico:** la std ayuda cuando ya hay historial, pero **en R9 con historial corto (n = 148) E1 empeora 0,030 s**. En esas 148 filas la pendiente siempre se imputa con la mediana de train. La std solo se imputa en 66 (1 vuelta limpia en la ventana); en las otras 82 se calcula con solo 2 vueltas. E1 empeora en los dos grupos: −0,040 s con n = 66 y −0,022 s con n = 82. Por eso la imputación de la std no basta para explicar el problema. Una std de 2 vueltas es inestable, y la bandera (coeficiente −0,095 s, ajustado en train) podría no trasladarse bien a R9. Esto es una hipótesis, no algo verificado. En R8 los dos grupos mejoran (+0,019 s con n = 82 y +0,017 s con n = 91). Además, el caso muestra que una sola vuelta atípica en t todavía contamina `recent_mean_s`.

**Siguiente chequeo:** con los mismos 1.808 `pair_id`, comparar dos variantes en las filas `short_history = 1`, separadas por carrera:
(a) usar la predicción de R0 como respaldo cuando `short_history = 1`;
(b) reemplazar `recent_mean_s` y std por versiones robustas (mediana o MAD de la ventana).
Se apoya si R9 con `short_history = 1` deja de empeorar sin perder lo ganado en `short_history = 0`.

## 3. Interpretación SHAP (C5, C6)

**Modelo explicado:** E1, el candidato. Lo retuvimos porque la ablación lo favorece en ambas carreras. **Explainer:** `shap.LinearExplainer` (interventional, masker `Independent`) sobre la entrada ya transformada por el pipeline. **Background:** 500 filas de **train** (rondas 1–7) muestreadas con seed 414. Las contribuciones están en **segundos**. Las columnas one-hot de `current_compound` y `current_team` se **suman** para volver al input original (mapeo en `shap_encoded_mapping.csv`).

### Local: `2026-R9-23-L7` (`shap_local_summary.json`, `shap_local_contributions.csv`)

| Input | Valor | Contribución SHAP (s) |
|---|---|---|
| `recent_mean_s` | 99,832 | +9,427 |
| `current_lap_s` | 105,128 | +4,922 |
| `recent_std_s` | 4,671 | **−2,383** |
| `recent_slope_s` | 4,414 | +0,531 |
| `short_history` | 0 | +0,056 |
| `current_compound` | HARD | +0,039 |
| `current_lap_number` | 7 | −0,034 |
| `current_team` | Williams | −0,030 |
| `current_tyre_life` | 6 | −0,014 |
| **Suma** | | **+12,514** |

Base 86,713 + 12,514 = **99,227 s**, igual a la predicción de E1 (diferencia 0,0 s; tolerancia declarada 1e-6 s; el script verifica las 1.808 filas con un error máximo < 1e-6).

**Lectura:** la base es la predicción media sobre el background de train. `recent_mean_s` y `current_lap_s` suben la predicción en +9,4 y +4,9 s porque Silverstone es más lenta que el promedio de las pistas de train y porque la vuelta t fue muy lenta. `recent_std_s` **baja** la predicción en 2,38 s respecto de la base: con ritmo inestable, el modelo le da menos peso al nivel reciente. Es una asociación del modelo, no un efecto causal. El error se calcula aparte: |97,882 − 99,227| = **1,345 s**.

### Global (`shap_global_mean_abs.csv`, `shap_global_bar.png`)

**Muestra:** las 1.808 filas de validación (R8 + R9). **Agregación:** para cada input original (one-hot sumado por fila), el promedio sobre las filas de |SHAP|, en segundos.

| Input | Media \|SHAP\| (s) |
|---|---|
| `recent_mean_s` | 8,532 |
| `current_lap_s` | 3,155 |
| `recent_std_s` | 0,154 |
| `short_history` | 0,078 |
| `current_team` | 0,063 |
| `current_compound` | 0,028 |
| `current_lap_number` | 0,024 |
| `recent_slope_s` | 0,023 |
| `current_tyre_life` | 0,009 |

**Qué sugiere:** casi toda la variación de la predicción respecto de la base viene del nivel de ritmo (`recent_mean_s` y `current_lap_s`), que en gran parte refleja la diferencia de circuito entre R8/R9 y el background de train. Entre los inputs nuevos, `recent_std_s` es el que más mueve la predicción y la pendiente apenas aporta. Esto coincide con la ablación (A2 ≈ E1 y A1 ≈ R0), aunque SHAP por sí solo no prueba que el error baje.

**Alcance:** describe E1 solo en estas 1.808 filas limpias de dos carreras y con este background. La magnitud de `recent_mean_s` depende de la distancia entre el nivel de cada pista y el background (es 10,0 s en R8 y 6,4 s en R9, `shap_global_by_round.csv`), así que no se generaliza como "importancia" a otras pistas. La media firmada no indica una dirección universal.

## 4. Reproducibilidad

Ver [`README.md`](README.md): comando, entorno, datos (SHA-256 en `run_hito2.json`) y mapa del código a las salidas.

## 5. Explicación individual

> Cada integrante escribe su párrafo con sus propias palabras (≈1 minuto de lectura): una decisión en la que contribuyó, el resultado o chequeo que la respalda (con archivo y número), una limitación o siguiente chequeo, y el uso de IA y cómo lo verificó.

**Francisco Polo:**

Con Milan decidimos, discutiéndolo juntos, construir la ventana de historial (`recent_std_s`, `recent_slope_s`, `short_history`) sobre la línea de tiempo original de cada piloto, carrera y stint, **antes** de aplicar el filtro `clean_pair`. Ese filtro usa información de t+1: si la ventana se arma después, el historial de una fila depende de cómo resultó la vuelta siguiente, cosa que al final de t todavía no se sabe. El Chequeo 4 en `salidas_hito2/run_hito2.json` lo respalda: calcular la std después del filtro habría cambiado 621 de 7.580 filas. Además, el `recent_mean_s` reconstruido desde los snapshots coincide con el publicado, y el Chequeo 1b confirma que alterar las vueltas posteriores a t no cambia ninguna feature (0 diferencias en 200 `pair_id`). **Limitación:** la ventana sigue incluyendo vueltas atípicas con bandera verde, como la vuelta 7 de `2026-R9-23-L7` (105,1 s). Como siguiente chequeo, probaría versiones robustas (mediana o MAD) de la ventana. **IA:** Claude Code propuso el código de la ventana y el Chequeo 1b. Lo verifiqué revisando que los chequeos 1, 1b, 2 y 4 dieran `passed: true` y comparando las vueltas del caso en `case_context_laps.csv`.

**Milan Kurte:**

Con Francisco decidimos, discutiéndolo juntos, mantener E1 como candidato aunque A2 (solo std + bandera) tuviera un MAE un poco menor: 0,36567 contra 0,36636 s en `salidas_hito2/metrics_all_runs.csv`, una diferencia de apenas 0,0007 s. Habíamos fijado E1 como candidato antes de correr. Cambiarlo por A2 sería elegir mirando la misma validación con la que lo evaluamos. Además, esa diferencia es unas diez veces menor que la variación de la mejora de E1 entre carreras (+0,0175 s en R8 y +0,0244 s en R9). Lo que sí aprendimos de A2 y A1 es que la mejora viene de la std y no de la pendiente. **Limitación:** E1 conserva un input (`recent_slope_s`) que no demostró aporte. Como siguiente chequeo, compararía E1 y A2 con validación cruzada dejando una carrera fuera dentro de R1–R7, sin tocar R8–R9 ni el test. **IA:** Claude Code propuso las ablaciones y redactó un borrador. Lo verifiqué recalculando las diferencias desde `metrics_all_runs.csv` y `race_comparison.csv`.
