# College Helpdesk Chatbot

An assistant for **timetables, exams, holidays, credits, attendance, and department contacts**, with **ML-based intent classification**, a **JSON knowledge base**, and **LLM fallback** (OpenAI or Ollama). Configuration lives under `config/` and `data/` — not scattered in code.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![scikit-learn](https://img.shields.io/badge/scikit--learn-TF--IDF%20%2B%20LR-orange.svg)

---

## Results at a glance

Evaluation is **reproducible** (scripts below). Two tracks: **your college-intent benchmark** (held-out, curated) and a **public real-world intent dataset** (Banking77) to validate the same ML pipeline on non-synthetic text.

| Track | Best headline | Notes |
|-------|----------------|--------|
| **College intents** (held-out test) | **~90%** intent accuracy / **~92%** macro-F1 | Small but strict splits; see tables |
| **Banking77** (public test set) | **~91%** accuracy / **~91%** macro-F1 | 3,080 real utterances; banking domain |

<details>
<summary><strong>Full tables (click to expand)</strong></summary>

#### College-domain benchmark (`evaluate_chatbot.py`)

Held-out sets from `data_splits/` — model was **not** trained on these rows (trained on merged **train + dev** only). ~50% of curated data per intent reserved for test.

| Dataset | Samples | Intent accuracy | Macro-F1 | Entity micro-F1 | Entity exact match |
|---------|--------:|----------------:|---------:|----------------:|-------------------:|
| `test_clean.json` | 29 | **89.66%** | **91.21%** | **100.00%** | **100.00%** |
| `test_stress.json` | 23 | **91.30%** | **92.24%** | **95.24%** | **90.00%** |

*Stress-set fallback class recall: **66.67%** — see `metrics_report.md` for the confusion matrix.*

#### Public real data — Banking77 (`evaluate_real_intent_benchmark.py`)

Real user messages; **77 intent classes** (banking). Same **TF–IDF + logistic regression** pipeline as above; domain differs from college — use this to show the **classifier** generalizes, not the college content.

| Split | Samples | Accuracy | Macro-F1 |
|-------|--------:|---------:|---------:|
| Dev | 1,001 | **89.91%** | **89.84%** |
| Test | 3,080 | **91.46%** | **91.48%** |

</details>

**Regenerate all numbers** (after you change data, splits, or config):

```bash
python prepare_datasets.py
python train_intent_model.py
python evaluate_chatbot.py
python prepare_real_intent_splits.py    # first run: downloads dataset
python evaluate_real_intent_benchmark.py
```

Artifacts: `metrics_report.md`, `metrics_report_real.md`, and **`METRICS.md`** (interpretation + caveats).

> **Honest scope:** College test sets are **hand-curated and modest in size** — strong for a portfolio / thesis demo, not a claim about every real campus query. Banking77 proves the **intent model** on **real text** in another domain.

---

## Features

| Capability | Description |
|------------|-------------|
| **Intents** | Timetable, exam, holiday, credits, attendance, contact, fallback |
| **Intent model** | TF–IDF + logistic regression (scikit-learn), trained on merged train+dev splits |
| **Entities** | Department, semester, day, date, exam type — patterns in `data/entity_extraction.json` |
| **Knowledge base** | `data/*.json` (timetable, exams, holidays, academic rules) |
| **LLM fallback** | OpenAI or Ollama when query is out of schema |
| **Admin UI** | `streamlit run admin.py` to edit JSON (set password in `admin.py` for production) |

---

## Quick start (3 commands)

```bash
cd LLM
pip install -r requirements.txt
python prepare_datasets.py
python train_intent_model.py
streamlit run app.py
```

Open `http://localhost:8501`. Optional: copy `.env.example` to `.env` and set `OPENAI_API_KEY` if you use OpenAI.

**One-shot setup (Windows):** `.\scripts\run_all.ps1`  
**Linux/macOS:** `bash scripts/run_all.sh`  
**Make:** `make install && make prepare && make train` then `make run`

---

## Limitations (read before citing metrics)

- Domain evaluation uses **curated** queries and **small N** — good for reproducible benchmarks, not a guarantee on all live traffic.
- Banking77 measures **intent classification** on **real** banking utterances; it does **not** score college-specific answers.
- **LLM** replies need a working **OpenAI** or **Ollama** setup; structured KB answers do not.

---

## Project layout

```
├── app.py                 # Streamlit chat UI
├── admin.py               # KB editor UI
├── config/                # app_config.json, ui_strings.json, prompts/
├── data/                  # Knowledge base JSON + entity_extraction.json
├── data_splits/           # train/dev/test (from prepare_datasets.py)
├── intent_detector.py     # Loads models/intent_model.pkl
├── intent_pipeline.py     # TF-IDF + classifier from config
├── train_intent_model.py
├── evaluate_chatbot.py
├── prepare_datasets.py
├── prepare_real_intent_splits.py
├── evaluate_real_intent_benchmark.py
├── tests/test_smoke.py
├── scripts/run_all.ps1 | run_all.sh
├── ARCHITECTURE.txt
├── METRICS.md
└── Makefile
```

---

## Architecture

High-level flow: **query → intent (ML) → entities (patterns) → KB or LLM**. Details: **`ARCHITECTURE.txt`**.

---

## Tests

```bash
pip install -r requirements.txt
pytest tests/test_smoke.py -q
```

Legacy check: `python test_setup.py`

---

## Security notes

- Never commit **`.env`** (see `.gitignore`). Use **`.env.example`** as a template.
- Set a strong **admin password** in `admin.py` before any shared deployment.
- User queries are **trimmed** to `limits.max_query_chars` in `config/app_config.json`.

---

## Customization

- **KB data:** edit `data/*.json` or use the admin panel.
- **Intents / thresholds / LLM URLs:** `config/app_config.json`.
- **UI strings:** `config/ui_strings.json`.
- **New training data:** extend `benchmark_queries.json` / `benchmark_stress.json`, then `prepare_datasets.py` → `train_intent_model.py`.

---

## License

MIT (see `LICENSE` if present). Educational use.
