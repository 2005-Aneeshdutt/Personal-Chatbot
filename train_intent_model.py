import json
import os
from collections import Counter
from typing import List, Tuple

import joblib
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict

from config_loader import load_config, project_root
from intent_pipeline import build_intent_model_pipeline


def _load_records(path: str) -> List[dict]:
    root = project_root()
    full = path if os.path.isabs(path) else os.path.normpath(os.path.join(root, path))
    with open(full, encoding="utf-8") as f:
        return json.load(f)


def load_dataset(paths: List[str]) -> Tuple[List[str], List[str]]:
    texts: List[str] = []
    labels: List[str] = []
    for path in paths:
        if not path:
            continue
        records = _load_records(path)
        for record in records:
            intent = record.get("intent")
            if not intent:
                continue
            texts.append(record.get("query", ""))
            labels.append(intent)
    return texts, labels


def main() -> None:
    cfg = load_config()
    paths_cfg = cfg["paths"]
    sources = paths_cfg.get("intent_train_sources")
    if not sources:
        sources = [paths_cfg.get("intent_train_data", "data_splits/train.json")]

    if not any(os.path.isfile(p) for p in sources if p):
        raise FileNotFoundError(
            "Missing split files. Run: python prepare_datasets.py"
        )

    x_train, y_train = load_dataset(list(sources))
    print(f"Training on merged non-test data: {len(x_train)} samples from {len(sources)} file(s)")

    model = build_intent_model_pipeline(cfg)

    min_class = min(Counter(y_train).values()) if y_train else 0
    n_splits = max(2, min(5, min_class)) if min_class >= 2 else 0
    if (
        n_splits >= 2
        and len(set(y_train)) >= 2
        and len(y_train) >= n_splits * 2
        and min_class >= 2
    ):
        pipe = build_intent_model_pipeline(cfg)
        cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
        try:
            y_pred = cross_val_predict(pipe, x_train, y_train, cv=cv)
        except ValueError:
            y_pred = None
        if y_pred is not None:
            print(
                f"\nStratified {n_splits}-fold CV on training pool (train+dev): "
                f"accuracy={accuracy_score(y_train, y_pred) * 100:.2f}%, "
                f"macro-F1={f1_score(y_train, y_pred, average='macro') * 100:.2f}%"
            )

    model.fit(x_train, y_train)
    print("\nFit final model on full training pool (train+dev). Test metrics: python evaluate_chatbot.py")

    out_path = paths_cfg.get("intent_model", "models/intent_model.pkl")
    model_dir = os.path.dirname(out_path)
    if model_dir:
        os.makedirs(model_dir, exist_ok=True)
    joblib.dump(model, out_path)
    print(f"Saved model to {out_path}")


if __name__ == "__main__":
    main()
