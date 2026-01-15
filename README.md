# 🎓 College Helpdesk Chatbot

<div align="center">

**An intelligent conversational AI assistant for college students**  
*Answering queries about timetables, exams, holidays, and academic information*

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[Features](#-features) • [Quick Start](#-quick-start) •

</div>

---

## 📖 Overview

The **College Helpdesk Chatbot** is a production-ready conversational AI system designed to assist college students with common academic queries. Built with Streamlit and powered by structured knowledge bases with optional LLM fallback, it provides instant, accurate answers about class schedules, exam dates, holidays, credit requirements, attendance policies, and department contacts.

### Key Highlights

-  **Fast Responses**: Knowledge base queries return instantly without LLM overhead
-  **Smart Context Management**: Remembers conversation history for natural follow-up questions
-  **Easy Customization**: JSON-based knowledge base makes updates simple
-  **Modular Architecture**: Clean, maintainable codebase with separation of concerns
-  **Dual LLM Support**: Works with OpenAI (cloud) or Ollama (local) for general queries
-  **User-Friendly UI**: Beautiful chat interface with FAQ buttons and sample questions

---

## ✨ Features

### Core Capabilities

| Feature | Description |
|---------|-------------|
| **Timetable Queries** | Get class schedules by department, semester, and day |
|  **Exam Schedules** | Query mid-semester and end-semester exam dates |
|  **Holiday Calendar** | Check if specific dates are holidays |
|  **Academic Rules** | Access credit requirements and attendance policies |
|  **Department Contacts** | Find HOD information and department details |
|  **FAQ Quick Access** | One-click buttons for common questions |

### Technical Features

- **Intent Detection**: Pattern-based NLP using regex and keyword matching
- **Entity Extraction**: Automatically extracts department, semester, date, and day from natural language
- **Conversation Memory**: Maintains context across messages for follow-up questions
- **LLM Fallback**: Seamlessly falls back to OpenAI/Ollama for general queries
- **Admin Panel**: Web-based interface to edit knowledge base without code changes
- **Export Functionality**: Download chat history as text files

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** ([Download](https://www.python.org/downloads/))
- **pip** (Python package installer)

### Installation

1. **Clone or download the repository**
   ```bash
   git clone <repository-url>
   cd LLM
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

4. **Access the chatbot**
   
   The app will automatically open in your browser at `http://localhost:8501`

### Verify Installation

Run the test script to verify everything works:

```bash
python test_setup.py
```

Expected output: `[OK] All tests passed! Setup looks good.`

---

## 📋 Supported Queries

The chatbot can answer questions in the following categories:

### 1. Timetable Information
```
"What is tomorrow's timetable for CSE sem 3?"
"Show me Tuesday classes for ECE semester 1"
"What about Tuesday?" (follow-up question)
```

### 2. Exam Schedules
```
"When are mid-semester exams?"
"When are end-semester exams for CSE semester 3?"
```

### 3. Holiday Information
```
"Is tomorrow a holiday?"
"Is 2024-08-15 a holiday?"
```

### 4. Academic Requirements
```
"How many credits are needed to pass?"
"What are the credit requirements?"
```

### 5. Attendance Policies
```
"What is the minimum attendance required?"
"What happens if attendance is below 75%?"
```

### 6. Department Contacts
```
"Who is HOD of CSE?"
"What is the contact for ECE department?"
```

---



## 📁 Project Structure

```
.
├── app.py                      # Main Streamlit application
├── admin.py                    # Admin panel for data management
├── knowledge_base.py           # Knowledge base loader and query handler
├── intent_detector.py          # Intent detection using keywords/regex
├── entity_extractor.py         # Entity extraction (department, semester, etc.)
├── llm_fallback.py             # LLM integration (OpenAI/Ollama)
├── test_setup.py               # Setup verification script
├── requirements.txt            # Python dependencies
├── env_example.txt             # Environment variables template
├── README.md                   # This file
├── QUICKSTART.md               # Quick start guide
├── LLM_EXPLAINED.md            # Detailed LLM integration guide
└── data/                       # Knowledge base JSON files
    ├── timetable.json          # Class schedules
    ├── exams.json              # Exam schedules
    ├── holidays.json           # Holiday calendar
    └── academic_rules.json     # Rules, credits, attendance, contacts
```

---

## 💻 Usage

### Basic Usage

1. **Start the application**
   ```bash
   streamlit run app.py
   ```

2. **Ask questions** in the chat interface
   - Type your query in the input box
   - Use FAQ buttons in the sidebar for quick access
   - Try sample questions for inspiration

3. **Admin Panel** (Optional)
   ```bash
   streamlit run admin.py
   ```
   - Edit knowledge base data through web interface
   - No code changes required
   - Default password: `admin123` (change in `admin.py` for production)

### Example Conversation

```
User: What is tomorrow's timetable for CSE sem 3?
Bot: 📚 Classes on Wednesday:
      • DSA
      • Math
      • Physics

User: What about Tuesday?
Bot: 📚 Classes on Tuesday:
      • OOPS
      • Lab
      • DSA
```

---

## 🏗️ Architecture

### System Flow

```
User Query
    ↓
┌─────────────────────────┐
│  Intent Detection       │ → Identifies query type (timetable, exam, etc.)
└───────────┬─────────────┘
            ↓
┌─────────────────────────┐
│  Entity Extraction      │ → Extracts department, semester, date, day
└───────────┬─────────────┘
            ↓
┌─────────────────────────┐
│  Context Management     │ → Maintains conversation history
└───────────┬─────────────┘
            ↓
    ┌───────┴───────┐
    │               │
┌───▼────┐    ┌────▼──────┐
│Knowledge│    │    LLM     │
│  Base   │    │  Fallback  │
│ (JSON)  │    │(OpenAI/    │
│         │    │ Ollama)    │
└─────────┘    └────────────┘
    │               │
    └───────┬───────┘
            ↓
      Response to User
```

### Key Components

- **IntentDetector**: Pattern-based intent classification using regex
- **EntityExtractor**: Natural language entity extraction (department, semester, date, day)
- **KnowledgeBase**: JSON-based data storage and retrieval system
- **LLMFallback**: Dual-provider LLM integration (OpenAI/Ollama)
- **Context Manager**: Session-based conversation memory

---

## 🔨 Customization

### Adding New Data

Edit JSON files in the `data/` directory or use the admin panel:

- **timetable.json**: Add departments, semesters, class schedules
- **exams.json**: Add exam schedules by type and department
- **holidays.json**: Add holidays by year and date
- **academic_rules.json**: Update credit requirements, attendance rules, contacts

### Adding New Intents

1. Add patterns to `intent_detector.py`:
   ```python
   "new_intent": [
       r"pattern1", r"pattern2"
   ]
   ```

2. Add handling logic in `app.py`'s `get_answer()` function

3. Update knowledge base or LLM fallback as needed

### Modifying LLM Behavior

Edit `llm_fallback.py` to:
- Change system prompts
- Adjust model parameters (temperature, max_tokens)
- Add custom processing logic

---


## 📄 License

This project is open source and available under the [MIT License](LICENSE) for educational purposes.


