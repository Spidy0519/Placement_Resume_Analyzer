🎓 Placement Resume Analyzer
AI-Powered Resume Analysis for College Placement

📁 Project Structure
PlacementResumeAnalyzer/
│
├── 📁 backend/                    ← Python FastAPI Server (Brain of the app)
│   ├── main.py                    ← All API routes (endpoints) are here
│   ├── requirements.txt           ← Libraries installation list
│   ├── .env.example               ← API Key template (copy → .env)
│   │
│   └── 📁 app/                    ← Core logic files
│       ├── __init__.py            ← Python package marker
│       ├── domain_config.py       ← 7 Departments × 10 Jobs × Skills data (College PDF data)
│       ├── domain_detector.py     ← Auto-detect department from resume text
│       ├── keywords_config.py     ← All keyword lists for scoring
│       ├── resume_parser.py       ← PDF & DOCX text extraction
│       ├── placement_scorer.py    ← 8-category placement scoring engine
│       ├── template_matcher.py    ← Resume vs College template comparison
│       ├── rag_engine.py          ← FAISS vector similarity (RAG)
│       └── groq_service.py        ← Groq (llama3-70b) integration
│
├── 📁 frontend/
│   └── index.html                 ← Complete UI (HTML + CSS + Bootstrap + JS)
│
├── 📁 docs/
│   └── API_REFERENCE.md           ← All API endpoints documentation
│
├── .gitignore                     ← Files that won't be pushed to GitHub
└── README.md                      ← This file!

⚙️ Step 1: Install Libraries
Check Python Version
bashpython --version
# If not installed, download from: https://python.org/downloads
Create Virtual Environment
bash# Navigate to backend folder
cd PlacementResumeAnalyzer/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

# You should see (venv) prompt - activation successful ✅
Install Libraries
bash# Install all libraries from requirements.txt
pip install -r requirements.txt

# Verify installation:
pip list
```

### Library Details:
| Library | Purpose | Size |
|---------|---------|------|
| `fastapi` | REST API framework | Small |
| `uvicorn` | Server to run FastAPI | Small |
| `python-multipart` | File upload support | Small |
| `pdfplumber` | PDF text extraction | Medium |
| `python-docx` | DOCX text extraction | Small |
| `sentence-transformers` | Text → Vector conversion (RAG) | **Large ~500MB** |
| `faiss-cpu` | Vector similarity search | Medium |
| `numpy` | Math operations | Medium |
| `groq` | Groq API connection | Small |
| `pydantic` | Data validation | Small |
| `python-dotenv` | .env file reading | Small |

> ⚠️ **Note:** `sentence-transformers` download may take 5-10 minutes. This is normal!

---

## 🔑 Step 2: How to Get Groq API Key (FREE)

**Steps:**
```
1. Go to https://console.groq.com → Sign Up (you can use Google account)
2. Click on "API Keys" in the left sidebar
3. Click "Create API Key" button
4. Copy the key (format: gsk_xxxx...)
5. Copy backend/.env.example file and rename it to .env
6. Paste the key: GROQ_API_KEY=gsk_xxxx...
bash# Create .env file
cd backend
cp .env.example .env

# Edit .env file and paste your key:
# GROQ_API_KEY=gsk_your_actual_key_here

✅ Groq is FREE — llama3-70b model usage (Daily limit is sufficient)


🚀 Step 3: How to Run
Start Backend Server
bash# Navigate to backend folder
cd PlacementResumeAnalyzer/backend

# Activate virtual environment
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux

# Start server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# You should see this message when server is ready:
# INFO: Uvicorn running on http://0.0.0.0:8000
Open Frontend
bash# Open frontend/index.html file in your browser
# Just double-click the file!

# Or use VS Code Live Server:
# VS Code → index.html → Right click → "Open with Live Server"
```

### API Documentation (Swagger UI)
```
http://localhost:8000/docs   ← Interactive API testing
http://localhost:8000/redoc  ← Documentation view

🔌 Step 4: How to Use the API (Frontend → Backend)
Complete Flow (5 Steps):
Step 1️⃣ — Upload Resume
javascriptconst formData = new FormData();
formData.append('file', resumeFile);  // PDF or DOCX

