import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, Optional
from knowledge_base import KnowledgeBase
from intent_detector import IntentDetector
from entity_extractor import EntityExtractor
from llm_fallback import LLMFallback

st.set_page_config(
    page_title="College Helpdesk Chatbot",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "kb" not in st.session_state:
    st.session_state.kb = KnowledgeBase()

if "intent_detector" not in st.session_state:
    st.session_state.intent_detector = IntentDetector()

if "entity_extractor" not in st.session_state:
    st.session_state.entity_extractor = EntityExtractor()

if "llm" not in st.session_state:
    provider = st.session_state.get("llm_provider", "ollama")
    model = st.session_state.get("llm_model", "llama2")
    st.session_state.llm = LLMFallback(provider=provider, model=model)

if "context" not in st.session_state:
    st.session_state.context = {
        "department": None,
        "semester": None,
        "last_intent": None
    }


def format_timetable(data, day=None):
    if day:
        classes = data.get(day, [])
        if classes:
            return f"Classes on {day}:\n" + "\n".join([f"  {cls}" for cls in classes])
        else:
            return f"No classes scheduled for {day}."
    else:
        response = "Weekly Timetable:\n\n"
        for day_name, classes in data.items():
            if classes:
                response += f"{day_name}:\n"
                response += "\n".join([f"  {cls}" for cls in classes]) + "\n\n"
        return response


def format_exam(data):
    response = "Exam Schedule:\n\n"
    response += f"Start Date: {data.get('start_date', 'N/A')}\n"
    response += f"End Date: {data.get('end_date', 'N/A')}\n"
    response += f"Subjects:\n"
    for subject in data.get('subjects', []):
        response += f"  {subject}\n"
    return response


def get_answer(query, context):
    intent, confidence = st.session_state.intent_detector.detect_intent(query)
    entities = st.session_state.entity_extractor.extract_all(query)
    
    dept = entities.get("department") or context.get("department")
    sem = entities.get("semester") or context.get("semester")
    day = entities.get("day")
    date = entities.get("date")
    exam_type = entities.get("exam_type") or context.get("exam_type")
    
    if dept:
        context["department"] = dept
    if sem:
        context["semester"] = sem
    if intent:
        context["last_intent"] = intent
    
    if not intent or confidence < 0.3:
        if context.get("last_intent"):
            if dept or sem or day:
                intent = context.get("last_intent")
                confidence = 0.5
    
    if intent == "timetable" and confidence > 0.3:
        if not dept:
            if context.get("department"):
                dept = context["department"]
            else:
                return "I need to know which department you're asking about. Please specify (e.g., CSE, ECE)."
        
        if not sem:
            if context.get("semester"):
                sem = context["semester"]
            else:
                return "I need to know which semester. Please specify (e.g., Semester 3)."
        
        timetable_data = st.session_state.kb.get_timetable(dept, sem, day)
        
        if timetable_data:
            if day:
                classes = timetable_data if isinstance(timetable_data, list) else None
                if classes:
                    return format_timetable({day: classes}, day)
                else:
                    return f"No classes scheduled for {day} for {dept} {sem}."
            else:
                return format_timetable(timetable_data)
        else:
            return f"Sorry, I couldn't find timetable information for {dept} {sem}. Please check if the department and semester are correct."
    
    elif intent == "exam" and confidence > 0.3:
        if not exam_type:
            exam_type = "mid_semester"
        
        if not dept:
            if context.get("department"):
                dept = context["department"]
            else:
                return "I need to know which department. Please specify (e.g., CSE, ECE)."
        
        if not sem:
            if context.get("semester"):
                sem = context["semester"]
            else:
                return "I need to know which semester. Please specify (e.g., Semester 3)."
        
        exam_data = st.session_state.kb.get_exam_schedule(exam_type, dept, sem)
        
        if exam_data:
            exam_name = exam_type.replace("_", " ").title()
            return f"{exam_name} Exam Schedule for {dept} {sem}:\n\n" + format_exam(exam_data)
        else:
            return f"Sorry, I couldn't find {exam_type} exam schedule for {dept} {sem}."
    
    elif intent == "holiday" and confidence > 0.3:
        if date:
            holiday_name = st.session_state.kb.check_holiday(date)
            if holiday_name:
                return f"Yes, {date} is a holiday: {holiday_name}"
            else:
                return f"No, {date} is not a holiday."
        else:
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            holiday_name = st.session_state.kb.check_holiday(tomorrow)
            if holiday_name:
                return f"Yes, tomorrow ({tomorrow}) is a holiday: {holiday_name}"
            else:
                return f"No, tomorrow ({tomorrow}) is not a holiday."
    
    elif intent == "credits" and confidence > 0.3:
        credit_info = st.session_state.kb.get_credit_requirements()
        response = "Credit Requirements:\n\n"
        response += f"Minimum credits to pass: {credit_info.get('minimum_credits_to_pass', 'N/A')}\n"
        response += f"Credits per semester: {credit_info.get('credits_per_semester', 'N/A')}\n"
        response += f"Total credits for degree: {credit_info.get('total_credits_for_degree', 'N/A')}\n"
        response += f"Minimum attendance required: {credit_info.get('minimum_attendance_percentage', 'N/A')}%\n"
        response += f"Backlogs allowed: {credit_info.get('backlog_allowed', 'N/A')}\n"
        return response
    
    elif intent == "attendance" and confidence > 0.3:
        attendance_info = st.session_state.kb.get_attendance_rules()
        response = "Attendance Rules:\n\n"
        response += f"Minimum attendance required: {attendance_info.get('minimum_percentage', 'N/A')}%\n"
        response += f"Below {attendance_info.get('minimum_percentage', 75)}%: {attendance_info.get('consequences_below_75', 'N/A')}\n"
        response += f"Medical leave allowed: {attendance_info.get('medical_leave_allowed', 'N/A')}\n"
        response += f"Leave application process: {attendance_info.get('leave_application_process', 'N/A')}\n"
        return response
    
    elif intent == "contact" and confidence > 0.3:
        if not dept:
            dept = entities.get("department") or context.get("department")
            if not dept:
                return "I need to know which department. Please specify (e.g., CSE, ECE)."
        
        contact_info = st.session_state.kb.get_department_contact(dept)
        
        if contact_info:
            response = f"{dept} Department Contacts:\n\n"
            response += f"HOD: {contact_info.get('HOD', 'N/A')}\n"
            response += f"Email: {contact_info.get('email', 'N/A')}\n"
            response += f"Phone: {contact_info.get('phone', 'N/A')}\n"
            response += f"Office Location: {contact_info.get('office_location', 'N/A')}\n"
            return response
        else:
            return f"Sorry, I couldn't find contact information for {dept} department."
    
    else:
        if context.get("last_intent") == "timetable" and (dept or context.get("department")):
            return "I have the department. Please also specify the semester (e.g., Semester 3)."
        
        if not st.session_state.llm.is_available():
            suggestions = []
            if context.get("last_intent"):
                suggestions.append(f"You were asking about {context.get('last_intent')}.")
            if context.get("department"):
                suggestions.append(f"Department: {context.get('department')}")
            if context.get("semester"):
                suggestions.append(f"Semester: {context.get('semester')}")
            
            msg = "I'm having trouble understanding your query."
            if suggestions:
                msg += " " + " ".join(suggestions)
            msg += " Please try rephrasing your question or use one of the FAQ buttons in the sidebar."
            
            return msg
        
        context_str = f"Department: {context.get('department')}, Semester: {context.get('semester')}"
        return st.session_state.llm.get_response(query, context_str)


def main():
    st.title("College Helpdesk Chatbot")
    st.markdown("Ask me about timetables, exams, holidays, credits, attendance, and department contacts!")
    
    with st.sidebar:
        st.header("Settings")
        
        llm_provider = st.selectbox(
            "LLM Provider",
            ["ollama", "openai"],
            index=0 if st.session_state.get("llm_provider", "ollama") == "ollama" else 1
        )
        
        llm_model = st.text_input(
            "LLM Model",
            value=st.session_state.get("llm_model", "llama2" if llm_provider == "ollama" else "gpt-3.5-turbo"),
            help="Model name (e.g., llama2, mistral for Ollama or gpt-3.5-turbo for OpenAI)"
        )
        
        if st.button("Update LLM Settings"):
            st.session_state.llm_provider = llm_provider
            st.session_state.llm_model = llm_model
            st.session_state.llm = LLMFallback(provider=llm_provider, model=llm_model)
            st.success("Settings updated!")
        
        st.divider()
        
        st.header("Supported Queries")
        st.markdown("""
        - **Timetable**: "What is tomorrow's timetable for CSE sem 3?"
        - **Exams**: "When are mid-semester exams?"
        - **Holidays**: "Is tomorrow a holiday?"
        - **Credits**: "How many credits are needed to pass?"
        - **Attendance**: "What is the minimum attendance required?"
        - **Contacts**: "Who is HOD of CSE?"
        """)
        
        st.divider()
        
        st.header("FAQ Quick Buttons")
        faq_questions = [
            ("Timetable", "What is tomorrow's timetable for CSE sem 3?"),
            ("Exams", "When are mid-semester exams for CSE semester 3?"),
            ("Holidays", "Is tomorrow a holiday?"),
            ("Credits", "How many credits are needed to pass?"),
            ("Attendance", "What is the minimum attendance required?"),
            ("Contact", "Who is HOD of CSE?")
        ]
        
        for label, question in faq_questions:
            if st.button(label, key=f"faq_{hash(question)}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": question})
                response = get_answer(question, st.session_state.context)
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
        
        st.divider()
        
        st.header("Sample Questions")
        sample_questions = [
            "What is tomorrow's timetable for CSE sem 3?",
            "When are mid-semester exams for CSE semester 3?",
            "Is tomorrow a holiday?",
            "How many credits are needed to pass?",
            "What is the minimum attendance required?",
            "Who is HOD of CSE?",
            "What about Tuesday?",
            "And for semester 4?"
        ]
        
        for q in sample_questions:
            if st.button(q, key=f"sample_{hash(q)}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": q})
                response = get_answer(q, st.session_state.context)
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
        
        st.divider()
        
        st.header("Export Chat")
        if st.button("Download Chat History", use_container_width=True):
            if st.session_state.messages:
                chat_text = "Chat History\n" + "="*50 + "\n\n"
                for msg in st.session_state.messages:
                    role = "You" if msg["role"] == "user" else "Bot"
                    chat_text += f"{role}: {msg['content']}\n\n"
                
                filename = f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                st.download_button(
                    label="Download",
                    data=chat_text,
                    file_name=filename,
                    mime="text/plain",
                    key="download_chat"
                )
            else:
                st.info("No chat history to export")
        
        if st.button("Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.session_state.context = {"department": None, "semester": None, "last_intent": None}
            st.rerun()
        
        st.divider()
        st.markdown("**Admin Panel:** Run `streamlit run admin.py`")
    
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        if prompt := st.chat_input("Ask me anything about the college..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = get_answer(prompt, st.session_state.context)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()
