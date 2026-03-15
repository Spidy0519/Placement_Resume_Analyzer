# main.py — Resume Placement Analyzer API v2
import os
import uuid
import logging
from typing import Optional, Dict, Any

import uvicorn  # type: ignore
from fastapi import FastAPI, UploadFile, File, HTTPException  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from pydantic import BaseModel  # type: ignore
from dotenv import load_dotenv  # type: ignore

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PlacementAPI")

# Load .env from the current file's directory
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)
    logger.info(f"Loaded .env from {env_path}")
else:
    logger.warning(f".env file not found at {env_path}. Ensure environment variables are set.")

from app.resume_parser import parse_resume  # type: ignore
from app.domain_detector import auto_detect_department, get_all_departments, extract_cgpa, check_cgpa_eligibility  # type: ignore
from app.domain_config import DEPARTMENT_JOBS  # type: ignore
from app.placement_scorer import score_general_skills, score_domain_skills, compute_overall_placement_score  # type: ignore
from app.template_matcher import match_resume_to_template, count_projects, check_portfolio_links, load_template_from_bytes  # type: ignore
from app.rag_engine import compute_rag_similarity  # type: ignore
from app.groq_service import get_placement_ai_analysis, get_resume_chat_answer, get_general_chatbot_response, get_skill_roadmap  # type: ignore

app = FastAPI(
    title="Student Placement Resume Analyzer API v2",
    description="AI-powered resume analysis for college placement",
    version="2.0.0"
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

sessions: Dict[str, Any] = {}
template_store: dict = {"loaded": False, "data": None}


# ── Startup Event ─────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    """Pre-load AI models to avoid hanging on first request."""
    logger.info("Initializing system... Pre-loading models.")
    try:
        from app.rag_engine import get_embedding_model  # type: ignore
        # This will trigger the download/load of the model if needed
        model = get_embedding_model()
        logger.info("✅ Embedding model (all-MiniLM-L6-v2) loaded successfully.")
    except Exception as e:
        logger.error(f"❌ Critical error during startup: {e}")
        logger.info("Server will continue, but RAG analysis might fail on first run.")


# ── Models ────────────────────────────────────────────
class AnalyzeRequest(BaseModel):
    session_id: str
    department: Optional[str] = None
    selected_job: Optional[str] = None

class AIAnalysisRequest(BaseModel):
    session_id: str
    department: Optional[str] = None
    selected_job: Optional[str] = None
    language: Optional[str] = "english"

class ChatRequest(BaseModel):
    session_id: str
    question: str
    department: Optional[str] = "CSE"
    selected_job: Optional[str] = None

class PlaceBotRequest(BaseModel):
    message: str
    language: Optional[str] = "english"

class RoadmapRequest(BaseModel):
    session_id: str
    department: Optional[str] = None
    selected_job: Optional[str] = None
    language: Optional[str] = "english"


# ── Root ──────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "name": "Student Placement Resume Analyzer v2",
        "flow": {
            "admin":   "POST /upload-template  → Upload college DOCX template (once)",
            "step_1":  "POST /upload-resume    → Student uploads PDF/DOCX",
            "step_2":  "POST /detect-department → Auto or manual department",
            "step_3":  "POST /get-placement-scores → Full scoring",
            "step_4":  "POST /get-ai-analysis  → AI suggestions",
            "step_5":  "POST /chat             → Ask resume questions",
            "step_6":  "POST /placebot         → General placement chatbot",
            "step_7":  "POST /generate-roadmap → Generate skill learning roadmap",
            "utils":   "GET  /departments      → All departments + jobs"
        }
    }

@app.get("/health")
def health():
    return {"status": "healthy", "template_loaded": template_store["loaded"], "active_sessions": len(sessions)}


