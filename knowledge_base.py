import json
import os
from datetime import datetime
from typing import Dict, Optional

from config_loader import load_config


class KnowledgeBase:
    def __init__(self, data_dir: Optional[str] = None, kb_files: Optional[Dict[str, str]] = None):
        cfg = load_config()
        paths = cfg["paths"]
        self.data_dir = data_dir or paths["knowledge_base_dir"]
        self.kb_files = kb_files or paths.get(
            "kb_files",
            {
                "timetable": "timetable.json",
                "exams": "exams.json",
                "holidays": "holidays.json",
                "academic_rules": "academic_rules.json",
            },
        )
        self.timetable = {}
        self.exams = {}
        self.holidays = {}
        self.academic_rules = {}
        self.load_all_data()

    def load_all_data(self) -> None:
        mapping = [
            ("timetable", "timetable"),
            ("exams", "exams"),
            ("holidays", "holidays"),
            ("academic_rules", "academic_rules"),
        ]
        for attr, key in mapping:
            name = self.kb_files.get(key)
            if not name:
                continue
            path = os.path.join(self.data_dir, name)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    setattr(self, attr, json.load(f))
            except FileNotFoundError:
                print(f"Warning: {name} not found at {path}")
    
    def get_timetable(self, department, semester, day=None):
        dept = department.upper()
        if dept in self.timetable:
            if semester in self.timetable[dept]:
                if day:
                    return self.timetable[dept][semester].get(day)
                return self.timetable[dept][semester]
        return None
    
    def get_exam_schedule(self, exam_type, department, semester):
        dept = department.upper()
        if exam_type in self.exams:
            if dept in self.exams[exam_type]:
                return self.exams[exam_type][dept].get(semester)
        return None
    
    def check_holiday(self, date):
        try:
            if len(date) == 10:
                date_obj = datetime.strptime(date, "%Y-%m-%d")
                year = str(date_obj.year)
                month_day = date_obj.strftime("%m-%d")
            else:
                month_day = date
                year = str(datetime.now().year)
            
            if year in self.holidays:
                return self.holidays[year].get(month_day)
        except ValueError:
            pass
        
        return None
    
    def get_credit_requirements(self):
        return self.academic_rules.get("credit_requirements", {})
    
    def get_attendance_rules(self):
        return self.academic_rules.get("attendance_rules", {})
    
    def get_department_contact(self, department):
        dept = department.upper()
        contacts = self.academic_rules.get("department_contacts", {})
        return contacts.get(dept)
    
    def get_all_departments(self):
        return list(self.timetable.keys())
    
    def get_semesters_for_dept(self, department):
        dept = department.upper()
        if dept in self.timetable:
            return list(self.timetable[dept].keys())
        return []
