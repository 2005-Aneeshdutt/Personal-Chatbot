import re
from typing import Dict, Optional, Tuple, List


class IntentDetector:
    def __init__(self):
        self.intent_patterns = {
            "timetable": [
                r"timetable", r"schedule", r"class schedule", r"what.*class",
                r"tomorrow.*class", r"today.*class", r"which.*class",
                r"when.*class", r"what.*period", r"time.*table"
            ],
            "exam": [
                r"exam", r"examination", r"mid.*sem", r"end.*sem",
                r"when.*exam", r"exam.*date", r"exam.*schedule",
                r"when.*examination", r"exam.*time"
            ],
            "holiday": [
                r"holiday", r"holidays", r"is.*holiday", r"holiday.*tomorrow",
                r"holiday.*today", r"when.*holiday", r"college.*closed",
                r"closed.*day"
            ],
            "credits": [
                r"credit", r"credits", r"how.*many.*credit",
                r"credit.*requirement", r"credit.*needed", r"credit.*pass",
                r"minimum.*credit", r"total.*credit"
            ],
            "attendance": [
                r"attendance", r"attendance.*percentage", r"minimum.*attendance",
                r"attendance.*rule", r"attendance.*required", r"attendance.*pass",
                r"how.*much.*attendance"
            ],
            "contact": [
                r"contact", r"hod", r"head.*department", r"department.*head",
                r"who.*hod", r"email.*department", r"phone.*department",
                r"department.*contact", r"office.*location"
            ]
        }
    
    def detect_intent(self, query):
        query_lower = query.lower()
        intent_scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, query_lower, re.IGNORECASE):
                    score += 1
            
            if score > 0:
                intent_scores[intent] = score
        
        if not intent_scores:
            return None, 0.0
        
        best_intent = max(intent_scores, key=intent_scores.get)
        confidence = min(intent_scores[best_intent] / 3.0, 1.0)
        
        return best_intent, confidence
    
    def get_all_intents(self):
        return list(self.intent_patterns.keys())
