# app/groq_service.py
# -------------------------------------------------------
# (llama3-70b) — Placement-Specific Analysis
# -------------------------------------------------------

import os
import httpx  # type: ignore
import logging
from typing import Optional, Any, Union
from groq import Groq  # type: ignore
from functools import wraps
from time import sleep

# FIXED PROBLEM 1: Added proper logging instead of print statements
logger = logging.getLogger(__name__)

# FIXED PROBLEM 2: Centralized configuration constants to avoid magic numbers
class GroqConfig:
    DEFAULT_MODEL = "llama-3.3-70b-versatile"
    DEFAULT_TEMPERATURE = 0.7
    MAX_TOKENS_ANALYSIS = 2500
    MAX_TOKENS_CHAT = 800
    RESUME_TEXT_LIMIT = 3000  # Increased from arbitrary 2500
    RESUME_CHAT_LIMIT = 2500  # Increased from 2000
    MAX_RETRY_ATTEMPTS = 3
    RETRY_DELAY_SECONDS = 1


# FIXED PROBLEM 3: Added retry decorator for transient failures
def retry_on_failure(max_attempts: int = GroqConfig.MAX_RETRY_ATTEMPTS):
    """Retry decorator for handling transient API failures."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception: Optional[Exception] = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying...")
                        sleep(GroqConfig.RETRY_DELAY_SECONDS * (attempt + 1))
                    else:
                        logger.error(f"All {max_attempts} attempts failed: {str(e)}")
            
            if last_exception:
                raise last_exception
            raise Exception(f"Failed after {max_attempts} attempts")
        return wrapper
    return decorator


# FIXED PROBLEM 4: Improved API key handling with validation
def get_groq_client(api_key: Optional[str] = None) -> Groq:
    """
    Get Groq client with proper API key validation.
    
    Args:
        api_key: Optional API key. Falls back to GROQ_API_KEY env var.
    
    Returns:
        Groq: Configured Groq client
    
    Raises:
        ValueError: If no valid API key is found
    """
    api_key = api_key or os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not provided or found in environment variables.")
    
    # FIXED PROBLEM 5: Validate API key format (basic check)
    if not api_key.startswith("gsk_"):
        logger.warning("API key format looks suspicious. Groq keys typically start with 'gsk_'")
    
    # Use a fresh httpx Client with timeout to avoid potential proxy configuration conflicts or hangs
    return Groq(api_key=api_key, http_client=httpx.Client(timeout=60.0))



# FIXED PROBLEM 6: Added input validation helper
def validate_inputs(**kwargs) -> None:
    """Validate that required inputs are not empty."""
    for key, value in kwargs.items():
        if value is None or (isinstance(value, str) and not value.strip()):
            raise ValueError(f"Required parameter '{key}' is empty or None")


# FIXED PROBLEM 7: Improved safe list extraction to handle None values properly
def safe_list_extract(data: Optional[dict[str, Any]], *keys: str, default: Optional[list[Any]] = None) -> list[Any]:
    """
    Safely extract a list from nested dictionaries, handling None values.
    """
    # Local variable to help linter with type narrowing
    final_default: list[Any] = default if default is not None else []
    
    if data is None:
        return list(final_default)
    
    current: Any = data
    for key in keys:
        if not isinstance(current, dict):
            return list(final_default)
        current = current.get(key)
        if current is None:
            return list(final_default)
    
    if isinstance(current, list):
        return list(current)
        
    return list(final_default)


def build_placement_prompt(
    resume_text: str,
    dept_code: str,
    dept_label: str,
    selected_job: str,
    overall_score: dict[str, Any],
    domain_scores: dict[str, Any],
    template_match: dict[str, Any],
    portfolio_check: dict[str, Any],
    project_count: dict[str, Any],
    cgpa_check: dict[str, Any],
    language: str = "tamil"
) -> str:
    """
    Build comprehensive placement analysis prompt.
    
    Args:
        resume_text: The student's resume text
        dept_code: Department code (e.g., 'CSE')
        dept_label: Full department name
        selected_job: Target job role
        overall_score: Overall scoring dictionary
        domain_scores: Domain-specific scores
        template_match: Template matching results
        portfolio_check: Portfolio validation results
        project_count: Project counting results
        cgpa_check: CGPA validation results
        language: Response language ('tamil' or 'english')
    
    Returns:
        str: Formatted prompt for Groq API
    """
    # FIXED PROBLEM 8: Input validation
    validate_inputs(
        resume_text=resume_text,
        dept_code=dept_code,
        dept_label=dept_label
    )
    
    # FIXED PROBLEM 9: Use safe_list_extract to handle None values properly
    missing_domain = safe_list_extract(domain_scores, "selected_job_match", "skills_missing")
    if not missing_domain:
        missing_domain = safe_list_extract(domain_scores, "best_matching_job", "skills_missing")
    
    missing_certs = safe_list_extract(domain_scores, "certifications", "certs_missing")
    missing_portfolio = safe_list_extract(portfolio_check, "absent")
    missing_template_kw = safe_list_extract(template_match, "missing_keywords")
    dsa_platforms_missing = safe_list_extract(domain_scores, "dsa_aptitude", "platforms_missing")
    
    # FIXED PROBLEM 10: Safe dict access with get() and defaults
    cgpa_status = cgpa_check.get("message", "CGPA not detected") if cgpa_check else "CGPA not detected"
    proj_status = project_count.get("status", "Unknown") if project_count else "Unknown"

    # FIXED PROBLEM 11: Explicit slicing handling
    # We use slices carefully to satisfy the linter
    m_domain_actual = list(missing_domain) if missing_domain else []
    m_certs_actual = list(missing_certs) if missing_certs else []
    m_portfolio_actual = list(missing_portfolio) if missing_portfolio else []
    m_dsa_actual = list(dsa_platforms_missing) if dsa_platforms_missing else []
    m_template_actual = list(missing_template_kw) if missing_template_kw else []

    # FIXED PROBLEM 11: Avoid bracket slicing to satisfy linter hallucinations
    def get_slice(items: list[Any], limit: int) -> list[Any]:
        res = []
        for i, val in enumerate(items):
            if i >= limit: break
            res.append(val)
        return res

    missing_domain_str = ", ".join(get_slice(m_domain_actual, 10)) if m_domain_actual else "None detected"
    missing_certs_str = ", ".join(get_slice(m_certs_actual, 5)) if m_certs_actual else "None"
    missing_portfolio_str = ", ".join(m_portfolio_actual) if m_portfolio_actual else "None"
    dsa_platforms_str = ", ".join(m_dsa_actual) if m_dsa_actual else "None"
    missing_template_kw_str = ", ".join(get_slice(m_template_actual, 10)) if m_template_actual else "None"

    lang_instruction = "CRITICAL: You MUST respond in professional ENGLISH only."

    # FIXED PROBLEM 12: Use consistent text limit from config
    # FIXED PROBLEM 12: Avoid bracket slicing to satisfy linter
    def _str_slice(s: str, limit: int) -> str:
        res = []
        for i, char in enumerate(s):
            if i >= limit: break
            res.append(char)
        return "".join(res)
        
    resume_snippet = _str_slice(str(resume_text), GroqConfig.RESUME_TEXT_LIMIT) if resume_text else ""

    prompt = f"""You are an expert placement counselor at a top engineering college in India.
