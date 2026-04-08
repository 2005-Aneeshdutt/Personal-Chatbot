# Evaluation metrics (reported values)

Regenerate after changing data or model:

```bash
python prepare_datasets.py
python train_intent_model.py
python evaluate_chatbot.py
python prepare_real_intent_splits.py   # first time: downloads Banking77
python evaluate_real_intent_benchmark.py
```

## Domain benchmark (college intents)

Held-out test sets from `benchmark_queries.json` / `benchmark_stress.json` via `prepare_datasets.py` (~50% of rows per intent to test). Model trained on merged **train + dev** only (not test). *Small sample sizes — illustrative, not production-scale.*

| Dataset | Samples | Intent accuracy | Macro-F1 | Entity micro-F1 | Entity exact match |
|---------|--------:|----------------:|---------:|----------------:|-------------------:|
| `data_splits/test_clean.json` | 29 | **89.66%** | **91.21%** | 100.00% | 100.00% |
| `data_splits/test_stress.json` | 23 | **91.30%** | **92.24%** | 95.24% | 90.00% |

Fallback recall (stress test): **66.67%** on fallback class (see full `metrics_report.md`).

## Real public data (Banking77)

Same ML pipeline, **non-synthetic** user utterances, **77 banking intents** (different domain than college — validates the classifier on real text).

| Split | Samples | Accuracy | Macro-F1 |
|-------|--------:|---------:|---------:|
| Dev | 1001 | **89.91%** | **89.84%** |
| Test | 3080 | **91.46%** | **91.48%** |

*Last run aligned with `metrics_report.md` and `metrics_report_real.md` in repo.*
