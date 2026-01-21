import json
import os
from datetime import datetime
from typing import Dict, Optional, List, Any


class KnowledgeBase:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.timetable = {}
        self.exams = {}
        self.holidays = {}
        self.academic_rules = {}
        self.load_all_data()
    
    def load_all_data(self):
        try:
            with open(os.path.join(self.data_dir, "timetable.json"), 'r', encoding='utf-8') as f:
                self.timetable = json.load(f)
        except FileNotFoundError:
            print(f"Warning: timetable.json not found in {self.data_dir}")
        
        try:
            with open(os.path.join(self.data_dir, "exams.json"), 'r', encoding='utf-8') as f:
                self.exams = json.load(f)
        except FileNotFoundError:
            print(f"Warning: exams.json not found in {self.data_dir}")
        
        try:
            with open(os.path.join(self.data_dir, "holidays.json"), 'r', encoding='utf-8') as f:
                self.holidays = json.load(f)
        except FileNotFoundError:
            print(f"Warning: holidays.json not found in {self.data_dir}")
        
        try:
            with open(os.path.join(self.data_dir, "academic_rules.json"), 'r', encoding='utf-8') as f:
                self.academic_rules = json.load(f)
        except FileNotFoundError:
            print(f"Warning: academic_rules.json not found in {self.data_dir}")
    
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