You help students get placed at top tech companies.

Analyze this student's resume for PLACEMENT READINESS and provide actionable guidance.
{lang_instruction}

--- STUDENT PROFILE ---
Department: {dept_label} ({dept_code})
Target Job Role: {selected_job or "Best matching role"}
Resume Text:
{resume_snippet}
--- END RESUME ---

--- ANALYSIS SCORES ---
Overall Placement Readiness: {overall_score.get('placement_readiness_score', 0)}/100 ({overall_score.get('grade', '')})
Template Match Score: {template_match.get('template_match_score', 0) if template_match else 0}/100
Portfolio Score: {portfolio_check.get('portfolio_score', 0) if portfolio_check else 0}/100
Projects: {project_count.get('estimated_count', 0) if project_count else 0} projects ({proj_status})
CGPA Status: {cgpa_status}
Skills Missing for {selected_job or "target role"}: {missing_domain_str}
Missing Certifications: {missing_certs_str}
Missing Portfolio Links: {missing_portfolio_str}
Missing DSA Platforms: {dsa_platforms_str}
Missing Template Keywords: {missing_template_kw_str}
--- END SCORES ---

Provide DETAILED PLACEMENT ANALYSIS with these exact sections:

## 🎯 PLACEMENT READINESS SUMMARY
(2-3 sentences overall assessment for this department and job role)

## 🚨 TOP 3 CRITICAL GAPS
(3 most important things blocking placement — be very specific)

## 💻 SKILLS TO ADD IMMEDIATELY
(Exact technical skills missing for {selected_job or "target role"} with learning resources)

## 📜 CERTIFICATIONS TO GET
(Top 3 certifications for {dept_label} — mention free options first)

## 🔢 DSA & APTITUDE PREPARATION
(Current status + specific platforms + how many problems per day)

## 📁 PROJECTS TO BUILD
(3 specific project ideas for {dept_label} that impress recruiters — with tech stack)

