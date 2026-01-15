# 🤖 LLM Integration - Complete Guide

## 📊 Overview: Two Options for LLM

The chatbot supports **TWO** LLM providers:

1. **OpenAI API** (Cloud-based) - Uses HTTP API calls
2. **Ollama** (Local) - Uses local HTTP API on your machine

**LLM is ONLY used when:**
- Knowledge base doesn't have the answer
- Query doesn't match any intent
- You need to handle general questions

---

## 🔄 When LLM is Called

### Flow Decision Tree:

```
User Query
    ↓
Intent Detected? ──No──→ LLM Fallback
    │ Yes
    ↓
Match KB Intent? ──No──→ LLM Fallback
    │ Yes
    ↓
Found in KB? ──No──→ LLM Fallback
    │ Yes
    ↓
Return KB Answer ✅
```

### Example Scenarios:

**Scenario 1: KB Has Answer (No LLM)**
```
Query: "What is tomorrow's timetable for CSE sem 3?"
→ Intent: "timetable" ✓
→ Found in KB ✓
→ Returns: Timetable data (No LLM call)
```

**Scenario 2: LLM Needed**
```
Query: "What is the library timing?"
→ Intent: None (no pattern match)
→ Not in KB
→ Calls LLM → "The library is open from 8 AM to 8 PM..."
```

---

## 🌐 Option 1: OpenAI API (Cloud-Based)

### How It Works:

**1. API Key Setup** (llm_fallback.py:30)
```python
self.api_key = os.getenv("OPENAI_API_KEY", "")
# Reads from environment variable or .env file
```

**2. API Call** (llm_fallback.py:55-75)
```python
from openai import OpenAI

client = OpenAI(api_key=self.api_key)

response = client.chat.completions.create(
    model="gpt-3.5-turbo",          # Model name
    messages=[
        {"role": "system", "content": "You are a college helpdesk assistant..."},
        {"role": "user", "content": "What is library timing?"}
    ],
    max_tokens=200,                  # Limit response length
    temperature=0.7                  # Creativity (0-1)
)

return response.choices[0].message.content
```

### What Happens Behind the Scenes:

```
Your Code
    ↓
OpenAI Python Library
    ↓
HTTP POST Request
POST https://api.openai.com/v1/chat/completions
Headers:
  Authorization: Bearer sk-xxxxx... (your API key)
  Content-Type: application/json
Body:
{
  "model": "gpt-3.5-turbo",
  "messages": [...],
  "max_tokens": 200,
  "temperature": 0.7
}
    ↓
OpenAI Servers (Cloud)
    ↓
HTTP Response
{
  "choices": [{
    "message": {
      "content": "The library is open from..."
    }
  }]
}
    ↓
Your Code Receives Response
```

### Setup Instructions:

**Step 1: Get API Key**
- Go to: https://platform.openai.com/api-keys
- Create new secret key
- Copy the key (starts with `sk-...`)

**Step 2: Set Environment Variable**

Windows PowerShell:
```powershell
$env:OPENAI_API_KEY="sk-your-key-here"
```

Windows CMD:
```cmd
set OPENAI_API_KEY=sk-your-key-here
```

Linux/Mac:
```bash
export OPENAI_API_KEY="sk-your-key-here"
```

**Step 3: Or Use .env File**
```bash
# Create .env file
OPENAI_API_KEY=sk-your-key-here
```

**Step 4: Configure in App**
- Open sidebar in chatbot
- Select "openai" from dropdown
- Enter model: `gpt-3.5-turbo`
- Click "Update LLM Settings"

### API Costs:
- **gpt-3.5-turbo**: ~$0.0015 per 1K tokens (very cheap!)
- Example: 200 tokens = ~$0.0003 per query
- First $5 free credits for new accounts

### Pros & Cons:

**✅ Pros:**
- No installation needed
- Fast responses
- Always up-to-date models
- Easy to use

**❌ Cons:**
- Requires internet
- Costs money (very cheap though)
- Needs API key
- Data sent to cloud

---

## 💻 Option 2: Ollama (Local)

### How It Works:

**1. Local Server** (llm_fallback.py:82-106)
```python
import requests

url = "http://localhost:11434/api/generate"

payload = {
    "model": "llama2",
    "prompt": "You are a college helpdesk assistant...\n\nUser: What is library timing?\n\nAssistant:",
    "stream": False
}

response = requests.post(url, json=payload, timeout=30)
return response.json().get("response")
```

