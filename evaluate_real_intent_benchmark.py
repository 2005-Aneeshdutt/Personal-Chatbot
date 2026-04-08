"""
Train and evaluate intent classifier on REAL public data (Banking77 splits).

Use this for credible, non-synthetic metrics. Domain-specific college metrics
still come from hand-curated benchmark_queries.json after prepare_datasets.py.

Run:
  python prepare_real_intent_splits.py   # once, downloads Banking77
  python evaluate_real_intent_benchmark.py
"""

from __future__ import annotations

import json
import os

from sklearn.metrics import accuracy_score, classification_report, f1_score

from config_loader import load_config
from intent_pipeline import build_intent_model_pipeline

SPLIT_DIR = os.path.join("data_splits_real", "banking77")


def _load(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    train_p = os.path.join(SPLIT_DIR, "train.json")
    dev_p = os.path.join(SPLIT_DIR, "dev.json")
    test_p = os.path.join(SPLIT_DIR, "test.json")
    if not all(os.path.isfile(p) for p in (train_p, dev_p, test_p)):
        raise FileNotFoundError(
            f"Missing files under {SPLIT_DIR}/. Run: python prepare_real_intent_splits.py"
        )

    train = _load(train_p)
    dev = _load(dev_p)
    test = _load(test_p)

    x_train = [r["query"] for r in train]
    y_train = [r["intent"] for r in train]
    x_dev = [r["query"] for r in dev]
    y_dev = [r["intent"] for r in dev]
    x_test = [r["query"] for r in test]
    y_test = [r["intent"] for r in test]

    model = build_intent_model_pipeline(load_config())
    model.fit(x_train, y_train)

    dev_preds = model.predict(x_dev)
    test_preds = model.predict(x_test)

    dev_acc = accuracy_score(y_dev, dev_preds)
    dev_f1 = f1_score(y_dev, dev_preds, average="macro", zero_division=0)
    test_acc = accuracy_score(y_test, test_preds)
    test_f1 = f1_score(y_test, test_preds, average="macro", zero_division=0)

    print("\n=== Real-data benchmark: Banking77 (non-synthetic) ===")
    print(f"Train: {len(train)}  Dev: {len(dev)}  Test: {len(test)}")
    print(f"Dev  accuracy:  {dev_acc * 100:.2f}%")
    print(f"Dev  macro-F1:  {dev_f1 * 100:.2f}%")
    print(f"Test accuracy:  {test_acc * 100:.2f}%")
    print(f"Test macro-F1: {test_f1 * 100:.2f}%")
    print("\nTest classification report (macro avg):")
    print(classification_report(y_test, test_preds, digits=3, zero_division=0))

    report_path = "metrics_report_real.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Real-data intent benchmark (Banking77)\n\n")
        f.write("Non-synthetic user utterances. Labels 0–77 (banking intents).\n\n")
        f.write(f"| Split | Samples | Accuracy | Macro-F1 |\n|---|---:|---:|---:|\n")
        f.write(f"| Dev | {len(dev)} | {dev_acc * 100:.2f}% | {dev_f1 * 100:.2f}% |\n")
        f.write(f"| Test | {len(test)} | {test_acc * 100:.2f}% | {test_f1 * 100:.2f}% |\n")
    print(f"\nWrote {report_path}")


if __name__ == "__main__":
    main()