# ── Admin: Upload Template ────────────────────────────
@app.post("/upload-template")
async def upload_template(file: UploadFile = File(...)):
    """Admin uploads college DOCX resume template once."""
    if not (file.filename or "").endswith(".docx"):
        raise HTTPException(400, "Only DOCX format supported for template.")
    file_bytes = await file.read()
    try:
        template_data = load_template_from_bytes(file_bytes)
        template_store["loaded"] = True
        template_store["data"] = template_data
        return {
            "success": True,
            "message": "Template loaded!",
            "keyword_count": template_data["total_keywords"],
            "sample_keywords": template_data["template_keywords"][:20]
        }
    except Exception as e:
        raise HTTPException(500, f"Template load failed: {e}")


# ── Departments ───────────────────────────────────────
@app.get("/departments")
def list_departments():
    return {"departments": get_all_departments()}

@app.get("/departments/{dept_code}/jobs")
def jobs_for_department(dept_code: str):
    dept_code = dept_code.upper()
    if dept_code not in DEPARTMENT_JOBS:
        raise HTTPException(404, f"Department not found. Available: {list(DEPARTMENT_JOBS.keys())}")
    d = DEPARTMENT_JOBS[dept_code]
    return {
        "department": dept_code,
        "label": d["label"],
        "jobs": d["jobs"],
        "min_cgpa": d["min_cgpa"],
        "certifications": d["certifications"],
        "dsa_platforms": d["dsa_platforms"]
    }


