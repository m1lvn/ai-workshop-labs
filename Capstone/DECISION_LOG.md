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
