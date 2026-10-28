# Common AI recommendation audit

Respond in at most five short lines to the recommendation quoted in the brief.
Accept/reject, methodological reason, and a precise checkable cell/function/output in this repository:

**Reject.** Once 2026 results choose the forest setting and the alert threshold, 2026 becomes part of model selection, and its score is optimistically biased.
Independence depends on what data were used for *any* decision, not on when training ends; reporting that score as a final test hides the selection.
Our protocol fixes selection to development only: `lab03_support_v3.py`, `load_learning` raises "Temporal partition contract failed" unless the data are train 2018–2021 plus 2022 rounds ≤ 11, and `evaluate_scores` calls `choose_threshold(dev_scores, dev, budget=BUDGET)`.
The run records this as `"threshold_selection": "dev only; reused unchanged on train"` in `outputs/run_manifest_v3.json`; `data/manifest_lab03_v3.json` lists 2026 under `"excluded"`.
We did not obtain or run 2026 data. A valid test would freeze our candidate and threshold first, then score untouched races once.

## Truthful use / no-use record

Tool and use, or “No AI used for this lab”:
Claude Code (CLI, model Claude Opus 5.5), working in this repository. It read the brief, rubric and supplied code. It created the `.venv` and ran the notebook. It drafted the notebook answer cells (sections 1, 2, 4 and the three error entries), `experiment_spec.md`, `memo.md`, the README run section and this file. It also added the section-5 query cells. We reviewed each step and approved it before the next one.

If used, one actual suggestion (quote or faithful summary):
After an export, development_predictions_v3.csv showed 937 alerts while comparison_v3.csv showed 938. Claude traced this to one window scored exactly at the threshold (`2022-05-22:63:11:4711.281000`): the forest's multi-threaded `predict_proba` moved it by about 1e-16. It suggested adding `joblib.parallel_config(backend='sequential')` to the setup cell.

What we accepted/rejected:
We accepted the change because it changes no model parameter. We did not accept that suggestion's correctness on trust. We also rejected part of Claude's own pre-run expectation after the run: it predicted "140 ± 10 entries, no clear improvement" and the candidate caught 159. We kept that expectation unchanged in `experiment_spec.md` and explained the miss in section 4.

Exact check performed and repository evidence:
1. With the setting, the five base systems still reproduce the supplied counts exactly.
2. Two consecutive full notebook runs gave identical `generated_sha256` values in `outputs/run_manifest_v3.json`.
3. Alerts, TP and caught entries in `outputs/development_predictions_v3.csv` and `outputs/event_errors_v3.csv` agree with the candidate's dev row in `outputs/comparison_v3.csv` (938 alerts, 376 TP, 159/370 entries).

The setting is in the notebook's setup cell (`setup-audit`) and documented in `README.md`.

One limitation relevant to this work:
The causes proposed in the three error patterns (hard-tyre starters, an unseen circuit, reactive stops under neutralisation) are hypotheses drafted by the assistant and are not measured. The assistant also chose which contexts to inspect, which is a form of selection on development data. Its drafts can sound more certain than the evidence.

Do not invent an error or interaction. No minimum number of prompts is required.

## Contributions

- Contributor 1, concrete action and related file/cell: Milan Kurte — Chose the candidate tuple (`forest_sqrt / min_samples_leaf / 100`) and validated its expectation and mechanism in `experiment_spec.md` before the first run; approved committing that spec before execution (commit `be6c673`) for traceability; reviewed the three error-pattern entries in notebook Section 5 ("Your three entries").
- Contributor 2, concrete action and related file/cell: Francisco Polo — Co-authored and reviewed the recommendation in `memo.md` so the metrics read correctly for the Head of Strategy, and verified the 2026 audit and leakage rejection in `PROMPTS.md`.
