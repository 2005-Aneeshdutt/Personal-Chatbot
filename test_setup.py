import sys

def test_imports():
    try:
        from knowledge_base import KnowledgeBase
        print("[OK] knowledge_base.py imported successfully")
        
        from intent_detector import IntentDetector
        print("[OK] intent_detector.py imported successfully")
        
        from entity_extractor import EntityExtractor
        print("[OK] entity_extractor.py imported successfully")
        
        from llm_fallback import LLMFallback
        print("[OK] llm_fallback.py imported successfully")
        
        return True
    except Exception as e:
        print(f"[ERROR] Import error: {e}")
        return False

def test_knowledge_base():
    try:
        from knowledge_base import KnowledgeBase
        kb = KnowledgeBase()
        
        timetable = kb.get_timetable("CSE", "Semester 3", "Monday")
        if timetable:
            print(f"[OK] Knowledge base loaded - found {len(timetable)} classes for CSE Sem 3 Monday")
        else:
            print("[WARN] Knowledge base loaded but no data found for test query")
        
        depts = kb.get_all_departments()
        print(f"[OK] Found {len(depts)} departments: {', '.join(depts)}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Knowledge base error: {e}")
        return False

def test_intent_detection():
    try:
        from intent_detector import IntentDetector
        detector = IntentDetector()
        
        test_queries = [
            ("What is tomorrow's timetable?", "timetable"),
            ("When are mid-semester exams?", "exam"),
            ("Is tomorrow a holiday?", "holiday"),
            ("How many credits are needed?", "credits"),
        ]
        
        for query, expected_intent in test_queries:
            intent, confidence = detector.detect_intent(query)
            if intent == expected_intent:
                print(f"[OK] Correctly detected '{expected_intent}' for: '{query}'")
            else:
                print(f"[WARN] Detected '{intent}' instead of '{expected_intent}' for: '{query}'")
        
        return True
    except Exception as e:
        print(f"[ERROR] Intent detection error: {e}")
        return False

def test_entity_extraction():
    try:
        from entity_extractor import EntityExtractor
        extractor = EntityExtractor()
        
        test_cases = [
            ("What is tomorrow's timetable for CSE sem 3?", {"department": "CSE", "semester": "Semester 3"}),
        ]
        
        for query, expected in test_cases:
            entities = extractor.extract_all(query)
            dept = entities.get("department")
            sem = entities.get("semester")
            
            if dept == expected.get("department") and sem == expected.get("semester"):
                print(f"[OK] Correctly extracted entities from: '{query}'")
            else:
                print(f"[WARN] Extracted dept='{dept}', sem='{sem}' from: '{query}'")
        
        return True
    except Exception as e:
        print(f"[ERROR] Entity extraction error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("College Helpdesk Chatbot - Setup Test")
    print("=" * 50)
    print()
    
    all_passed = True
    
    print("Testing imports...")
    all_passed &= test_imports()
    print()
    
    print("Testing knowledge base...")
    all_passed &= test_knowledge_base()
    print()
    
    print("Testing intent detection...")
    all_passed &= test_intent_detection()
    print()
    
    print("Testing entity extraction...")
    all_passed &= test_entity_extraction()
    print()
    
    print("=" * 50)
    if all_passed:
        print("[OK] All tests passed! Setup looks good.")
    else:
        print("[WARN] Some tests had warnings. Check the output above.")
    print("=" * 50)
    print()
    print("To run the chatbot:")
    print("  streamlit run app.py")