### What Happens Behind the Scenes:

```
Your Code
    ↓
HTTP POST Request
POST http://localhost:11434/api/generate
Headers:
  Content-Type: application/json
Body:
{
  "model": "llama2",
  "prompt": "You are a college helpdesk assistant...\n\nUser: What is library timing?\n\nAssistant:",
  "stream": false
}
    ↓
Ollama Server (Running Locally on Port 11434)
    ↓
Local LLM Model (llama2, mistral, etc.)
Processes on YOUR computer
    ↓
HTTP Response
{
  "response": "The library is open from..."
}
    ↓
Your Code Receives Response
```

### Setup Instructions:

**Step 1: Install Ollama**
- Download from: https://ollama.ai
- Install (Windows/Mac/Linux)

**Step 2: Download Model**
```bash
ollama pull llama2
# or
ollama pull mistral
# or
ollama pull codellama
```

**Step 3: Verify It's Running**
```bash
ollama list
# Should show downloaded models
```

**Step 4: Test Server**
```bash
# Check if Ollama API is accessible
curl http://localhost:11434/api/tags
```

**Step 5: Configure in App**
- Open sidebar in chatbot
- Select "ollama" from dropdown
- Enter model: `llama2` (or your downloaded model)
- Click "Update LLM Settings"

### How Ollama Works:

- **Local Server**: Runs on your computer (port 11434)
- **No Internet**: All processing happens locally
- **Free**: No API costs
- **Privacy**: Data never leaves your machine
- **Models**: Downloads models locally (3-7GB each)

### Available Models:

```bash
# Popular models you can use:
ollama pull llama2         # 3.8GB - Good general purpose
ollama pull mistral        # 4.1GB - Fast and efficient
ollama pull codellama      # 3.8GB - Code-focused
ollama pull phi            # 1.6GB - Small and fast
ollama pull gemma          # 2.0GB - Google's model
```

### Pros & Cons:

**✅ Pros:**
- **Free** (no API costs)
- **Private** (data stays local)
- **No internet** needed
- **Multiple models** available

**❌ Cons:**
- Requires installation
- Needs disk space (3-7GB per model)
- Slower than OpenAI
- Uses your computer's resources

---

## 🔧 Code Walkthrough

### Initialization (llm_fallback.py:14-30)

```python
def __init__(self, provider: str = "openai", model: str = "gpt-3.5-turbo"):
    self.provider = provider.lower()  # "openai" or "ollama"
    self.model = model                # Model name
    
    # Try to load .env file for API keys
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    # Get OpenAI API key from environment
    self.api_key = os.getenv("OPENAI_API_KEY", "")
```

### Main Entry Point (llm_fallback.py:32-53)

```python
def get_response(self, query: str, context: Optional[str] = None) -> str:
    # Create system prompt
    system_prompt = "You are a college helpdesk assistant. Answer in short and simple language."
    
    # Add conversation context if available
    if context:
        system_prompt += f"\n\nPrevious conversation context: {context}"
    
    # Route to appropriate provider
    if self.provider == "openai":
        return self._get_openai_response(query, system_prompt)
    elif self.provider == "ollama":
        return self._get_ollama_response(query, system_prompt)
```

### OpenAI Implementation (llm_fallback.py:55-80)

```python
def _get_openai_response(self, query: str, system_prompt: str) -> str:
    from openai import OpenAI
    
    # Check if API key exists
    if not self.api_key:
        return "OpenAI API key not found..."
    
    # Create OpenAI client
    client = OpenAI(api_key=self.api_key)
    
    # Make API call
    response = client.chat.completions.create(
        model=self.model,                    # e.g., "gpt-3.5-turbo"
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        max_tokens=200,                      # Limit response length
        temperature=0.7                      # Creativity level
    )
    
    # Extract and return response
    return response.choices[0].message.content.strip()
```

**API Request Details:**
- **URL**: `https://api.openai.com/v1/chat/completions`
- **Method**: POST
- **Headers**: 
  - `Authorization: Bearer sk-xxxxx`
  - `Content-Type: application/json`
- **Body**: JSON with model, messages, parameters

### Ollama Implementation (llm_fallback.py:82-106)

