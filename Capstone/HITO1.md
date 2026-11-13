# Hito 1 · NextLap · Grupo 3

**Equipo:** Francisco Polo, Milan Kurte · **Curso:** IIT414W · **Fecha:** 12-11-2026
**Repositorio:** https://github.com/m1lvn/ai-workshop-labs (carpeta `Capstone/`) · commit: ver texto de entrega / release `Hito1`

## 1. Problema y valor de decisión

| Elemento | Definición |
|---|---|
| Objetivo | `next_lap_s`: duración de la vuelta t+1 del mismo piloto, en **segundos** |
| Momento de predicción | Al terminar la vuelta t del piloto (`end_time_s` de t). Solo se usa información observada hasta ese instante. |
| Lector / usuario | Ingeniero de carrera que monitorea el ritmo y la degradación de su piloto durante el stint. |
| Decisión informada | Si la vuelta siguiente esperada se aleja del ritmo reciente, decidir si **avisar al piloto** (gestionar neumáticos/ritmo) o **preparar una alerta** de degradación para el muro. |
| Lo que NO establece | No decide cuándo entrar a boxes ni cuántas posiciones gana una estrategia; eso requiere simular rivales, tráfico y tiempos de pit, fuera de este objetivo. |
| Límite de la población | `clean_pair` es una población **retrospectiva y condicional**: se filtra usando información de t+1 (p. ej. que t+1 no sea vuelta de pit, SC o borrada). Un MAE en estos pares **no** es evidencia de rendimiento en toda la carrera ni en vivo, donde no se sabe de antemano si t+1 será "limpia". |

## 2. Referencia reproducida (ejecución propia)

- **Datos:** `IIT414W_Capstone_NextLap_StudentData_v1` (paquete `base_NextLap/`, snapshots `race_2026_rXX_laps_v2.csv`, `source_manifest_v2.json`). SHA-256 registrados en `salidas_referencia/reference_run.json`.
- **Split:** train = rondas 1–7 (5.772 pares limpios); validación = rondas 8–9 (1.808 pares). `RANDOM_SEED = 414`. Test reservado: **no usado ni accedido**; sin acceso previo.
- **Features:** `current_lap_s, recent_mean_s, current_lap_number, current_tyre_life` (numéricas) + `current_compound, current_team` (categóricas). Ninguna columna `next_*` entra al modelo (assert en el script).
- **Fit/transform:** el `Pipeline` de `make_model('OLS')` (imputador + escalador + one-hot + OLS) se ajusta **solo con train** (`.fit(train[features], train[TARGET])`) y luego solo transforma validación. La mediana se calcula en train.
- **Comando:** `cd Capstone && ../.venv/bin/python probar_referencia_v1.py` (ver `README.md`). Entorno: numpy 2.0.2, pandas 2.3.1, scikit-learn 1.8.0.

| Modelo | Población | n | MAE (s) |
|---|---|---|---|
| Mediana de train | validación completa | 1808 | 11.376 |
| Persistencia (`current_lap_s`) | validación completa | 1808 | 0.409 |
| OLS referencia | validación completa | 1808 | **0.387** |
| Mediana / Persistencia / OLS | ronda 8 | 1066 | 11.716 / 0.401 / 0.374 |
| Mediana / Persistencia / OLS | ronda 9 | 742 | 10.888 / 0.422 / 0.406 |

Los tres modelos se evalúan sobre **las mismas 1.808 filas** (mismo `pair_id`, guardado en `salidas_referencia/validation_reference_predictions.csv`). Nuestra ejecución reproduce exactamente los valores del paquete del curso.

**Interpretación de una comparación:** OLS mejora a persistencia en solo ~0,023 s (≈5,5 %). La vuelta actual ya explica casi todo; la mediana global falla (~11 s) porque ignora la diferencia entre circuitos. Por lo tanto, cualquier feature nueva compite por una mejora pequeña y debe medirse sobre filas idénticas y por carrera, no solo en el total.

## 3. Hipótesis principal: historial de ritmo (variabilidad y tendencia)

