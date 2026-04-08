# Quick Start Guide

## 🚀 Get Started in 3 Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Choose Your LLM (Pick One)

**Option A: Use Ollama (Recommended - Local & Free)**
```bash
# Install Ollama from https://ollama.ai
# Then pull a model:
ollama pull llama2
```

**Option B: Use OpenAI (Requires API Key)**
```bash
# Set your API key:
# Windows PowerShell:
$env:OPENAI_API_KEY="your-key-here"

# Windows CMD:
set OPENAI_API_KEY=your-key-here

# Linux/Mac:
export OPENAI_API_KEY="your-key-here"
```

### 3. Run the App
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📝 Example Questions to Try

- "What is tomorrow's timetable for CSE sem 3?"
- "When are mid-semester exams?"
- "Is tomorrow a holiday?"
- "How many credits are needed to pass?"
- "Who is HOD of CSE?"
- "What about Tuesday?" (follow-up question)

## ⚙️ Configuration

- Change LLM provider in the sidebar
- Update data in `data/*.json` files
- Customize intents in `intent_detector.py`

## 🧪 Test Setup

Run the test script to verify everything works:
```bash
python test_setup.py
```

Enjoy your chatbot! 🎓
