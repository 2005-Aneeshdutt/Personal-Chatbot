import streamlit as st
import json
import os
from datetime import datetime
from knowledge_base import KnowledgeBase


def load_json_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        st.error(f"Error: Invalid JSON in {filepath}")
        return {}


def save_json_file(filepath, data):
    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    st.success(f"Saved to {filepath}")


def main():
    st.set_page_config(
        page_title="Admin Panel - College Helpdesk",
        page_icon="",
        layout="wide"
    )
    
    st.title("Admin Panel - Knowledge Base Editor")
    st.markdown("Edit college information without touching code files.")
    
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False
    
    if not st.session_state.admin_authenticated:
        password = st.text_input("Enter Admin Password:", type="password", key="admin_pwd")
        if st.button("Login"):
            if password == "admin123":
                st.session_state.admin_authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password!")
        st.info("Default password: admin123 (change this in code for production!)")
        return
    
    if st.sidebar.button("Logout"):
        st.session_state.admin_authenticated = False
        st.rerun()
    
    data_dir = "data"
    tabs = st.tabs(["Timetable", "Exams", "Holidays", "Academic Rules", "View All Data"])
    
    with tabs[0]:
        st.header("Edit Timetable")
        
        timetable_file = os.path.join(data_dir, "timetable.json")
        timetable_data = load_json_file(timetable_file)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Add/Edit Timetable Entry")
            
            departments = list(timetable_data.keys()) if timetable_data else []
            new_dept = st.text_input("Department (e.g., CSE, ECE)", key="timetable_dept")
            new_sem = st.text_input("Semester (e.g., Semester 3)", key="timetable_sem")
            
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            selected_day = st.selectbox("Day of Week", days, key="timetable_day")
            
            classes_input = st.text_area(
                "Classes (one per line or comma-separated)",
                help="Example: DSA, Math, Physics",
                key="timetable_classes"
            )
            
            if st.button("Add/Update Timetable Entry"):
                if new_dept and new_sem and selected_day:
                    dept_upper = new_dept.upper()
                    
                    if dept_upper not in timetable_data:
                        timetable_data[dept_upper] = {}
                    if new_sem not in timetable_data[dept_upper]:
                        timetable_data[dept_upper][new_sem] = {}
                    
                    if classes_input:
                        classes = [c.strip() for c in classes_input.replace('\n', ',').split(',') if c.strip()]
                        timetable_data[dept_upper][new_sem][selected_day] = classes
                        save_json_file(timetable_file, timetable_data)
                    else:
                        st.warning("Please enter at least one class")
                else:
                    st.error("Please fill all required fields")
        
        with col2:
            st.subheader("Current Timetable Data")
            st.json(timetable_data)
            
            if st.button("Reload from File", key="reload_timetable"):
                timetable_data = load_json_file(timetable_file)
                st.rerun()
    
    with tabs[1]:
        st.header("Edit Exam Schedule")
        
        exams_file = os.path.join(data_dir, "exams.json")
        exams_data = load_json_file(exams_file)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Add/Edit Exam Entry")
            
            exam_type = st.selectbox("Exam Type", ["mid_semester", "end_semester"], key="exam_type")
            exam_dept = st.text_input("Department", key="exam_dept")
            exam_sem = st.text_input("Semester", key="exam_sem")
            start_date = st.date_input("Start Date", key="exam_start")
            end_date = st.date_input("End Date", key="exam_end")
            
            subjects_input = st.text_area(
                "Subjects (one per line or comma-separated)",
                key="exam_subjects"
            )
            
            if st.button("Add/Update Exam Entry"):
                if exam_dept and exam_sem:
                    dept_upper = exam_dept.upper()
                    
                    if exam_type not in exams_data:
                        exams_data[exam_type] = {}
                    if dept_upper not in exams_data[exam_type]:
                        exams_data[exam_type][dept_upper] = {}
                    
                    subjects = [s.strip() for s in subjects_input.replace('\n', ',').split(',') if s.strip()]
                    
                    exams_data[exam_type][dept_upper][exam_sem] = {
                        "start_date": start_date.strftime("%Y-%m-%d"),
                        "end_date": end_date.strftime("%Y-%m-%d"),
                        "subjects": subjects
                    }
                    save_json_file(exams_file, exams_data)
                else:
                    st.error("Please fill all required fields")
        
        with col2:
            st.subheader("Current Exam Data")
            st.json(exams_data)
    
    with tabs[2]:
        st.header("Edit Holidays")
        
        holidays_file = os.path.join(data_dir, "holidays.json")
        holidays_data = load_json_file(holidays_file)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Add/Edit Holiday")
            
            year = st.selectbox("Year", [str(y) for y in range(2020, 2030)], index=4, key="holiday_year")
            holiday_date = st.date_input("Holiday Date", key="holiday_date")
            holiday_name = st.text_input("Holiday Name", key="holiday_name")
            
            if st.button("Add/Update Holiday"):
                if holiday_name:
                    if year not in holidays_data:
                        holidays_data[year] = {}
                    
                    month_day = holiday_date.strftime("%m-%d")
                    holidays_data[year][month_day] = holiday_name
                    save_json_file(holidays_file, holidays_data)
                else:
                    st.error("Please enter holiday name")
        
        with col2:
            st.subheader("Current Holidays")
            st.json(holidays_data)
    
    with tabs[3]:
        st.header("Edit Academic Rules")
        
        rules_file = os.path.join(data_dir, "academic_rules.json")
        rules_data = load_json_file(rules_file)
        
        st.subheader("Credit Requirements")
        col1, col2 = st.columns(2)
        
        with col1:
            min_credits = st.number_input("Minimum Credits to Pass", min_value=0, value=rules_data.get("credit_requirements", {}).get("minimum_credits_to_pass", 120), key="min_credits")
            credits_per_sem = st.number_input("Credits per Semester", min_value=0, value=rules_data.get("credit_requirements", {}).get("credits_per_semester", 20), key="credits_sem")
            total_credits = st.number_input("Total Credits for Degree", min_value=0, value=rules_data.get("credit_requirements", {}).get("total_credits_for_degree", 160), key="total_credits")
        
        with col2:
            min_attendance = st.number_input("Minimum Attendance %", min_value=0, max_value=100, value=rules_data.get("credit_requirements", {}).get("minimum_attendance_percentage", 75), key="min_att")
            backlog_allowed = st.number_input("Backlogs Allowed", min_value=0, value=rules_data.get("credit_requirements", {}).get("backlog_allowed", 4), key="backlog")
        
        st.subheader("Department Contacts")
        dept_contact = st.selectbox("Select Department", ["CSE", "ECE", "ME"], key="contact_dept")
        
        col3, col4 = st.columns(2)
        with col3:
            hod_name = st.text_input("HOD Name", value=rules_data.get("department_contacts", {}).get(dept_contact, {}).get("HOD", ""), key="hod_name")
            hod_email = st.text_input("Email", value=rules_data.get("department_contacts", {}).get(dept_contact, {}).get("email", ""), key="hod_email")
        with col4:
            hod_phone = st.text_input("Phone", value=rules_data.get("department_contacts", {}).get(dept_contact, {}).get("phone", ""), key="hod_phone")
            hod_location = st.text_input("Office Location", value=rules_data.get("department_contacts", {}).get(dept_contact, {}).get("office_location", ""), key="hod_loc")
        
        if st.button("Save Academic Rules"):
            if "credit_requirements" not in rules_data:
                rules_data["credit_requirements"] = {}
            if "department_contacts" not in rules_data:
                rules_data["department_contacts"] = {}
            if dept_contact not in rules_data["department_contacts"]:
                rules_data["department_contacts"][dept_contact] = {}
            
            rules_data["credit_requirements"] = {
                "minimum_credits_to_pass": int(min_credits),
                "credits_per_semester": int(credits_per_sem),
                "total_credits_for_degree": int(total_credits),
                "minimum_attendance_percentage": int(min_attendance),
                "backlog_allowed": int(backlog_allowed)
            }
            
            rules_data["department_contacts"][dept_contact] = {
                "HOD": hod_name,
                "email": hod_email,
                "phone": hod_phone,
                "office_location": hod_location
            }
            
            save_json_file(rules_file, rules_data)
    
    with tabs[4]:
        st.header("View All Knowledge Base Data")
        
        kb = KnowledgeBase()
        
        st.subheader("Available Departments")
        st.write(", ".join(kb.get_all_departments()) if kb.get_all_departments() else "No departments found")
        
        st.subheader("Data Summary")
        st.write(f"Timetable entries: {len(timetable_data)} departments")
        st.write(f"Exam types: {len(exams_data)}")
        st.write(f"Holiday years: {len(holidays_data)}")
        st.write(f"Rules configured: Yes" if rules_data else "Rules configured: No")


if __name__ == "__main__":
    main()
