import json
import os
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from config_loader import load_config


class EntityExtractor:
    """Loads regex patterns and maps from data/entity_extraction.json (config-driven)."""

    def __init__(self, entity_config_path: Optional[str] = None):
        cfg = load_config()
        path = entity_config_path or cfg["paths"].get("entity_extraction")
        if not path or not os.path.isfile(path):
            raise FileNotFoundError(
                f"Entity config not found: {path}. Set paths.entity_extraction in config/app_config.json"
            )
        with open(path, encoding="utf-8") as f:
            self._spec: Dict[str, Any] = json.load(f)

        self.department_patterns = [re.compile(p, re.IGNORECASE) for p in self._spec["department_patterns"]]
        self.department_canonical = self._spec["department_canonical"]
        self.semester_patterns = [re.compile(p, re.IGNORECASE) for p in self._spec["semester_patterns"]]
        self.semester_label_format = self._spec.get("semester_label_format", "Semester {n}")
        self.day_map = self._spec["day_map"]
        self.relative_day_keywords = self._spec.get("relative_day_keywords", {"tomorrow": 1, "today": 0})
        self.date_patterns = [re.compile(p, re.IGNORECASE) for p in self._spec["date_patterns"]]
        self.date_parse_formats: List[str] = self._spec["date_parse_formats"]
        self.exam_type_rules = [
            (re.compile(rule["pattern"], re.IGNORECASE), rule["label"])
            for rule in self._spec["exam_type_rules"]
        ]

    def extract_department(self, query: str) -> Optional[str]:
        query_lower = query.lower()
        for pattern in self.department_patterns:
            match = pattern.search(query_lower)
            if match:
                matched_text = match.group(0).lower()
                for key, value in self.department_canonical.items():
                    if key in matched_text:
                        return value
        return None

    def extract_semester(self, query: str) -> Optional[str]:
        query_lower = query.lower()
        for pattern in self.semester_patterns:
            match = pattern.search(query_lower)
            if match:
                number_match = re.search(r"\d+", match.group(0))
                if number_match:
                    sem_num = int(number_match.group(0))
                    return self.semester_label_format.format(n=sem_num)
        return None

    def extract_day(self, query: str) -> Optional[str]:
        query_lower = query.lower()
        for day_key, day_value in self.day_map.items():
            if re.search(rf"\b{re.escape(day_key)}\b", query_lower, re.IGNORECASE):
                return day_value

        if re.search(r"\btomorrow\b", query_lower):
            delta = self.relative_day_keywords.get("tomorrow", 1)
            day = datetime.now() + timedelta(days=int(delta))
            return day.strftime("%A")

        if re.search(r"\btoday\b", query_lower):
            delta = self.relative_day_keywords.get("today", 0)
            day = datetime.now() + timedelta(days=int(delta))
            return day.strftime("%A")

        return None

    def extract_date(self, query: str) -> Optional[str]:
        query_lower = query.lower()
        today = datetime.now()

        if re.search(r"\btomorrow\b", query_lower):
            tomorrow = today + timedelta(days=1)
            return tomorrow.strftime("%Y-%m-%d")
        if re.search(r"\btoday\b", query_lower):
            return today.strftime("%Y-%m-%d")

        for pattern in self.date_patterns[1:]:
            match = pattern.search(query_lower)
            if match:
                date_str = match.group(1)
                for fmt in self.date_parse_formats:
                    try:
                        date_obj = datetime.strptime(date_str, fmt)
                        return date_obj.strftime("%Y-%m-%d")
                    except ValueError:
                        continue

        return None

    def extract_exam_type(self, query: str) -> Optional[str]:
        query_lower = query.lower()
        for pattern, label in self.exam_type_rules:
            if pattern.search(query_lower):
                return label
        return None

    def extract_all(self, query: str) -> Dict[str, Optional[str]]:
        return {
            "department": self.extract_department(query),
            "semester": self.extract_semester(query),
            "day": self.extract_day(query),
            "date": self.extract_date(query),
            "exam_type": self.extract_exam_type(query),
        }
