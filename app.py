import streamlit as st
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from config_loader import load_config, load_ui_strings
from entity_extractor import EntityExtractor
from intent_detector import IntentDetector
from knowledge_base import KnowledgeBase
from llm_fallback import LLMFallback

_cfg = load_config()
_app_ui = load_ui_strings().get("app", {})
st.set_page_config(
    page_title=_app_ui.get("page_title", "College Helpdesk Chatbot"),
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "kb" not in st.session_state:
    st.session_state.kb = KnowledgeBase()

if "intent_detector" not in st.session_state:
    st.session_state.intent_detector = IntentDetector()

if "entity_extractor" not in st.session_state:
    st.session_state.entity_extractor = EntityExtractor()

_llm_def = _cfg.get("llm_defaults", {})
if "llm_provider" not in st.session_state:
    st.session_state.llm_provider = _llm_def.get("provider", "ollama")
if "llm_model" not in st.session_state:
    if st.session_state.llm_provider == "openai":
        st.session_state.llm_model = _llm_def.get("openai_model", "gpt-3.5-turbo")
    else:
        st.session_state.llm_model = _llm_def.get("ollama_model", "llama2")

if "llm" not in st.session_state:
    st.session_state.llm = LLMFallback(
        provider=st.session_state.llm_provider,
        model=st.session_state.llm_model,
    )

if "context" not in st.session_state:
    st.session_state.context = {
        "department": None,
        "semester": None,
        "last_intent": None,
        "exam_type": None,
    }


def _empty_context() -> Dict[str, Any]:
    return {"department": None, "semester": None, "last_intent": None, "exam_type": None}


def format_timetable(data, day=None, R: Optional[Dict[str, str]] = None):
    R = R or {}
    if day:
        classes = data.get(day, [])
        if classes:
            return R.get("classes_on_day", "Classes on {day}:\n").format(day=day) + "\n".join(
                [f"  {cls}" for cls in classes]
            )
        return R.get("no_classes_day_generic", "No classes scheduled for {day}.").format(day=day)
    response = R.get("weekly_timetable_title", "Weekly Timetable:\n\n")
    for day_name, classes in data.items():
        if classes:
            response += f"{day_name}:\n"
            response += "\n".join([f"  {cls}" for cls in classes]) + "\n\n"
    return response


def format_exam(data, R: Optional[Dict[str, str]] = None):
    R = R or {}
    response = R.get("exam_schedule_block", "Exam Schedule:\n\n")
    response += R.get("exam_start", "Start Date: {start}\n").format(start=data.get("start_date", "N/A"))
    response += R.get("exam_end", "End Date: {end}\n").format(end=data.get("end_date", "N/A"))
    response += R.get("exam_subjects", "Subjects:\n")
    for subject in data.get("subjects", []):
        response += f"  {subject}\n"
    return response


def get_answer(query: str, context: Dict[str, Any]) -> str:
    cfg = load_config()
    max_q = int(cfg.get("limits", {}).get("max_query_chars", 4000))
    if len(query) > max_q:
        query = query[:max_q].rstrip() + "\n\n[Message truncated to max length.]"
    ui = load_ui_strings()
    R = ui.get("responses", {})
    route_min = float(cfg["intent"].get("routing_min_confidence", 0.3))
    recover_conf = float(cfg["intent"].get("context_recovery_confidence", 0.5))
    default_exam = cfg.get("defaults", {}).get("exam_type", "mid_semester")

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
    if exam_type:
        context["exam_type"] = exam_type

    if not intent or confidence < route_min:
        if context.get("last_intent"):
            if dept or sem or day:
                intent = context.get("last_intent")
                confidence = recover_conf

    if intent == "timetable" and confidence > route_min:
        if not dept:
            if context.get("department"):
                dept = context["department"]
            else:
                return R.get(
                    "need_department",
                    "I need to know which department you're asking about.",
                )

        if not sem:
            if context.get("semester"):
                sem = context["semester"]
            else:
                return R.get("need_semester", "I need to know which semester.")

        timetable_data = st.session_state.kb.get_timetable(dept, sem, day)

        if timetable_data:
            if day:
                classes = timetable_data if isinstance(timetable_data, list) else None
                if classes:
                    return format_timetable({day: classes}, day, R)
                return R.get("no_classes_day", "No classes scheduled for {day} for {dept} {sem}.").format(
                    day=day, dept=dept, sem=sem
                )
            return format_timetable(timetable_data, None, R)
        return R.get("timetable_not_found", "Sorry, timetable not found for {dept} {sem}.").format(
            dept=dept, sem=sem
        )

    if intent == "exam" and confidence > route_min:
        if not exam_type:
            exam_type = default_exam

        if not dept:
            if context.get("department"):
                dept = context["department"]
            else:
                return R.get("need_department_short", "I need to know which department.")

        if not sem:
            if context.get("semester"):
                sem = context["semester"]
            else:
                return R.get("need_semester", "I need to know which semester.")

        exam_data = st.session_state.kb.get_exam_schedule(exam_type, dept, sem)

        if exam_data:
            exam_name = exam_type.replace("_", " ").title()
            return (
                f"{exam_name} Exam Schedule for {dept} {sem}:\n\n" + format_exam(exam_data, R)
            )
        return R.get("exam_not_found", "Sorry, exam schedule not found.").format(
            exam_type=exam_type, dept=dept, sem=sem
        )

    if intent == "holiday" and confidence > route_min:
        if date:
            holiday_name = st.session_state.kb.check_holiday(date)
            if holiday_name:
                return R.get("holiday_yes", "Yes, {date} is a holiday: {name}").format(
                    date=date, name=holiday_name
                )
            return R.get("holiday_no", "No, {date} is not a holiday.").format(date=date)
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        holiday_name = st.session_state.kb.check_holiday(tomorrow)
        if holiday_name:
            return R.get("holiday_tomorrow_yes", "Yes, tomorrow is a holiday: {name}").format(
                date=tomorrow, name=holiday_name
            )
        return R.get("holiday_tomorrow_no", "No, tomorrow is not a holiday.").format(date=tomorrow)

    if intent == "credits" and confidence > route_min:
        credit_info = st.session_state.kb.get_credit_requirements()
        response = R.get("credits_header", "Credit Requirements:\n\n")
        response += f"Minimum credits to pass: {credit_info.get('minimum_credits_to_pass', 'N/A')}\n"
        response += f"Credits per semester: {credit_info.get('credits_per_semester', 'N/A')}\n"
        response += f"Total credits for degree: {credit_info.get('total_credits_for_degree', 'N/A')}\n"
        response += f"Minimum attendance required: {credit_info.get('minimum_attendance_percentage', 'N/A')}%\n"
        response += f"Backlogs allowed: {credit_info.get('backlog_allowed', 'N/A')}\n"
        return response

    if intent == "attendance" and confidence > route_min:
        attendance_info = st.session_state.kb.get_attendance_rules()
        response = R.get("attendance_header", "Attendance Rules:\n\n")
        response += f"Minimum attendance required: {attendance_info.get('minimum_percentage', 'N/A')}%\n"
        response += f"Below {attendance_info.get('minimum_percentage', 75)}%: {attendance_info.get('consequences_below_75', 'N/A')}\n"
        response += f"Medical leave allowed: {attendance_info.get('medical_leave_allowed', 'N/A')}\n"
        response += f"Leave application process: {attendance_info.get('leave_application_process', 'N/A')}\n"
        return response

    if intent == "contact" and confidence > route_min:
        if not dept:
            dept = entities.get("department") or context.get("department")
            if not dept:
                return R.get("need_department_short", "I need to know which department.")

        contact_info = st.session_state.kb.get_department_contact(dept)

        if contact_info:
            response = R.get("contact_header", "{dept} Department Contacts:\n\n").format(dept=dept)
            response += f"HOD: {contact_info.get('HOD', 'N/A')}\n"
            response += f"Email: {contact_info.get('email', 'N/A')}\n"
            response += f"Phone: {contact_info.get('phone', 'N/A')}\n"
            response += f"Office Location: {contact_info.get('office_location', 'N/A')}\n"
            return response
        return R.get("contact_not_found", "Sorry, no contact for {dept}.").format(dept=dept)

    if context.get("last_intent") == "timetable" and (dept or context.get("department")):
        return R.get(
            "followup_need_semester",
            "I have the department. Please also specify the semester.",
        )

    if not st.session_state.llm.is_available():
        suggestions = []
        if context.get("last_intent"):
            suggestions.append(f"You were asking about {context.get('last_intent')}.")
        if context.get("department"):
            suggestions.append(f"Department: {context.get('department')}")
        if context.get("semester"):
            suggestions.append(f"Semester: {context.get('semester')}")

        msg = R.get("llm_unavailable_prefix", "I'm having trouble understanding your query.")
        if suggestions:
            msg += " " + " ".join(suggestions)
        msg += R.get(
            "llm_unavailable_suffix",
            " Please try rephrasing or use the FAQ buttons.",
        )
        return msg

    context_str = f"Department: {context.get('department')}, Semester: {context.get('semester')}"
    return st.session_state.llm.get_response(query, context_str)


def main() -> None:
    ui = load_ui_strings()
    app = ui.get("app", {})
    sb = ui.get("sidebar", {})
    exp = ui.get("export", {})

    st.title(app.get("page_title", "College Helpdesk Chatbot"))
    st.markdown(app.get("subtitle_markdown", ""))

    with st.sidebar:
        st.header(sb.get("settings_header", "Settings"))

        with st.expander("System status", expanded=False):
            try:
                depts = st.session_state.kb.get_all_departments()
                st.caption(f"Knowledge base: {len(depts)} department(s) in timetable data")
            except Exception:
                st.caption("Knowledge base: check data/*.json")
            model_ok = st.session_state.intent_detector.model is not None
            st.caption(f"Intent model: {'loaded' if model_ok else 'not loaded — run train_intent_model.py'}")
            st.caption(f"LLM fallback: {'available' if st.session_state.llm.is_available() else 'unavailable'}")

        llm_provider = st.selectbox(
            sb.get("llm_provider_label", "LLM Provider"),
            ["ollama", "openai"],
            index=0 if st.session_state.get("llm_provider", "ollama") == "ollama" else 1,
        )

        llm_model = st.text_input(
            sb.get("llm_model_label", "LLM Model"),
            value=st.session_state.get("llm_model", "llama2"),
            help=sb.get("llm_model_help", ""),
        )

        if st.button(sb.get("update_llm_button", "Update LLM Settings")):
            st.session_state.llm_provider = llm_provider
            st.session_state.llm_model = llm_model
            st.session_state.llm = LLMFallback(provider=llm_provider, model=llm_model)
            st.success(sb.get("update_success", "Settings updated!"))

        st.divider()

        st.header(sb.get("supported_header", "Supported Queries"))
        st.markdown(sb.get("supported_markdown", ""))

        st.divider()

        st.header(sb.get("faq_header", "FAQ Quick Buttons"))
        for label, question in ui.get("faq_buttons", []):
            if st.button(label, key=f"faq_{hash(question)}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": question})
                response = get_answer(question, st.session_state.context)
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()

        st.divider()

        st.header(sb.get("sample_header", "Sample Questions"))
        for q in ui.get("sample_questions", []):
            if st.button(q, key=f"sample_{hash(q)}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": q})
                response = get_answer(q, st.session_state.context)
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()

        st.divider()

        st.header(sb.get("export_header", "Export Chat"))
        if st.button(sb.get("download_history_button", "Download Chat History"), use_container_width=True):
            if st.session_state.messages:
                sep = exp.get("separator", "=" * 50)
                chat_text = f"{exp.get('chat_title', 'Chat History')}\n{sep}\n\n"
                for msg in st.session_state.messages:
                    role = (
                        exp.get("user_label", "You")
                        if msg["role"] == "user"
                        else exp.get("bot_label", "Bot")
                    )
                    chat_text += f"{role}: {msg['content']}\n\n"

                filename = f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                st.download_button(
                    label=sb.get("download_label", "Download"),
                    data=chat_text,
                    file_name=filename,
                    mime="text/plain",
                    key="download_chat",
                )
            else:
                st.info(sb.get("no_history_info", "No chat history"))

        if st.button(sb.get("clear_history_button", "Clear Chat History"), use_container_width=True):
            st.session_state.messages = []
            st.session_state.context = _empty_context()
            st.rerun()

        st.divider()
        st.markdown(sb.get("admin_hint", ""))

    chat_container = st.container()

    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        placeholder = app.get("chat_placeholder", "Ask...")
        if prompt := st.chat_input(placeholder):
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner(app.get("spinner_text", "Thinking...")):
                    response = get_answer(prompt, st.session_state.context)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()
