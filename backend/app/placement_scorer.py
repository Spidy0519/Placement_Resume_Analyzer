# app/placement_scorer.py
# -------------------------------------------------------
# Full Placement Readiness Scoring Engine
# Combines: General Skills + Domain Skills + Template + Portfolio
# -------------------------------------------------------

import re
from app.domain_config import PLACEMENT_GENERAL_SKILLS, DEPARTMENT_JOBS
from app.domain_detector import extract_cgpa, check_cgpa_eligibility
from app.template_matcher import count_projects, check_portfolio_links


def find_keywords(text: str, keywords: list) -> dict:
    """Find keyword matches in text."""
    text_lower = text.lower()
    found, missing = [], []
    for kw in keywords:
        pattern = r'\b' + re.escape(kw.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found.append(kw)
        else:
            missing.append(kw)
    return {"found": found, "missing": missing}


def score_to_grade(score: float) -> dict:
    """Convert score to grade + color."""
    if score >= 85:
        return {"grade": "Excellent", "color": "green", "emoji": "✅"}
    elif score >= 70:
        return {"grade": "Good", "color": "blue", "emoji": "👍"}
    elif score >= 50:
        return {"grade": "Average", "color": "yellow", "emoji": "⚠️"}
    elif score >= 30:
        return {"grade": "Needs Work", "color": "orange", "emoji": "🔧"}
    else:
        return {"grade": "Missing", "color": "red", "emoji": "❌"}


def calculate_score(found: int, total: int) -> float:
    """Score 0-100 with curve."""
    if total == 0:
        return 0.0
    pct = (found / total) * 100
    if pct >= 70:
        return min(100.0, 80 + (pct - 70) * 0.67)
    elif pct >= 40:
        return 50 + (pct - 40) * 1.0
    else:
        return pct * 1.25


def score_general_skills(resume_text: str) -> dict:
    """Score all 6 general placement categories."""
    results = {}

    for category_key, category_data in PLACEMENT_GENERAL_SKILLS.items():
        keywords = category_data["keywords"]
        weight = category_data["weight"]
        matches = find_keywords(resume_text, keywords)
        found_count = len(matches["found"])
        total = len(keywords)
        raw_score = calculate_score(found_count, total)
        grade_info = score_to_grade(raw_score)

        results[category_key] = {
            "label": category_data["label"],
            "score": round(raw_score, 1),
            "weight": weight,
            "grade": grade_info["grade"],
            "color": grade_info["color"],
            "emoji": grade_info["emoji"],
            "keywords_found": matches["found"],
            "keywords_missing": matches["missing"][:8],
            "match_count": found_count,
            "total_keywords": total
        }

    return results


def score_domain_skills(resume_text: str, dept_code: str, selected_job: str = None) -> dict:
    """Score domain-specific skills for the student's department + job."""
    dept_code = dept_code.upper()
    dept_data = DEPARTMENT_JOBS.get(dept_code)

    if not dept_data:
        return {"error": f"Department {dept_code} not found"}

    results = {}

    if selected_job and selected_job in dept_data.get("required_skills", {}):
        # Score for specific selected job
        job_keywords = dept_data["required_skills"][selected_job]
        matches = find_keywords(resume_text, job_keywords)
        found_count = len(matches["found"])
        total = len(job_keywords)
        raw_score = calculate_score(found_count, total)
        grade_info = score_to_grade(raw_score)

        results["selected_job_match"] = {
            "job_title": selected_job,
            "score": round(raw_score, 1),
            "grade": grade_info["grade"],
            "color": grade_info["color"],
            "emoji": grade_info["emoji"],
            "skills_present": matches["found"],
            "skills_missing": matches["missing"],
            "match_count": found_count,
            "total_required": total
        }

    else:
        # Score against ALL jobs in department - find best match
        all_job_scores = {}
        for job_title, job_keywords in dept_data.get("required_skills", {}).items():
            matches = find_keywords(resume_text, job_keywords)
            found_count = len(matches["found"])
            total = len(job_keywords)
            raw_score = calculate_score(found_count, total)
            all_job_scores[job_title] = {
                "score": round(raw_score, 1),
                "skills_present": matches["found"],
                "skills_missing": matches["missing"],
            }

        # Best matching job
        if all_job_scores:
            best_job = max(all_job_scores, key=lambda x: all_job_scores[x]["score"])
            results["best_matching_job"] = {
                "job_title": best_job,
                **all_job_scores[best_job],
                **score_to_grade(all_job_scores[best_job]["score"])
            }
            results["all_job_scores"] = all_job_scores

    # DSA platform check
    dsa_platforms = dept_data.get("dsa_platforms", [])
    dsa_matches = find_keywords(resume_text, dsa_platforms)
    dsa_score = calculate_score(len(dsa_matches["found"]), len(dsa_platforms))
    results["dsa_aptitude"] = {
        "score": round(dsa_score, 1),
        **score_to_grade(dsa_score),
        "platforms_found": dsa_matches["found"],
        "platforms_missing": dsa_matches["missing"]
    }

    # Certification check
    certifications = dept_data.get("certifications", [])
    cert_matches = find_keywords(resume_text, certifications)
    cert_score = calculate_score(len(cert_matches["found"]), max(len(certifications), 1))
    results["certifications"] = {
        "score": round(cert_score, 1),
        **score_to_grade(cert_score),
        "certs_found": cert_matches["found"],
        "recommended_certs": certifications,
        "certs_missing": cert_matches["missing"]
    }

    return results


def compute_overall_placement_score(
    general_scores: dict,
    domain_scores: dict,
    template_match: dict,
    portfolio_check: dict,
    project_count: dict,
    cgpa_check: dict
) -> dict:
    """Compute final weighted placement readiness score."""

    score_components = {}

    # General skills (weighted avg)
    general_weighted = 0
    general_total_weight = 0
    for key, data in general_scores.items():
        if isinstance(data, dict) and "score" in data:
            w = data.get("weight", 10)
            general_weighted += data["score"] * w
            general_total_weight += w
    general_avg = general_weighted / general_total_weight if general_total_weight else 0
    score_components["general_skills"] = round(general_avg, 1)

    # Domain score
    if "selected_job_match" in domain_scores:
        domain_score = domain_scores["selected_job_match"]["score"]
    elif "best_matching_job" in domain_scores:
        domain_score = domain_scores["best_matching_job"]["score"]
    else:
        domain_score = 0
    score_components["domain_skills"] = round(domain_score, 1)

    # Template match
    score_components["template_match"] = template_match.get("template_match_score", 0)

    # Portfolio
    score_components["portfolio"] = portfolio_check.get("portfolio_score", 0)

    # Projects (0-100 based on count vs target 5)
    proj_count = project_count.get("estimated_count", 0)
    proj_score = min(100, (proj_count / 5) * 100)
    score_components["projects"] = round(proj_score, 1)

    # CGPA
    if cgpa_check.get("eligible") == True:
        cgpa_score = 100.0
    elif cgpa_check.get("eligible") == False:
        gap = cgpa_check.get("gap", 1.0)
        cgpa_score = max(0, 100 - (gap * 20))
    else:
        cgpa_score = 50.0  # Unknown = partial credit
    score_components["academics"] = round(cgpa_score, 1)

    # DSA
    dsa_info = domain_scores.get("dsa_aptitude", {})
    score_components["dsa_aptitude"] = dsa_info.get("score", 0)

    # Weights for final score
    weights = {
        "domain_skills": 25,
        "general_skills": 20,
        "template_match": 15,
        "dsa_aptitude": 15,
        "projects": 10,
        "portfolio": 8,
        "academics": 7
    }

    final_score = sum(
        score_components.get(k, 0) * (w / 100)
        for k, w in weights.items()
    )

    grade_info = score_to_grade(final_score)

    return {
        "placement_readiness_score": round(final_score, 1),
        "grade": grade_info["grade"],
        "color": grade_info["color"],
        "emoji": grade_info["emoji"],
        "component_scores": score_components,
        "weights_used": weights,
        "interpretation": get_placement_interpretation(final_score)
    }


def get_placement_interpretation(score: float) -> str:
    if score >= 85:
        return "🌟 Excellent! You're highly placement-ready. Apply for top companies now."
    elif score >= 70:
        return "👍 Good placement readiness. Fix the weak areas and you'll stand out."
    elif score >= 50:
        return "⚠️ Average readiness. Focus on domain skills and projects to improve."
    elif score >= 30:
        return "🔧 Significant gaps found. Follow the AI suggestions to improve systematically."
    else:
        return "❌ Resume needs major work. Start with the template and add all missing sections."
