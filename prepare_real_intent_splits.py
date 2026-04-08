"""
Build train/dev/test JSON from real public intent data (no synthetic templates).

Uses Hugging Face `banking77`: real banking customer utterances, 77 intent classes.
- train / dev: stratified split from the official *training* split only
- test: official *test* split (held out, never seen during train/dev tuning)

Output: data_splits_real/banking77/{train,dev,test}.json
Each row: {"query": "<text>", "intent": "<label_as_string>"}

Run: pip install datasets
     python prepare_real_intent_splits.py
"""

from __future__ import annotations

import json
import os
from typing import List, Tuple

from sklearn.model_selection import train_test_split

RANDOM_SEED = 42
OUT_DIR = os.path.join("data_splits_real", "banking77")


def _stratified_train_dev(
    texts: List[str], labels: List[str], dev_size: float = 0.1
) -> Tuple[List[dict], List[dict]]:
    idx_train, idx_dev = train_test_split(
        range(len(texts)),
        test_size=dev_size,
        random_state=RANDOM_SEED,
        stratify=labels,
    )
    train_recs = [{"query": texts[i], "intent": labels[i]} for i in idx_train]
    dev_recs = [{"query": texts[i], "intent": labels[i]} for i in idx_dev]
    return train_recs, dev_recs


def main() -> None:
    from datasets import load_dataset

    ds = load_dataset("banking77")
    train_texts = [str(x) for x in ds["train"]["text"]]
    train_labels = [str(y) for y in ds["train"]["label"]]

    train_recs, dev_recs = _stratified_train_dev(train_texts, train_labels)

    test_texts = [str(x) for x in ds["test"]["text"]]
    test_labels = [str(y) for y in ds["test"]["label"]]
    test_recs = [{"query": t, "intent": y} for t, y in zip(test_texts, test_labels)]

    os.makedirs(OUT_DIR, exist_ok=True)
    for name, recs in [
        ("train.json", train_recs),
        ("dev.json", dev_recs),
        ("test.json", test_recs),
    ]:
        path = os.path.join(OUT_DIR, name)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(recs, f, indent=2)

    print("Wrote real (non-synthetic) Banking77 splits:")
    print(f"  {OUT_DIR}/train.json  ({len(train_recs)} rows)")
    print(f"  {OUT_DIR}/dev.json    ({len(dev_recs)} rows)")
    print(f"  {OUT_DIR}/test.json   ({len(test_recs)} rows) — official held-out test")
    print("Labels are 0..76 (string). This benchmarks the ML pipeline on real user text.")


if __name__ == "__main__":
    main()
