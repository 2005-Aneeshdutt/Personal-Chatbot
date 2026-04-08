"""Shared TF-IDF + LogisticRegression pipeline for intent classification (config-driven)."""

from __future__ import annotations

from typing import Any, Dict

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion, Pipeline

from config_loader import load_config


def _tuple_ng(val: Any) -> tuple:
    if isinstance(val, (list, tuple)):
        return tuple(val)
    return (1, 2)


def _tfidf_from_cfg(section: Dict[str, Any]) -> TfidfVectorizer:
    """Build TfidfVectorizer; unknown keys are ignored."""
    params = {
        "ngram_range": _tuple_ng(section.get("ngram_range", [1, 2])),
        "lowercase": bool(section.get("lowercase", True)),
        "sublinear_tf": bool(section.get("sublinear_tf", False)),
        "min_df": section.get("min_df", 1),
        "max_df": section.get("max_df", 1.0),
    }
    if "analyzer" in section:
        params["analyzer"] = section["analyzer"]
    if "max_features" in section:
        params["max_features"] = section["max_features"]
    return TfidfVectorizer(**params)


def build_intent_model_pipeline(config: Dict[str, Any] | None = None) -> Pipeline:
    cfg = config or load_config()
    tm = cfg.get("intent_model_training", {})
    lr_cfg = dict(
        tm.get(
            "logistic_regression",
            {
                "max_iter": 2000,
                "class_weight": "balanced",
                "solver": "saga",
                "multi_class": "multinomial",
                "C": 10.0,
                "random_state": 42,
                "n_jobs": -1,
            },
        )
    )
    tw = tm.get("tfidf_word", {"ngram_range": [1, 3], "lowercase": True})
    tc = tm.get(
        "tfidf_char",
        {"analyzer": "char_wb", "ngram_range": [2, 5], "lowercase": True},
    )

    word_vec = _tfidf_from_cfg(tw)
    char_vec = _tfidf_from_cfg(tc)

    return Pipeline(
        steps=[
            (
                "features",
                FeatureUnion(
                    transformer_list=[
                        ("word_tfidf", word_vec),
                        ("char_tfidf", char_vec),
                    ]
                ),
            ),
            ("clf", LogisticRegression(**lr_cfg)),
        ]
    )
