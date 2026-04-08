# 🚀 GitHub Repository Setup Guide

## Step-by-Step Instructions to Push to GitHub

### Step 1: Create Repository on GitHub

1. Go to [GitHub](https://github.com/2005-Aneeshdutt)
2. Click the **"+"** button in the top right → **"New repository"**
3. Repository name: `Personal-Chatbot`
4. Description: `Intelligent college helpdesk chatbot with knowledge base and LLM fallback support`
5. Select: **Public**
6. **DO NOT** initialize with README, .gitignore, or license (we already have these)
7. Click **"Create repository"**

### Step 2: Initialize Git (if not already done)

Open PowerShell/Command Prompt in your project directory:

```powershell
cd C:\Users\anees\OneDrive\Desktop\LLM

# Initialize git (if not already done)
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: College Helpdesk Chatbot with knowledge base and LLM support"
```

### Step 3: Connect to GitHub and Push

```powershell
# Add remote repository (replace with your actual username if different)
git remote add origin https://github.com/2005-Aneeshdutt/Personal-Chatbot.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

### Step 4: Verify on GitHub

1. Visit: https://github.com/2005-Aneeshdutt/Personal-Chatbot
2. Verify all files are uploaded
3. Check that README displays correctly
4. Verify LICENSE file is present

---

## Files Included in Repository

- ✅ **README.md** - Professional documentation
- ✅ **LICENSE** - MIT License
- ✅ **.gitignore** - Git ignore rules
- ✅ **requirements.txt** - Python dependencies
- ✅ **app.py** - Main chatbot application
- ✅ **admin.py** - Admin panel
- ✅ **knowledge_base.py** - KB handler
- ✅ **intent_detector.py** - Intent detection
- ✅ **entity_extractor.py** - Entity extraction
- ✅ **llm_fallback.py** - LLM integration
- ✅ **test_setup.py** - Setup verification
- ✅ **data/** - Knowledge base JSON files
- ✅ **QUICKSTART.md** - Quick start guide
- ✅ **LLM_EXPLAINED.md** - LLM documentation

---

## Troubleshooting

### If you get authentication errors:

**Option 1: Use Personal Access Token**
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with `repo` permissions
3. Use token as password when pushing

**Option 2: Use GitHub CLI**
```powershell
gh auth login
git push -u origin main
```

### If repository already exists:

```powershell
git remote set-url origin https://github.com/2005-Aneeshdutt/Personal-Chatbot.git
git push -u origin main
```

---

## After Pushing - Enhance Your Repository

1. **Add Topics/Tags**: Go to repository → ⚙️ → Topics → Add: `chatbot`, `streamlit`, `python`, `nlp`, `college-helpdesk`

2. **Add Description**: Update repository description on GitHub

3. **Pin Repository**: Pin it to your profile for visibility

4. **Add Badges** (already in README): Should display automatically

---

## Repository Information

- **Name**: Personal-Chatbot
- **Visibility**: Public
- **License**: MIT
- **Language**: Python
- **Topics**: chatbot, streamlit, python, nlp, knowledge-base

---

**Your repository is ready! 🎉**