const response = await fetch('http://localhost:8000/upload-resume', {
  method: 'POST',
  body: formData
});
const { session_id } = await response.json();
// Save session_id for subsequent API calls
Step 2️⃣ — Detect / Set Department
javascriptconst response = await fetch('http://localhost:8000/detect-department', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    session_id: session_id,
    department: 'CSE',        // Manual selection (or null for auto-detect)
    selected_job: 'Full Stack Developer'
  })
});
Step 3️⃣ — Get All Scores
javascriptconst response = await fetch('http://localhost:8000/get-placement-scores', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    session_id: session_id,
    department: 'CSE',
    selected_job: 'Full Stack Developer'
  })
});
const data = await response.json();
// data.overall_placement_score.placement_readiness_score → 0-100
// data.general_skills → office, communication, programming scores
// data.domain_skills → job-specific skill gaps
// data.template_match → college template keyword match
// data.portfolio → github, linkedin check
// data.academics → cgpa check
Step 4️⃣ — Get AI Analysis
javascriptconst response = await fetch('http://localhost:8000/get-ai-analysis', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ session_id: session_id })
});
const { ai_analysis } = await response.json();
// ai_analysis = detailed markdown text with 10 sections
Step 5️⃣ — Chat (Ask Questions)
javascriptconst response = await fetch('http://localhost:8000/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    session_id: session_id,
    question: 'What projects should I add for Data Scientist role?',
    department: 'AIDS'
  })
});
const { answer } = await response.json();
Admin — Upload College Template (One-time)
javascriptconst formData = new FormData();
formData.append('file', templateDocxFile);

await fetch('http://localhost:8000/upload-template', {
  method: 'POST',
  body: formData
});
// Upload your college DOCX template once, and it's saved
```

---

## 📊 Scoring System Breakdown
```
PLACEMENT READINESS SCORE (0-100)
├── Domain Skills Match     ← 25% weight  (Job-specific skills)
├── General Skills          ← 20% weight  (Programming, Communication, Office Tools)
├── Template Match          ← 15% weight  (College template keyword match)
├── DSA & Aptitude          ← 15% weight  (LeetCode, HackerRank presence)
├── Projects                ← 10% weight  (Count of projects, target: 5-10)
├── Portfolio               ←  8% weight  (GitHub, LinkedIn, Portfolio links)
└── Academics (CGPA)        ←  7% weight  (CGPA vs job minimum requirement)

Score → Grade Mapping:
  85-100 → Excellent ✅  (Apply to top companies now!)
  70-84  → Good 👍       (Fix weak areas, you're ready)
  50-69  → Average ⚠️    (Improve domain skills + projects)
  30-49  → Needs Work 🔧 (Follow AI suggestions systematically)
  0-29   → Missing ❌    (Rebuild resume from template)

🆕 What Can Be Added (Future Improvements)
Easy to Add (1-2 days):

 Resume PDF Download — Fill form and export as PDF
 Job Description Match — Paste job description → show match score
 Compare Resumes — Side-by-side comparison of 2 resumes
 Email Report — Send analysis results via email

Medium Complexity (3-5 days):

 College PDF Auto-Load — Add POST /upload-college-data route
 User Login — Students can register and view history
 Admin Dashboard — View how many students analyzed, average scores
 Resume Ranking — Top 10 students list for placement officer

Advanced Features (1-2 weeks):

 Real-time Job Matching — Connect LinkedIn / Naukri API
 Mock Interview Q&A — Domain-specific interview questions
 Resume Versions — Save multiple versions, track improvement
 WhatsApp Bot — Send resume via WhatsApp, get analysis back


🐛 Common Errors & Solutions
ErrorCauseFixModuleNotFoundErrorLibrary not installedRun pip install -r requirements.txtGROQ_API_KEY not found.env file missingCopy .env.example → .env, add your keyCORS error in browserFrontend → Backend blockedAlready fixed in code (allow_origins=["*"])Port 8000 in useAnother app is running on port 8000Use different port: uvicorn main:app --port 8001File parse errorScanned/image-based PDFAsk student to use text-based PDFsentence-transformers slowFirst time downloadWait 5-10 min, model downloads once

🛠️ Tech Stack
LayerTechnologyFrontendHTML5 + CSS3 + Bootstrap 5 + Vanilla JSBackendPython 3.10+ + FastAPIAI/MLsentence-transformers + FAISS (RAG)LLMGroq API → llama3-70b-8192PDF ParsepdfplumberDOCX Parsepython-docxServerUvicorn (ASGI)

📞 Quick Start Summary
bash# 1. Install dependencies
cd backend
pip install -r requirements.txt

# 2. Setup API Key
cp .env.example .env
# Edit .env file → add GROQ_API_KEY

# 3. Run the server
uvicorn main:app --reload --port 8000

# 4. Open frontend/index.html in browser

# 5. Done! 🎉

🎯 How to Run (Alternative Method):

Open backend folder in VS Code
Open terminal and run:

bash   cd backend
   venv\Scripts\python main.py
OR
bash   venv\Scripts\python main.py (or)

uvicorn main:app --host 0.0.0.0 --port 8000 --reload

Open frontend/index.html in browser
Upload resume and analyze!