```python
def _get_ollama_response(self, query: str, system_prompt: str) -> str:
    import requests
    
    # Ollama API endpoint (localhost)
    url = "http://localhost:11434/api/generate"
    
    # Prepare prompt
    prompt = f"{system_prompt}\n\nUser: {query}\n\nAssistant:"
    
    # Make HTTP POST request
    payload = {
        "model": self.model,        # e.g., "llama2"
        "prompt": prompt,
        "stream": False             # Get complete response
    }
    
    response = requests.post(url, json=payload, timeout=30)
    
    # Check response
    if response.status_code == 200:
        return response.json().get("response")
    else:
        return "Ollama server not accessible..."
```

**API Request Details:**
- **URL**: `http://localhost:11434/api/generate`
- **Method**: POST
- **Headers**: `Content-Type: application/json`
- **Body**: JSON with model and prompt

### Availability Check (llm_fallback.py:108-119)

```python
def is_available(self) -> bool:
    if self.provider == "openai":
        # Check if API key exists
        return bool(self.api_key)
    
    elif self.provider == "ollama":
        # Check if Ollama server is running
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    return False
```

---

## 🎯 How LLM is Used in Main App

### Integration Point (app.py:226-241)

```python
else:
    # Fallback to LLM when:
    # 1. No intent matched
    # 2. Query not in knowledge base
    
    # Check if we should try KB first with context
    if context.get("last_intent") == "timetable" and (dept or context.get("department")):
        return "I have the department. Please also specify the semester..."
    
    # Check if LLM is available
    if not st.session_state.llm.is_available():
        # LLM not available, give helpful message
        return "I'm having trouble understanding your query. Please try rephrasing..."
    
    # Call LLM with context
    context_str = f"Department: {context.get('department')}, Semester: {context.get('semester')}"
    return st.session_state.llm.get_response(query, context_str)
```

---

## 📊 Comparison Table

| Feature | OpenAI API | Ollama |
|---------|-----------|--------|
| **Location** | Cloud | Local |
| **Internet** | Required | Not required |
| **Cost** | ~$0.0015/1K tokens | Free |
| **Speed** | Fast (~1-2s) | Slower (~2-10s) |
| **Setup** | API key only | Install + download model |
| **Privacy** | Data sent to cloud | Data stays local |
| **Models** | Many (GPT-3.5, GPT-4) | Many (Llama2, Mistral) |
| **API Type** | REST API | Local HTTP API |

---

## 🔍 Testing LLM Integration

### Test OpenAI:

```python
from llm_fallback import LLMFallback

llm = LLMFallback(provider="openai", model="gpt-3.5-turbo")
response = llm.get_response("What is the library timing?")
print(response)
```

### Test Ollama:

```python
from llm_fallback import LLMFallback

llm = LLMFallback(provider="ollama", model="llama2")
response = llm.get_response("What is the library timing?")
print(response)
```

### Check Availability:

```python
llm = LLMFallback(provider="ollama")
if llm.is_available():
    print("Ollama is running!")
else:
    print("Ollama is not running")
```

---

## 🚨 Error Handling

### Common Errors:

**1. OpenAI API Key Missing**
```
Error: "OpenAI API key not found..."
Solution: Set OPENAI_API_KEY environment variable
```

**2. Ollama Not Running**
```
Error: "Cannot connect to Ollama..."
Solution: Start Ollama or install it
```

**3. Model Not Found (Ollama)**
```
Error: "Model not found"
Solution: Run: ollama pull <model-name>
```

**4. Network Error**
```
Error: "Connection timeout"
Solution: Check internet (OpenAI) or Ollama server (local)
```

---

## 💡 Best Practices

1. **For Development**: Use Ollama (free, local)
2. **For Production**: Use OpenAI (faster, more reliable)
3. **For Privacy**: Use Ollama (data stays local)
4. **For Cost Control**: Use Ollama (no per-query cost)

---

## 🎯 Summary

**LLM is used as a FALLBACK only when:**
- ✅ Knowledge base doesn't have the answer
- ✅ Query doesn't match any intent pattern
- ✅ Need to handle general/unknown questions

**Two options available:**
1. **OpenAI API** - Cloud-based, requires API key, costs money
2. **Ollama** - Local, free, requires installation

**Both use HTTP APIs:**
- OpenAI: `https://api.openai.com/v1/chat/completions`
- Ollama: `http://localhost:11434/api/generate`

**The system automatically handles:**
- API key loading (.env or environment variables)
- Error handling
- Timeout management
- Response parsing

---

**Bottom Line:** You're using **HTTP REST APIs** - OpenAI's cloud API or Ollama's local API. The chatbot calls these APIs only when the knowledge base can't answer the question!
