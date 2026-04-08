import json
import os
import random
from collections import Counter, defaultdict
from typing import Dict, List

import numpy as np
from sklearn.model_selection import train_test_split

RANDOM_SEED = 42
OUTPUT_DIR = "data_splits"

# Default: 50% of samples go to test (25% train, 25% dev). Override with BENCHMARK_TEST_FRACTION=0.4 etc.
def _test_fraction() -> float:
    raw = os.environ.get("BENCHMARK_TEST_FRACTION", "0.5").strip()
    try:
        f = float(raw)
        return min(0.9, max(0.1, f))
    except ValueError:
        return 0.5


def _load(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _dump(path: str, records: List[Dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)


def stratified_split(records: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Split each intent group into train / dev / test.
    Default: test_fraction of all rows go to test (~50%), remainder split 50-50 between train and dev
    (so overall ~25% train, ~25% dev, ~50% test).
    """
    if not records:
        return {"train": [], "dev": [], "test": []}

    test_fraction = _test_fraction()
    train_val_fraction = 1.0 - test_fraction
    # Of the train+dev block, half each -> (1-test)/2 train, (1-test)/2 dev
    dev_of_trainval = 0.5

    grouped = defaultdict(list)
    for rec in records:
        grouped[rec["intent"]].append(rec)

    rng = random.Random(RANDOM_SEED)
    train, dev, test = [], [], []

    for _, items in grouped.items():
        rng.shuffle(items)
        labels = [rec["intent"] for rec in items]
        n = len(items)
        if n < 2:
            train.extend(items)
            continue

        idx = np.arange(n)
        y = np.array(labels)
        try:
            strat = y if min(Counter(labels).values()) >= 2 else None
            idx_tv, idx_te, _, _ = train_test_split(
                idx,
                y,
                test_size=test_fraction,
                random_state=RANDOM_SEED,
                stratify=strat,
            )
        except ValueError:
            idx_tv, idx_te, _, _ = train_test_split(
                idx, y, test_size=test_fraction, random_state=RANDOM_SEED
            )

        items_arr = np.array(items, dtype=object)
        tv_items = items_arr[idx_tv].tolist()
        te_items = items_arr[idx_te].tolist()
        test.extend(te_items)

        if len(tv_items) < 2:
            train.extend(tv_items)
            continue

        y_tv = [rec["intent"] for rec in tv_items]
        idx2 = np.arange(len(tv_items))
        try:
            strat2 = y_tv if min(Counter(y_tv).values()) >= 2 else None
            idx_tr, idx_dv, _, _ = train_test_split(
                idx2,
                y_tv,
                test_size=dev_of_trainval,
                random_state=RANDOM_SEED,
                stratify=strat2,
            )
        except ValueError:
            idx_tr, idx_dv, _, _ = train_test_split(
                idx2, y_tv, test_size=dev_of_trainval, random_state=RANDOM_SEED
            )

        tv_arr = np.array(tv_items, dtype=object)
        train.extend(tv_arr[idx_tr].tolist())
        dev.extend(tv_arr[idx_dv].tolist())

    rng.shuffle(train)
    rng.shuffle(dev)
    rng.shuffle(test)

    return {"train": train, "dev": dev, "test": test}


def _resolve_benchmark_paths() -> tuple:
    """Prefer hand-curated JSON by default (accurate domain metrics). Synthetic only if opted in."""
    use_synthetic = os.environ.get("USE_SYNTHETIC_BENCHMARKS", "").lower() in (
        "1",
        "true",
        "yes",
    )
    if use_synthetic:
        if os.path.exists("benchmark_queries_large.json") and os.path.exists(
            "benchmark_stress_large.json"
        ):
            return "benchmark_queries_large.json", "benchmark_stress_large.json"
        if os.path.exists("benchmark_queries_augmented.json") and os.path.exists(
            "benchmark_stress_augmented.json"
        ):
            return "benchmark_queries_augmented.json", "benchmark_stress_augmented.json"
    return "benchmark_queries.json", "benchmark_stress.json"


def main() -> None:
    clean_path, stress_path = _resolve_benchmark_paths()

    clean_records = _load(clean_path)
    stress_records = _load(stress_path)

    clean_split = stratified_split(clean_records)
    stress_split = stratified_split(stress_records)

    combined_train = clean_split["train"] + stress_split["train"]
    combined_dev = clean_split["dev"] + stress_split["dev"]
    rng = random.Random(RANDOM_SEED)
    rng.shuffle(combined_train)
    rng.shuffle(combined_dev)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    _dump(os.path.join(OUTPUT_DIR, "train.json"), combined_train)
    _dump(os.path.join(OUTPUT_DIR, "dev.json"), combined_dev)
    _dump(os.path.join(OUTPUT_DIR, "test_clean.json"), clean_split["test"])
    _dump(os.path.join(OUTPUT_DIR, "test_stress.json"), stress_split["test"])

    print("Created leakage-free datasets in data_splits/:")
    print(f"- source clean: {clean_path}")
    print(f"- source stress: {stress_path}")
    if "large" not in clean_path and "augmented" not in clean_path:
        print("- (hand-curated sources; set USE_SYNTHETIC_BENCHMARKS=1 to use generated large/augmented files)")
    print(f"- train.json: {len(combined_train)}")
    print(f"- dev.json: {len(combined_dev)}")
    print(f"- test_clean.json: {len(clean_split['test'])}")
    print(f"- test_stress.json: {len(stress_split['test'])}")
    print(f"- test fraction target: {_test_fraction():.0%} of each intent bucket (env BENCHMARK_TEST_FRACTION)")


if __name__ == "__main__":
    main()
