# 🎓 College Helpdesk Chatbot

<div align="center">

**An intelligent conversational AI assistant for college students**  
*Answering queries about timetables, exams, holidays, and academic information*

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 📖 Overview

The **College Helpdesk Chatbot** is a production-ready conversational AI system designed to assist college students with common academic queries. Built with Streamlit and powered by structured knowledge bases with optional LLM fallback, it provides instant, accurate answers about class schedules, exam dates, holidays, credit requirements, attendance policies, and department contacts.

### Key Highlights

- ⚡ **Fast Responses**: Knowledge base queries return instantly without LLM overhead
- 🧠 **Smart Context Management**: Remembers conversation history for natural follow-up questions
- 🔧 **Easy Customization**: JSON-based knowledge base makes updates simple
- 🎯 **Modular Architecture**: Clean, maintainable codebase with separation of concerns
- 🌐 **Dual LLM Support**: Works with OpenAI (cloud) or Ollama (local) for general queries
- 💬 **User-Friendly UI**: Beautiful chat interface with FAQ buttons and sample questions

---

## ✨ Features

### Core Capabilities

| Feature | Description |
|---------|-------------|
| 📅 **Timetable Queries** | Get class schedules by department, semester, and day |
| 📝 **Exam Schedules** | Query mid-semester and end-semester exam dates |
| 🎉 **Holiday Calendar** | Check if specific dates are holidays |
| 📊 **Academic Rules** | Access credit requirements and attendance policies |
| 📞 **Department Contacts** | Find HOD information and department details |
| 💡 **FAQ Quick Access** | One-click buttons for common questions |

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

## 🔧 Configuration

### LLM Setup (Optional)

The chatbot works **perfectly fine without LLM** for all knowledge base queries. LLM is only needed for general questions not in the knowledge base.

#### Option A: OpenAI (Cloud-based)

1. Get an API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Set environment variable:
   ```bash
   # Windows PowerShell
   $env:OPENAI_API_KEY="your-api-key-here"
   
   # Windows CMD
   set OPENAI_API_KEY=your-api-key-here
   
   # Linux/Mac
   export OPENAI_API_KEY="your-api-key-here"
   ```
3. In the app sidebar, select **"openai"** and enter model (e.g., `gpt-3.5-turbo`)

#### Option B: Ollama (Local - Recommended for Privacy)

1. Install Ollama from [ollama.ai](https://ollama.ai)
2. Download a model:
   ```bash
   ollama pull llama2
   # or
   ollama pull mistral
   ```
3. Verify installation:
   ```bash
   ollama list
   ```
4. In the app sidebar, select **"ollama"** and enter model name (e.g., `llama2`)

#### Option C: No LLM (Knowledge Base Only)

The chatbot works excellently without any LLM setup. Simply use queries that match the knowledge base intents (timetable, exams, holidays, credits, attendance, contacts).

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

## 📊 Knowledge Base Format

### Timetable Structure

```json
{
  "CSE": {
    "Semester 3": {
      "Monday": ["DSA", "Math", "Physics"],
      "Tuesday": ["OOPS", "Lab"]
    }
  }
}
```

### Exam Structure

```json
{
  "mid_semester": {
    "CSE": {
      "Semester 3": {
        "start_date": "2024-09-15",
        "end_date": "2024-09-20",
        "subjects": ["DSA", "OOPS", "Operating Systems"]
      }
    }
  }
}
```

### Holiday Structure

```json
{
  "2024": {
    "01-26": "Republic Day",
    "08-15": "Independence Day"
  }
}
```

---

## 🐛 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| **"Module not found"** | Run `pip install -r requirements.txt` |
| **"OpenAI API key not found"** | Set `OPENAI_API_KEY` environment variable or use Ollama |
| **"Cannot connect to Ollama"** | Ensure Ollama is running: `ollama list` or install from [ollama.ai](https://ollama.ai) |
| **"No data found"** | Verify JSON files exist in `data/` directory and are valid JSON |
| **Port already in use** | Streamlit will automatically use the next available port |

### Getting Help

- Run `python test_setup.py` to diagnose setup issues
- Check Streamlit terminal output for error messages
- Verify all JSON files are valid using a JSON validator
- Ensure Python version is 3.8 or higher: `python --version`

---

## 🧪 Testing

### Setup Verification

```bash
python test_setup.py
```

This verifies:
- ✅ All modules import correctly
- ✅ Knowledge base loads properly
- ✅ Intent detection works
- ✅ Entity extraction functions correctly

### Manual Testing

Test each intent type:
- Timetable queries with various departments/semesters
- Exam schedule queries
- Holiday date checks
- Credit and attendance rule queries
- Department contact lookups
- Follow-up questions (context memory)

---

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)**: Fast setup guide
- **[LLM_EXPLAINED.md](LLM_EXPLAINED.md)**: Detailed LLM integration guide

---

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- [ ] Enhanced entity extraction (e.g., using spaCy)
- [ ] Voice input support
- [ ] Multi-language support
- [ ] Database backend option
- [ ] API endpoints for integration
- [ ] Additional intent categories
- [ ] Improved error handling
- [ ] Unit tests and integration tests

### Contributing Guidelines

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE) for educational purposes.

---

## 🙏 Acknowledgments

Built with:
- [Streamlit](https://streamlit.io/) - For the beautiful UI framework
- [OpenAI](https://openai.com/) - For cloud-based LLM capabilities
- [Ollama](https://ollama.ai/) - For local LLM support

---

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review troubleshooting section

---

<div align="center">

**Made with ❤️ for college students**

⭐ **Star this repo if you find it helpful!**

</div>
