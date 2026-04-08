import json
import os
from typing import Any, Dict, List, Optional, Tuple

import joblib
from sklearn.pipeline import Pipeline

from config_loader import load_config
from intent_pipeline import build_intent_model_pipeline


def _load_training_records(cfg: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    paths_cfg = cfg["paths"]
    sources: List[str] = paths_cfg.get("intent_train_sources") or []
    if not sources:
        single = paths_cfg.get("intent_train_data")
        sources = [single] if single else []

    texts: List[str] = []
    labels: List[str] = []
    for path in sources:
        if not path or not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8") as f:
            records = json.load(f)
        for record in records:
            label = record.get("intent")
            if not label:
                continue
            texts.append(record.get("query", ""))
            labels.append(label)
    return texts, labels


class IntentDetector:
    def __init__(
        self,
        model_path: Optional[str] = None,
        train_data_path: Optional[str] = None,
        min_confidence: Optional[float] = None,
    ):
        cfg = load_config()
        paths = cfg["paths"]
        intent_cfg = cfg.get("intent", {})
        self.model_path = model_path or paths["intent_model"]
        self.train_data_path = train_data_path or paths.get("intent_train_data")
        self.min_confidence = (
            min_confidence if min_confidence is not None else intent_cfg.get("min_confidence", 0.2)
        )
        self.model: Optional[Pipeline] = self._load_or_train_model()

    def _load_or_train_model(self) -> Optional[Pipeline]:
        if os.path.exists(self.model_path):
            try:
                return joblib.load(self.model_path)
            except Exception:
                pass

        return self._train_from_config()

    def _train_from_config(self) -> Optional[Pipeline]:
        cfg = load_config()
        texts, labels = _load_training_records(cfg)
        if not texts:
            return None

        model = build_intent_model_pipeline(cfg)
        model.fit(texts, labels)

        model_dir = os.path.dirname(self.model_path)
        if model_dir:
            os.makedirs(model_dir, exist_ok=True)
        joblib.dump(model, self.model_path)
        return model

    def detect_intent(self, query: str) -> Tuple[Optional[str], float]:
        if not self.model:
            return None, 0.0

        probabilities = self.model.predict_proba([query])[0]
        classes = self.model.classes_

        best_index = max(range(len(probabilities)), key=lambda idx: probabilities[idx])
        confidence = float(probabilities[best_index])
        best_intent = str(classes[best_index])

        if best_intent == "fallback":
            return None, confidence
        if confidence < self.min_confidence:
            return None, confidence
        return best_intent, confidence

    def get_all_intents(self):
        if not self.model:
            return []
        return [str(intent) for intent in self.model.classes_]
