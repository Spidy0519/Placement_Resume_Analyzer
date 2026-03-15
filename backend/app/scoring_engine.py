# app/scoring_engine.py
# -------------------------------------------------------
# Section-wise keyword matching and scoring logic
# Each section gets a score 0-100
# -------------------------------------------------------

import re
from app.keywords_config import SECTION_KEYWORDS, ATS_CRITICAL


def normalize_text(text: str) -> str:
    """Lowercase and clean for matching."""
    return text.lower()


def find_keyword_matches(text: str, keywords: list[str]) -> dict:
    """Find which keywords are present in the text."""
    text_lower = normalize_text(text)
    found = []
    missing = []
    for keyword in keywords:
        # Word boundary match for accuracy
        pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found.append(keyword)
        else:
            missing.append(keyword)
    return {"found": found, "missing": missing}


def calculate_section_score(found: int, total: int) -> float:
    """Calculate score 0-100 based on keyword match ratio."""
    if total == 0:
        return 0.0
    # Score formula: percentage of keywords found, capped at 100
    raw_score = (found / total) * 100
    # Apply a curve - finding 60% keywords = 80 score (more realistic)
    if raw_score >= 80:
        return 100.0
    elif raw_score >= 60:
        return 85.0 + (raw_score - 60) * 0.75
    elif raw_score >= 40:
        return 65.0 + (raw_score - 40) * 1.0
    elif raw_score >= 20:
        return 40.0 + (raw_score - 20) * 1.25
    else:
        return raw_score * 2.0


def get_section_grade(score: float) -> str:
    """Convert numeric score to grade."""
    if score >= 85:
        return "Excellent"
    elif score >= 70:
        return "Good"
    elif score >= 50:
        return "Average"
    elif score >= 30:
        return "Needs Work"
    else:
        return "Missing"


def check_ats_compatibility(text: str) -> dict:
    """Check ATS critical keyword presence."""
    text_lower = normalize_text(text)
    passed = []
    failed = []
    for keyword in ATS_CRITICAL:
        pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
        if re.search(pattern, text_lower):
            passed.append(keyword)
        else:
            failed.append(keyword)

    ats_score = (len(passed) / len(ATS_CRITICAL)) * 100
    return {
        "ats_score": round(ats_score, 1),
        "passed": passed,
        "failed": failed,
        "is_ats_friendly": ats_score >= 70
    }


def estimate_resume_length(word_count: int) -> dict:
    """Check if resume length is appropriate."""
    if word_count < 200:
        status = "Too Short"
        suggestion = "Resume seems very short. Add more details to projects and experience."
    elif word_count <= 600:
        status = "Perfect (1 page)"
        suggestion = "Great length for a fresher or junior developer."
    elif word_count <= 1000:
        status = "Good (1-2 pages)"
        suggestion = "Good length for experienced professionals."
    elif word_count <= 1400:
        status = "Slightly Long"
        suggestion = "Consider trimming to keep it under 2 pages."
    else:
        status = "Too Long"
        suggestion = "Resume is too long. Recruiters spend ~6 seconds per resume. Trim to max 2 pages."

    return {"word_count": word_count, "status": status, "suggestion": suggestion}


def score_resume(resume_data: dict) -> dict:
    """
    Main scoring function.
    Input: parsed resume data
    Output: detailed section scores + overall score
    """
    text = resume_data["cleaned_text"]
    word_count = resume_data["word_count"]

    section_results = {}
    total_weighted_score = 0
    total_weight = 0

    for section_name, section_config in SECTION_KEYWORDS.items():
        keywords = section_config["keywords"]
        weight = section_config["weight"]

        matches = find_keyword_matches(text, keywords)
        found_count = len(matches["found"])
        total_keywords = len(keywords)

        raw_score = calculate_section_score(found_count, total_keywords)
        grade = get_section_grade(raw_score)

        section_results[section_name] = {
            "score": round(raw_score, 1),
            "grade": grade,
            "weight": weight,
            "keywords_found": matches["found"],
            "keywords_missing": matches["missing"][:10],  # Top 10 missing only
            "found_count": found_count,
            "total_keywords": total_keywords,
            "match_percentage": round((found_count / total_keywords) * 100, 1)
        }

        weighted = raw_score * (weight / 100)
        total_weighted_score += weighted
        total_weight += weight

    # Normalize to 100
    overall_score = (total_weighted_score / total_weight) * 100 if total_weight > 0 else 0

    # ATS check
    ats_result = check_ats_compatibility(text)

    # Length check
    length_result = estimate_resume_length(word_count)

    # Identify top strengths and weaknesses
    scored_sections = sorted(
        section_results.items(),
        key=lambda x: x[1]["score"],
        reverse=True
    )
    strengths = [s[0] for s in scored_sections[:3] if s[1]["score"] >= 50]
    weaknesses = [s[0] for s in scored_sections if s[1]["score"] < 50]

    return {
        "overall_score": round(overall_score, 1),
        "overall_grade": get_section_grade(overall_score),
        "section_scores": section_results,
        "ats_check": ats_result,
        "length_check": length_result,
        "strengths": strengths,
        "weaknesses": weaknesses
    }
