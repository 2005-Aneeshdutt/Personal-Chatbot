"""
Evaluate the same intent-classification pipeline on a public, real benchmark.

Uses Hugging Face `datasets` (many Kaggle NLP tasks are mirrored there; no API key).
Default: `banking77` — 77 banking intents, real user utterances (harder than templated data).

Run:
  pip install datasets
  python evaluate_external_intent.py

Optional:
  python evaluate_external_intent.py --dataset clinc_oos --config plus --sample 10000
"""

from __future__ import annotations

import argparse
import random
from typing import List, Tuple

from sklearn.metrics import accuracy_score, classification_report, f1_score
import joblib

from config_loader import load_config
from intent_pipeline import build_intent_model_pipeline


def load_banking77() -> Tuple[List[str], List[str], List[str], List[str]]:
    from datasets import load_dataset

    ds = load_dataset("banking77")
    x_train = [str(t) for t in ds["train"]["text"]]
    y_train = [str(t) for t in ds["train"]["label"]]
    x_test = [str(t) for t in ds["test"]["text"]]
    y_test = [str(t) for t in ds["test"]["label"]]
    return x_train, y_train, x_test, y_test


def load_clinc_oos(config: str = "plus") -> Tuple[List[str], List[str], List[str], List[str]]:
    from datasets import load_dataset

    ds = load_dataset("clinc_oos", config)
    # "intent" is string label; "validation" used as dev if needed
    train = ds["train"]
    test = ds["test"]
    x_train = [str(t) for t in train["text"]]
    y_train = [str(t) for t in train["intent"]]
    x_test = [str(t) for t in test["text"]]
    y_test = [str(t) for t in test["intent"]]
    return x_train, y_train, x_test, y_test


def subsample(
    x: List[str], y: List[str], n: int, seed: int
) -> Tuple[List[str], List[str]]:
    if n <= 0 or n >= len(x):
        return x, y
    rng = random.Random(seed)
    idx = list(range(len(x)))
    rng.shuffle(idx)
    idx = idx[:n]
    return [x[i] for i in idx], [y[i] for i in idx]


def main() -> None:
    parser = argparse.ArgumentParser(description="External intent benchmark (real public data).")
    parser.add_argument(
        "--dataset",
        choices=["banking77", "clinc_oos"],
        default="banking77",
        help="Public benchmark name.",
    )
    parser.add_argument(
        "--config",
        default="plus",
        help="For clinc_oos: 'small', 'imbalanced', 'plus' (default: plus).",
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=0,
        help="Optional cap on training rows (0 = use all). Speeds up local runs.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for subsampling.",
    )
    parser.add_argument(
        "--save",
        default="",
        help="Optional path to save trained model (e.g. models/external_banking77.pkl).",
    )
    args = parser.parse_args()

    if args.dataset == "banking77":
        x_train, y_train, x_test, y_test = load_banking77()
    else:
        x_train, y_train, x_test, y_test = load_clinc_oos(args.config)

    if args.sample > 0:
        x_train, y_train = subsample(x_train, y_train, args.sample, args.seed)

    model = build_intent_model_pipeline(load_config())
    model.fit(x_train, y_train)
    preds = model.predict(x_test)

    acc = accuracy_score(y_test, preds)
    macro_f1 = f1_score(y_test, preds, average="macro", zero_division=0)

    print(f"\nExternal benchmark: {args.dataset}")
    if args.dataset == "clinc_oos":
        print(f"  config: {args.config}")
    print(f"  train size: {len(x_train)}")
    print(f"  test size:  {len(x_test)}")
    print(f"  Test accuracy:  {acc * 100:.2f}%")
    print(f"  Test macro-F1: {macro_f1 * 100:.2f}%")
    print("\nClassification report (test, first 15 lines of summary):")
    report = classification_report(y_test, preds, digits=3, zero_division=0)
    lines = report.splitlines()
    print("\n".join(lines[:15]))
    if len(lines) > 15:
        print("  ...")

    if args.save:
        joblib.dump(model, args.save)
        print(f"\nSaved model to {args.save}")


if __name__ == "__main__":
    main()
