"""Lightweight smoke tests — run: pytest tests/test_smoke.py -q"""

import os
import sys

# Project root on path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def test_imports():
    from knowledge_base import KnowledgeBase
    from intent_detector import IntentDetector
    from entity_extractor import EntityExtractor
    from llm_fallback import LLMFallback

    assert KnowledgeBase and IntentDetector and EntityExtractor and LLMFallback


def test_knowledge_base_loads():
    from knowledge_base import KnowledgeBase

    kb = KnowledgeBase()
    assert isinstance(kb.get_all_departments(), list)


def test_entity_extractor_one_query():
    from entity_extractor import EntityExtractor

    ex = EntityExtractor()
    out = ex.extract_all("What is the timetable for CSE semester 3 on Monday?")
    assert out.get("department") == "CSE"
    assert "Semester" in (out.get("semester") or "")


def test_intent_model_if_present():
    from intent_detector import IntentDetector

    det = IntentDetector()
    if det.model is None:
        return
    intent, conf = det.detect_intent("When are mid-semester exams for CSE semester 3?")
    assert conf >= 0.0
    if intent is not None:
        assert isinstance(intent, str)
