import re
from datetime import datetime, timedelta
from typing import Dict, Optional


class EntityExtractor:
    def __init__(self):
        self.department_patterns = [
            r'\b(cse|computer science|computer science engineering)\b',
            r'\b(ece|electronics|electronics and communication)\b',
            r'\b(me|mechanical|mechanical engineering)\b',
            r'\b(ee|electrical|electrical engineering)\b',
            r'\b(ce|civil|civil engineering)\b',
            r'\b(bt|biotech|biotechnology)\b'
        ]
        
        self.semester_patterns = [
            r'\b(sem\s*[1-8]|semester\s*[1-8]|1st\s*sem|first\s*sem|2nd\s*sem|second\s*sem|3rd\s*sem|third\s*sem|4th\s*sem|fourth\s*sem)\b',
            r'\bsem\s*(\d+)\b',
            r'\bsemester\s*(\d+)\b'
        ]
        
        self.day_patterns = [
            r'\b(monday|mon)\b', r'\b(tuesday|tue)\b', r'\b(wednesday|wed)\b',
            r'\b(thursday|thu)\b', r'\b(friday|fri)\b', r'\b(saturday|sat)\b',
            r'\b(sunday|sun)\b'
        ]
        
        self.date_patterns = [
            r'\b(tomorrow|today)\b',
            r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b',
            r'\b(\d{4}[-/]\d{1,2}[-/]\d{1,2})\b',
        ]
        
        self.exam_type_patterns = [
            r'\b(mid\s*sem|mid\s*semester|midterm)\b',
            r'\b(end\s*sem|end\s*semester|final\s*exam)\b'
        ]
    
    def extract_department(self, query):
        query_lower = query.lower()
        
        department_map = {
            'cse': 'CSE',
            'computer science': 'CSE',
            'computer science engineering': 'CSE',
            'ece': 'ECE',
            'electronics': 'ECE',
            'electronics and communication': 'ECE',
            'me': 'ME',
            'mechanical': 'ME',
            'mechanical engineering': 'ME',
            'ee': 'EE',
            'electrical': 'EE',
            'electrical engineering': 'EE',
            'ce': 'CE',
            'civil': 'CE',
            'civil engineering': 'CE',
            'bt': 'BT',
            'biotech': 'BT',
            'biotechnology': 'BT'
        }
        
        for pattern in self.department_patterns:
            match = re.search(pattern, query_lower, re.IGNORECASE)
            if match:
                matched_text = match.group(0).lower()
                for key, value in department_map.items():
                    if key in matched_text:
                        return value
        
        return None
    
    def extract_semester(self, query):
        query_lower = query.lower()
        
        for pattern in self.semester_patterns:
            match = re.search(pattern, query_lower, re.IGNORECASE)
            if match:
                number_match = re.search(r'\d+', match.group(0))
                if number_match:
                    sem_num = int(number_match.group(0))
                    return f"Semester {sem_num}"
        
        return None
    
    def extract_day(self, query):
        query_lower = query.lower()
        
        day_map = {
            'monday': 'Monday', 'mon': 'Monday',
            'tuesday': 'Tuesday', 'tue': 'Tuesday',
            'wednesday': 'Wednesday', 'wed': 'Wednesday',
            'thursday': 'Thursday', 'thu': 'Thursday',
            'friday': 'Friday', 'fri': 'Friday',
            'saturday': 'Saturday', 'sat': 'Saturday',
            'sunday': 'Sunday', 'sun': 'Sunday'
        }
        
        for day_key, day_value in day_map.items():
            if re.search(rf'\b{day_key}\b', query_lower, re.IGNORECASE):
                return day_value
        
        if re.search(r'\btomorrow\b', query_lower):
            tomorrow = datetime.now() + timedelta(days=1)
            return tomorrow.strftime("%A")
        
        if re.search(r'\btoday\b', query_lower):
            today = datetime.now()
            return today.strftime("%A")
        
        return None
    
    def extract_date(self, query):
        query_lower = query.lower()
        today = datetime.now()
        
        if re.search(r'\btomorrow\b', query_lower):
            tomorrow = today + timedelta(days=1)
            return tomorrow.strftime("%Y-%m-%d")
        elif re.search(r'\btoday\b', query_lower):
            return today.strftime("%Y-%m-%d")
        
        for pattern in self.date_patterns[1:]:
            match = re.search(pattern, query_lower)
            if match:
                date_str = match.group(1)
                try:
                    for fmt in ["%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d", "%Y/%m/%d", "%d-%m-%y", "%d/%m/%y"]:
                        try:
                            date_obj = datetime.strptime(date_str, fmt)
                            return date_obj.strftime("%Y-%m-%d")
                        except ValueError:
                            continue
                except:
                    pass
        
        return None
    
    def extract_exam_type(self, query):
        query_lower = query.lower()
        
        if re.search(self.exam_type_patterns[0], query_lower, re.IGNORECASE):
            return "mid_semester"
        elif re.search(self.exam_type_patterns[1], query_lower, re.IGNORECASE):
            return "end_semester"
        
        return None
    
    def extract_all(self, query):
        return {
            "department": self.extract_department(query),
            "semester": self.extract_semester(query),
            "day": self.extract_day(query),
            "date": self.extract_date(query),
            "exam_type": self.extract_exam_type(query)
        }