## 🌐 PORTFOLIO & ONLINE PRESENCE
(Exact steps to improve GitHub, LinkedIn, portfolio based on what's missing)

## 🎓 ACADEMICS
(CGPA advice + how to compensate if CGPA is low)

## ✏️ RESUME QUICK WINS
(5 specific changes to make in the next 30 minutes)

## 📅 30-DAY PLACEMENT ACTION PLAN
(Week-by-week: what to learn, build, and apply for)

Be specific, practical, and encouraging. Use Indian tech placement context 
(TCS, Infosys, Wipro for mass; FAANG/startups for dream companies)."""

    return prompt


# FIXED PROBLEM 13: Added retry decorator and improved error handling
@retry_on_failure(max_attempts=2)
def get_placement_ai_analysis(
    resume_text: str,
    dept_code: str,
    dept_label: str,
    selected_job: str,
    overall_score: dict[str, Any],
    general_scores: dict[str, Any],
    domain_scores: dict[str, Any],
    template_match: dict[str, Any],
    portfolio_check: dict[str, Any],
    project_count: dict[str, Any],
    cgpa_check: dict[str, Any],
    language: str = "tamil"
) -> dict[str, Any]:
    """
    Get AI placement analysis with retry logic.
    
    Returns:
        dict: Analysis result with success status, content, and metadata
    """
    try:
        client = get_groq_client()
        prompt = build_placement_prompt(
            resume_text, dept_code, dept_label, selected_job,
            overall_score, domain_scores, template_match,
            portfolio_check, project_count, cgpa_check,
            language=language
        )

        response = client.chat.completions.create(
            model=GroqConfig.DEFAULT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert placement counselor specializing in engineering college placements in India. "
                        "You give specific, actionable, and encouraging advice tailored to each student's department and target role. "
                        "You know the Indian tech job market, top companies, and exactly what skills each role requires."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            temperature=GroqConfig.DEFAULT_TEMPERATURE,
            max_tokens=GroqConfig.MAX_TOKENS_ANALYSIS
        )

        return {
            "success": True,
            "analysis": response.choices[0].message.content,
            "model_used": GroqConfig.DEFAULT_MODEL,
            "tokens_used": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }

    except Exception as e:
        # FIXED PROBLEM 14: Proper logging without exposing sensitive data
        logger.error(f"Placement AI analysis failed: {type(e).__name__}")
        return {
            "success": False,
            "error": type(e).__name__,  # Don't expose full error message
            "analysis": "AI analysis temporarily unavailable. Please check your API configuration.",
            "model_used": GroqConfig.DEFAULT_MODEL
        }


# FIXED PROBLEM 15: Consistent API key handling across all functions
def _get_api_key_with_fallback(primary_key: str, fallback_key: str = "GROQ_API_KEY") -> Optional[str]:
    """Get API key with fallback logic."""
    return os.getenv(primary_key) or os.getenv(fallback_key)


def get_resume_chat_answer(
    question: str, 
    resume_text: str, 
    dept_code: str, 
    selected_job: str
) -> dict[str, Any]:
    """
    Answer specific student questions about their resume.
    
    Args:
        question: Student's question
        resume_text: Resume content
        dept_code: Department code
        selected_job: Target job role
    
    Returns:
        dict: Answer result with success status
    """
    try:
        # FIXED PROBLEM 16: Use consistent API key handling
        api_key = _get_api_key_with_fallback("CHATBOT_API_KEY")
        if not api_key:
            raise ValueError("No API key found")
            
        client = get_groq_client(api_key)
        
        # FIXED PROBLEM 17: Use config constant for text limit
        # FIXED PROBLEM 17: Avoid bracket slicing to satisfy linter
        def _str_slice(s: str, limit: int) -> str:
            res = []
            for i, char in enumerate(s):
                if i >= limit: break
                res.append(char)
            return "".join(res)
            
        resume_snippet = _str_slice(str(resume_text), GroqConfig.RESUME_CHAT_LIMIT) if resume_text else ""
        
        response = client.chat.completions.create(
            model=GroqConfig.DEFAULT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": f"""You are a placement counselor helping a {dept_code} student
targeting {selected_job or 'software developer'} role.
Their resume:
---
{resume_snippet}
---
Answer questions specifically and practically. Be concise."""
                },
                {"role": "user", "content": question}
            ],
            temperature=GroqConfig.DEFAULT_TEMPERATURE,
            max_tokens=GroqConfig.MAX_TOKENS_CHAT
        )
        return {"success": True, "answer": response.choices[0].message.content}

    except Exception as e:
        logger.error(f"Resume chat failed: {type(e).__name__}")
        return {
            "success": False, 
            "error": type(e).__name__, 
            "answer": "Could not process your question. Please try again."
        }


def get_general_chatbot_response(messages: list[dict[str, str]]) -> dict[str, Any]:
    """
    General placement chatbot (PlaceBot) logic.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content'
    
    Returns:
        dict: Response with success status and answer
    """
    try:
        # FIXED PROBLEM 18: Consistent error handling and logging
        api_key = _get_api_key_with_fallback("CHATBOT_API_KEY")
        if not api_key:
            logger.error("No API key found for chatbot")
            return {
                "success": False, 
                "error": "Configuration error", 
                "answer": "PlaceBot configuration missing. Please contact support."
            }
            
        client = get_groq_client(api_key)
        
        response = client.chat.completions.create(
            model=GroqConfig.DEFAULT_MODEL,
            messages=messages,
            temperature=GroqConfig.DEFAULT_TEMPERATURE,
            max_tokens=GroqConfig.MAX_TOKENS_CHAT
        )
        return {"success": True, "answer": response.choices[0].message.content}

    except Exception as e:
        logger.error(f"General chatbot error: {type(e).__name__}")
        return {
            "success": False, 
            "error": type(e).__name__, 
            "answer": "PlaceBot is temporarily resting. Try again in a minute!"
        }


def get_skill_roadmap(
    resume_text: str,
    dept_code: str,
    dept_label: str,
    selected_job: str,
    domain_scores: dict[str, Any],
    language: str = "english"
) -> dict[str, Any]:
    """
    Generate a step-by-step Skill Learning Roadmap based on missing skills.
    
    Args:
        resume_text: Student's resume content
        dept_code: Department code
        dept_label: Full department name
        selected_job: Target job role
        domain_scores: Domain scoring results
        language: Response language ('tamil' or 'english')
    
    Returns:
        dict: Roadmap generation result
    """
    # FIXED PROBLEM 19 (bonus): Use safe extraction for all nested data
    m_domain = safe_list_extract(domain_scores, "selected_job_match", "skills_missing")
    m_certs = safe_list_extract(domain_scores, "selected_job_match", "certs_recommended")
    suggested_projects = safe_list_extract(domain_scores, "dsa_aptitude", "suggested_projects")
    
    # FIXED PROBLEM: Satisfy linter by avoiding bracket slicing
    def _slice(items: list[Any], limit: int) -> list[Any]:
        return [items[i] for i in range(min(len(items), limit))]
        
    m_domain_actual = list(m_domain) if m_domain else []
    m_certs_actual = list(m_certs) if m_certs else []
    m_projects_actual = list(suggested_projects) if suggested_projects else []

    missing_domain_str = ", ".join(_slice(m_domain_actual, 8)) if m_domain_actual else 'Advanced domain skills'
    m_certs_str = ", ".join(_slice(m_certs_actual, 5)) if m_certs_actual else 'None'
    projects_str = ", ".join(_slice(m_projects_actual, 3)) if m_projects_actual else 'None'

    lang_instruction = "CRITICAL: You MUST respond in professional ENGLISH only."

    prompt = f"""You are an expert technical career coach.
Create a detailed, step-by-step Skill Learning Roadmap for an engineering student.
{lang_instruction}

--- STUDENT PROFILE ---
Department: {dept_label} ({dept_code})
Target Job Role: {selected_job or "Best matching role"}
Missing Skills to Learn: {missing_domain_str}
Recommended Certifications: {m_certs_str}
Suggested Projects: {projects_str}
--- END PROFILE ---

Provide a comprehensive, week-by-week learning roadmap to master the missing skills and become job-ready for the {selected_job or "target"} role. 
Format the response using clear markdown headings and bullet points. Include:
1. 🎯 Roadmap Overview (Goal & Timeline)
2. 📅 Week-by-Week Plan (What to learn, resources, and practice exercises)
3. 🛠️ Project Integration (How to build a project using these skills)
4. 📚 Recommended Resources (Free courses, websites, YouTube channels)
"""
    try:
        api_key = _get_api_key_with_fallback("ROADMAP_API_KEY")
        if not api_key:
            raise ValueError("No API key found")
            
        client = get_groq_client(api_key)
        response = client.chat.completions.create(
            model=GroqConfig.DEFAULT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a specialized technical career coach building structured, practical learning roadmaps for Indian engineering students."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=GroqConfig.DEFAULT_TEMPERATURE,
            max_tokens=GroqConfig.MAX_TOKENS_ANALYSIS
        )
        return {
            "success": True,
            "roadmap": response.choices[0].message.content
        }
    except Exception as e:
        logger.error(f"Roadmap generation failed: {type(e).__name__}")
        return {
            "success": False,
            "error": type(e).__name__,
            "roadmap": "Roadmap generation temporarily unavailable. Please check API configuration."
        }
