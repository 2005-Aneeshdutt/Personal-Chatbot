"""Load project configuration from JSON (no hardcoded paths in business logic)."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Any, Dict, Optional


def project_root() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def resolve_path(root: str, relative: str) -> str:
    if os.path.isabs(relative):
        return relative
    return os.path.normpath(os.path.join(root, relative))


@lru_cache(maxsize=4)
def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    root = project_root()
    path = config_path or os.environ.get(
        "CHATBOT_CONFIG", os.path.join(root, "config", "app_config.json")
    )
    with open(path, encoding="utf-8") as f:
        cfg = json.load(f)
    cfg["_project_root"] = root
    cfg["_config_path"] = path
    paths = cfg.get("paths", {})
    for key in (
        "entity_extraction",
        "intent_model",
        "intent_train_data",
        "ui_strings",
        "llm_system_prompt_file",
    ):
        if key in paths and isinstance(paths[key], str):
            paths[key] = resolve_path(root, paths[key])
    if "knowledge_base_dir" in paths:
        paths["knowledge_base_dir"] = resolve_path(root, paths["knowledge_base_dir"])
    if "intent_train_sources" in paths and isinstance(paths["intent_train_sources"], list):
        paths["intent_train_sources"] = [
            resolve_path(root, p) if isinstance(p, str) and not os.path.isabs(p) else p
            for p in paths["intent_train_sources"]
        ]
    cfg["paths"] = paths
    return cfg


def load_ui_strings(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    cfg = config or load_config()
    path = cfg["paths"].get("ui_strings")
    if not path or not os.path.isfile(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)