# ── Step 1: Upload Resume ─────────────────────────────
@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    if not file:
        logger.error("No file received in upload-resume")
        raise HTTPException(400, "No file uploaded.")
    
    filename = file.filename or "unknown_resume"
    logger.info(f"[Backend] Upload request received for file: {filename}")
    
    if not (filename.lower().endswith(".pdf") or filename.lower().endswith(".docx")):
        logger.warning(f"Unsupported file type: {filename}")
        raise HTTPException(400, "Only PDF and DOCX supported.")
    
    try:
        file_bytes = await file.read()
        logger.info(f"[Backend] Read {len(file_bytes)} bytes from {filename}")
        
        if len(file_bytes) > 5 * 1024 * 1024:
            raise HTTPException(400, "File too large. Max 5MB.")

        resume_data = parse_resume(file_bytes, filename)
        print(f"[Backend] Parsed resume successfully. Words: {resume_data['word_count']}")
        sid = str(uuid.uuid4())
        sessions[sid] = {
            "resume_data": resume_data,
            "filename": filename,
            "department": None,
            "selected_job": None,
            "scores": {}
        }
        return {
            "success": True,
            "session_id": sid,
            "filename": filename,
            "word_count": resume_data["word_count"],
            "message": "Resume uploaded! Call /detect-department next."
        }
    except ValueError as e:
        print(f"[Backend] Validation Error in parse_resume: {e}")
        raise HTTPException(422, str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[Backend] Unexpected Error in upload-resume: {e}")
        raise HTTPException(500, f"System error: {e}")


# ── Step 2: Detect Department ─────────────────────────
@app.post("/detect-department")
async def detect_department(request: AnalyzeRequest):
    """Auto-detect or manually set student's department."""
    session = sessions.get(request.session_id)
    if not session:
        raise HTTPException(404, "Session not found. Upload resume first.")
    resume_text = session["resume_data"]["cleaned_text"]

    if request.department:
        dept_code = str(request.department).upper()
        if dept_code not in DEPARTMENT_JOBS:
            raise HTTPException(400, f"Invalid department. Choose: {list(DEPARTMENT_JOBS.keys())}")
        dept_info = DEPARTMENT_JOBS[dept_code]
        detection = {"method": "manual", "department": dept_code,
                     "department_label": dept_info["label"], "confidence": 100,
                     "jobs": dept_info["jobs"]}
    else:
        detection = auto_detect_department(resume_text)
        detection["method"] = "auto"
        if detection.get("detected"):
            dept_code = detection["department"]
            detection["jobs"] = DEPARTMENT_JOBS[dept_code]["jobs"]
        else:
            dept_code = None

    sessions[request.session_id]["department"] = detection.get("department")
    sessions[request.session_id]["selected_job"] = request.selected_job

    cgpa_data = extract_cgpa(resume_text)
    cgpa_check = check_cgpa_eligibility(cgpa_data, dept_code) if dept_code else {}

    return {
        "success": True,
        "detection": detection,
        "cgpa": cgpa_data,
        "cgpa_eligibility": cgpa_check
    }


# ── Step 3: Get Full Placement Scores ─────────────────
@app.post("/get-placement-scores")
async def get_placement_scores(request: AnalyzeRequest):
    """Full placement scoring across all 8 categories."""
    print(f"[Backend] Getting scores for session: {request.session_id}")
    session = sessions.get(request.session_id)
    if not session:
        raise HTTPException(404, "Session not found.")

    resume_text = session["resume_data"]["cleaned_text"]
    resume_raw  = session["resume_data"]["raw_text"]

    dept_code = (request.department or session.get("department") or "CSE").upper()
    sessions[request.session_id]["department"] = dept_code

    selected_job = request.selected_job or session.get("selected_job")
    sessions[request.session_id]["selected_job"] = selected_job

    dept_info = DEPARTMENT_JOBS.get(dept_code, {})

    try:
        general_scores  = score_general_skills(resume_text)
        domain_scores   = score_domain_skills(resume_text, dept_code, selected_job)
        template_match  = (
            match_resume_to_template(resume_text, template_store["data"])
            if template_store["loaded"]
            else {
                "template_match_score": 0,
                "grade": "No Template Loaded",
                "color": "gray",
                "matched_keywords": [],
                "missing_keywords": [],
                "recommendation": "Admin must upload the college DOCX template via POST /upload-template"
            }
        )
        portfolio_check = check_portfolio_links(resume_raw)
        project_count   = count_projects(resume_raw)
        cgpa_data       = extract_cgpa(resume_text)
        cgpa_check      = check_cgpa_eligibility(cgpa_data, dept_code)
        rag_results     = compute_rag_similarity(session["resume_data"]["chunks"])
        overall_score   = compute_overall_placement_score(
            general_scores, domain_scores, template_match,
            portfolio_check, project_count, cgpa_check
        )

        # Cache
        sessions[request.session_id]["scores"] = {
            "general_scores": general_scores, "domain_scores": domain_scores,
            "template_match": template_match, "portfolio_check": portfolio_check,
            "project_count": project_count, "cgpa_data": cgpa_data,
            "cgpa_check": cgpa_check, "rag_results": rag_results,
            "overall_score": overall_score, "department": dept_code,
            "selected_job": selected_job
        }

        results = {
            "success": True,
            "session_id": request.session_id,
            "department": dept_code,
            "department_label": dept_info.get("label", dept_code),
            "selected_job": selected_job,
            "overall_placement_score": overall_score,
            "general_skills": general_scores,
            "domain_skills": domain_scores,
            "template_match": template_match,
            "portfolio": portfolio_check,
            "projects": project_count,
            "academics": {
                "cgpa": cgpa_data,
                "eligibility": cgpa_check,
                "min_required": dept_info.get("min_cgpa", 6.0)
            },
            "rag_analysis": rag_results
        }
        
        return results
    except Exception as e:
        import traceback
        logger.error(f"Scoring failed for session {request.session_id}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(500, detail=f"Scoring failed: {type(e).__name__} - {str(e)}")


# ── Step 4: AI Analysis ───────────────────────────────
@app.post("/get-ai-analysis")
async def get_ai_analysis(request: AIAnalysisRequest):
    """AI — 10-section placement improvement plan."""
    session = sessions.get(request.session_id)
    if not session:
        raise HTTPException(404, "Session not found.")
    cached = session.get("scores", {})
    if not cached:
        raise HTTPException(400, "Run /get-placement-scores first.")

    dept_code = cached.get("department", "CSE")
    dept_info = DEPARTMENT_JOBS.get(dept_code.upper(), {})

    try:
        ai_result = get_placement_ai_analysis(
            resume_text   = session["resume_data"]["cleaned_text"],
            dept_code     = dept_code,
            dept_label    = dept_info.get("label", dept_code),
            selected_job  = cached.get("selected_job", ""),
            overall_score = cached["overall_score"],
            general_scores= cached["general_scores"],
            domain_scores = cached["domain_scores"],
            template_match= cached["template_match"],
            portfolio_check=cached["portfolio_check"],
            project_count = cached["project_count"],
            cgpa_check    = cached["cgpa_check"],
            language      = request.language
        )
        return {
            "success": ai_result.get("success", False),
            "session_id": request.session_id,
            "department": dept_code,
            "selected_job": cached.get("selected_job"),
            "ai_analysis": ai_result["analysis"],
            "model_used": ai_result["model_used"],
            "tokens_used": ai_result.get("tokens_used", {})
        }
    except Exception as e:
        import traceback
        logger.error(f"AI Analysis error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(500, detail=f"AI analysis failed: {type(e).__name__} - {str(e)}")


# ── Step 5: Chat ──────────────────────────────────────
@app.post("/chat")
async def chat(request: ChatRequest):
    """Ask specific placement or resume questions."""
    session = sessions.get(request.session_id)
    if not session:
        raise HTTPException(404, "Session not found.")
    dept_code    = request.department or session.get("department", "CSE")
    selected_job = request.selected_job or session.get("selected_job", "")
    result = get_resume_chat_answer(
        question     = request.question,
        resume_text  = session["resume_data"]["cleaned_text"],
        dept_code    = dept_code,
        selected_job = selected_job
    )
    if not result.get("success"):
        logger.error(f"Chat service error: {result.get('error')}")
        raise HTTPException(500, detail=result.get("error", "Chat failed"))
    return {"success": True, "question": request.question, "answer": result["answer"]}


# ── Step 6: General PlaceBot ──────────────────────────
@app.post("/placebot")
async def placebot(request: PlaceBotRequest):
    """General placement chatbot interaction."""
    # FIXED PROBLEM: Avoid bracket slicing for linter
    msg_preview = "".join([char for i, char in enumerate(str(request.message)) if i < 50])
    logger.info(f"Received PlaceBot request: {msg_preview}...")
    
    # We pass a simple message list to the service
    system_prompt = "You are PlaceBot, a friendly AI Placement Assistant for engineering students. Response in Tanglish (Tamil + English mix)."
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": request.message}
    ]
    
    try:
        result = get_general_chatbot_response(messages)
        if not result.get("success"):
            logger.error(f"Chatbot service error: {result.get('error')}")
            raise HTTPException(500, detail=result.get("error", "Chatbot failed"))
        return {"reply": result["answer"]}
    except Exception as e:
        import traceback
        logger.error(f"Unexpected error in /placebot: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(500, detail=f"{type(e).__name__}: {str(e)}")


# ── Step 7: Skill Roadmap ─────────────────────────────
@app.post("/generate-roadmap")
async def generate_roadmap(request: RoadmapRequest):
    """Generate a learning roadmap based on missing skills."""
    session = sessions.get(request.session_id)
    if not session:
        raise HTTPException(404, "Session not found.")
    cached = session.get("scores", {})
    if not cached:
        raise HTTPException(400, "Run /get-placement-scores first.")

    dept_code = cached.get("department", "CSE")
    dept_info = DEPARTMENT_JOBS.get(dept_code.upper(), {})

    try:
        roadmap_result = get_skill_roadmap(
            resume_text   = session["resume_data"]["cleaned_text"],
            dept_code     = dept_code,
            dept_label    = dept_info.get("label", dept_code),
            selected_job  = cached.get("selected_job", ""),
            domain_scores = cached["domain_scores"],
            language      = request.language
        )
        if not roadmap_result.get("success"):
            raise HTTPException(500, roadmap_result.get("error", "Failed to generate roadmap"))
            
        return {
            "success": True,
            "session_id": request.session_id,
            "roadmap": roadmap_result["roadmap"]
        }
    except Exception as e:
        import traceback
        logger.error(f"Roadmap generation error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(500, detail=f"Roadmap generation failed: {type(e).__name__} - {str(e)}")


# ── Cleanup ───────────────────────────────────────────
@app.delete("/session/{session_id}")
def clear_session(session_id: str):
    if session_id in sessions:
        sessions.pop(session_id, None)
        return {"success": True}
    raise HTTPException(404, "Session not found.")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