| Elemento | Detalle |
|---|---|
| Cambio propuesto | Agregar a los 6 inputs de referencia: `recent_std_s` (desviación estándar de las últimas k vueltas) y `recent_slope_s` (pendiente lineal de tiempo de vuelta vs. número de vuelta en las últimas k vueltas), más la bandera `short_history`. |
| Mecanismo esperado | `recent_mean_s` resume el nivel pero no la **dirección** ni la **estabilidad**. Una pendiente positiva indica degradación en curso (t+1 probablemente más lenta que la media); una desviación alta indica ritmo inestable, donde conviene confiar menos en la última vuelta. |
| Fuente | Datos publicados: `base_NextLap/data/race_2026_rXX_laps_v2.csv` (`lap_time_s`, `lap_number`, `end_time_s`, `stint`, `driver_number`). No requiere fuente externa, así que no hace falta fallback externo. |
| Disponibilidad en t | Ventana que **incluye la vuelta t y anteriores**, agrupada por piloto/carrera/stint, construida sobre la **línea de tiempo original antes del filtro `clean_pair`** (mismo criterio que `build_pairs`, que ya usa `rolling(3)` para `recent_mean_s`). Se verificará que `max(end_time_s` de las vueltas usadas`) <= end_time_s(t)`. |
| Regla de historial corto / faltantes | Con menos de 2 vueltas válidas en la ventana, std y pendiente no existen (pendiente necesita ≥ 2; usaremos ≥ 3 para k=3): se imputan con la **mediana de train** (dentro del pipeline, ajustada solo con train) y `short_history = 1`. Ninguna fila se elimina; las vueltas no válidas ya observadas se tratan igual que en la referencia (no entran como historial). |

## 4. Plan de experimento y verificación

**Fijo en todas las comparaciones:** objetivo `next_lap_s`; métrica MAE en segundos; split rondas 1–7 / 8–9; las mismas 1.808 filas de validación (mismo conjunto de `pair_id`); familia de modelo OLS con el mismo pipeline de preprocesamiento ajustado solo en train; seed 414.

| ID | Modelo | Propósito |
|---|---|---|
| R0 | OLS referencia (6 inputs) | Línea base oficial |
| E1 | R0 + `recent_std_s` + `recent_slope_s` + `short_history` (k=3) | Extensión principal |
| A1 | R0 + `recent_slope_s` + `short_history` | Ablación: aporte de la tendencia sola |
| A2 | R0 + `recent_std_s` + `short_history` | Ablación: aporte de la variabilidad sola |
| A3 | R0 + `short_history` solamente | Control: separar el efecto de la bandera del de la información nueva |
| E2 | Como E1 con k=5 | Única variación de búsqueda |

**Búsqueda acotada:** solo k ∈ {3, 5} y las ablaciones anteriores (6 corridas en total). Todas se registran en `DECISION_LOG.md`, incluidas las que no mejoren. No se cambia de algoritmo para "probar"; un modelo no lineal, si se prueba, se reporta aparte y comparado con y sin las features.

**Selección vs. evaluación final:** validación (rondas 8–9) solo sirve para elegir entre E1/E2 y se reporta como evidencia de selección. El test reservado no se usa para elegir features, parámetros ni modelos.

**Chequeos escritos antes de implementar:**
1. *Tiempo:* para cada fila, la última `end_time_s` usada por las features ≤ `end_time_s` de t. Falla: alguna fila usa t+1.
2. *Fronteras:* ninguna ventana cruza piloto, carrera o stint (la primera vuelta de cada stint debe tener `short_history = 1`). Falla: std/pendiente definida en la primera vuelta de un stint.
3. *Filas:* el conjunto de `pair_id` de validación de E1 es idéntico al de R0 (1.808) y no hay predicciones NaN. Falla: filas perdidas o predicciones no finitas.
4. *Orden de construcción:* features calculadas sobre los snapshots completos y luego unidas por `pair_id` a los pares limpios. Falla: valores distintos a calcularlos después de filtrar.
5. *Robustez:* MAE por carrera de validación (ronda 8 n=1066, ronda 9 n=742) para R0 y E1.

**Qué apoya o contradice la hipótesis:** se apoya si E1 baja el MAE frente a R0 sobre las mismas filas **en ambas carreras de validación**, y si A1/A2 muestran que la mejora viene de la información nueva y no de la bandera (A3). Se contradice si la diferencia es ≈0 o negativa, o si aparece en una sola carrera. Un resultado negativo se reporta igual.

**Fuera de la comparación común:** cualquier análisis con todos los pares observados (`observed_pairs_train_validation_v1.csv`, no solo los limpios) se reporta por separado.

## 5. Trazabilidad y próximos pasos

Las contribuciones, el registro de IA, la revisión tras feedback y los responsables están en [`DECISION_LOG.md`](DECISION_LOG.md).

**Hacia el Hito 2 (19-11):** implementar las features y los chequeos 1–4 → correr R0/E1/A1–A3/E2 → MAE por carrera → errores contextuales y SHAP.
**Bloqueo conocido:** ninguno técnico. Riesgo: la mejora esperada es pequeña (OLS supera a persistencia por solo ~0,02 s), así que la diferencia podría ser del orden del ruido.
