# app/domain_detector.py
# -------------------------------------------------------
# Auto-detect student's department from resume text
# OR accept manual selection from frontend
# -------------------------------------------------------

import re
from app.domain_config import DEPARTMENT_JOBS, CGPA_PATTERN, PERCENTAGE_PATTERN


def auto_detect_department(resume_text: str) -> dict:
    """
    Scan resume text and detect which department the student belongs to.
    Returns best match + confidence score.
    """
    text_lower = resume_text.lower()
    scores = {}

    for dept_code, dept_data in DEPARTMENT_JOBS.items():
        detect_keywords = dept_data["detect_keywords"]
        match_count = 0
        matched_keywords = []

        for keyword in detect_keywords:
            if keyword in text_lower:
                match_count += 1
                matched_keywords.append(keyword)

        if match_count > 0:
            confidence = round((match_count / len(detect_keywords)) * 100, 1)
            scores[dept_code] = {
                "confidence": confidence,
                "matched_keywords": matched_keywords
            }

    if not scores:
        return {
            "detected": False,
            "department": None,
            "confidence": 0,
            "message": "Could not auto-detect department. Please select manually."
        }

    # Best match
    best_dept = max(scores, key=lambda x: scores[x]["confidence"])
    best_data = scores[best_dept]

    return {
        "detected": True,
        "department": best_dept,
        "department_label": DEPARTMENT_JOBS[best_dept]["label"],
        "confidence": best_data["confidence"],
        "matched_keywords": best_data["matched_keywords"],
        "all_scores": scores
    }


def get_department_info(dept_code: str) -> dict:
    """Get all department data for a given department code."""
    if not dept_code:
        return {}
    dept_code = str(dept_code).upper()
    if dept_code not in DEPARTMENT_JOBS:
        available = list(DEPARTMENT_JOBS.keys())
        raise ValueError(f"Department '{dept_code}' not found. Available: {available}")
    return DEPARTMENT_JOBS[dept_code]


def get_all_departments() -> list:
    """Return list of all available departments for dropdown."""
    return [
        {
            "code": code,
            "label": data["label"],
            "jobs": data["jobs"]
        }
        for code, data in DEPARTMENT_JOBS.items()
    ]


def extract_cgpa(resume_text: str) -> dict:
    """Extract CGPA or percentage from resume text."""
    text_lower = resume_text.lower()

    # Try CGPA
    cgpa_match = re.search(CGPA_PATTERN, text_lower)
    if cgpa_match:
        cgpa_value = float(cgpa_match.group(1))
        return {
            "type": "cgpa",
            "value": cgpa_value,
            "found": True,
            "out_of": 10.0 if cgpa_value <= 10 else 4.0
        }

    # Try percentage
    pct_matches = re.findall(PERCENTAGE_PATTERN, text_lower)
    if pct_matches:
        # Take the most likely academic percentage (between 50-100)
        for pct in pct_matches:
            val = float(pct)
            if 50 <= val <= 100:
                return {
                    "type": "percentage",
                    "value": val,
                    "found": True,
                    "cgpa_equivalent": round(val / 10, 1)
                }

    return {
        "type": None,
        "value": None,
        "found": False,
        "message": "CGPA/Percentage not found in resume"
    }


def check_cgpa_eligibility(cgpa_data: dict, dept_code: str) -> dict:
    """Check if student's CGPA meets the minimum for their department."""
    if not cgpa_data["found"]:
        return {
            "eligible": "unknown",
            "message": "CGPA not detected — add your CGPA/percentage to resume."
        }

    dept_info = DEPARTMENT_JOBS.get(dept_code.upper(), {})
    min_cgpa = dept_info.get("min_cgpa", 6.0)

    # Convert percentage to CGPA if needed
    if cgpa_data["type"] == "percentage":
        student_cgpa = cgpa_data["cgpa_equivalent"]
    else:
        student_cgpa = cgpa_data["value"]

    if student_cgpa >= min_cgpa:
        return {
            "eligible": True,
            "student_cgpa": student_cgpa,
            "min_required": min_cgpa,
            "message": f"✅ CGPA {student_cgpa} meets minimum requirement of {min_cgpa}"
        }
    else:
        gap = round(min_cgpa - student_cgpa, 2)
        return {
            "eligible": False,
            "student_cgpa": student_cgpa,
            "min_required": min_cgpa,
            "gap": gap,
            "message": f"⚠️ CGPA {student_cgpa} is below minimum {min_cgpa}. Gap: {gap} points."
        }
