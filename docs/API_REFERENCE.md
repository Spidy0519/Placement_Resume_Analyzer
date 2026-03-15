# 📡 API Reference — Placement Resume Analyzer

Base URL: `http://localhost:8000`
Interactive Docs: `http://localhost:8000/docs`

---

## All Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info + all routes |
| GET | `/health` | Server health check |
| POST | `/upload-template` | Admin: Upload college DOCX template |
| GET | `/departments` | All departments list (for dropdown) |
| GET | `/departments/{code}/jobs` | Jobs for a specific department |
| POST | `/upload-resume` | Student uploads resume (PDF/DOCX) |
| POST | `/detect-department` | Auto or manual department set |
| POST | `/get-placement-scores` | Full 8-category scoring |
| POST | `/get-ai-analysis` | 10-section analysis |
| POST | `/chat` | Ask resume questions |
| DELETE | `/session/{id}` | Clear session |

---

## Request / Response Examples

### POST `/upload-resume`
**Request:** `multipart/form-data` with `file` field

**Response:**
```json
{
  "success": true,
  "session_id": "abc123-uuid",
  "filename": "myresume.pdf",
  "word_count": 450,
  "message": "Resume uploaded! Call /detect-department next."
}
```

### POST `/get-placement-scores`
**Request:**
```json
{
  "session_id": "abc123-uuid",
  "department": "CSE",
  "selected_job": "Full Stack Developer"
}
```

**Response:**
```json
{
  "success": true,
  "overall_placement_score": {
    "placement_readiness_score": 73.5,
    "grade": "Good",
    "color": "blue",
    "emoji": "👍"
  },
  "general_skills": {
    "office_tools": { "score": 72, "grade": "Good", "keywords_found": ["excel","word"], "keywords_missing": ["pivot table"] },
    "communication": { "score": 55, "grade": "Average" },
    "programming_basics": { "score": 80, "grade": "Excellent" },
    "dsa_aptitude": { "score": 40, "grade": "Needs Work" },
    "portfolio": { "score": 60, "grade": "Average" },
    "academics": { "score": 90, "grade": "Excellent" }
  },
  "domain_skills": {
    "selected_job_match": {
      "job_title": "Full Stack Developer",
      "score": 68,
      "skills_present": ["React", "JavaScript", "HTML"],
      "skills_missing": ["Node.js", "Docker", "MongoDB"]
    },
    "dsa_aptitude": { "score": 40, "platforms_found": ["hackerrank"], "platforms_missing": ["leetcode"] },
    "certifications": { "score": 50, "certs_found": [], "recommended_certs": ["Full Stack Development Certification"] }
  },
  "template_match": {
    "template_match_score": 65.2,
    "grade": "Good Match",
    "missing_keywords": ["docker", "agile", "rest api"]
  },
  "portfolio": {
    "portfolio_score": 60,
    "present": ["github", "linkedin"],
    "absent": ["portfolio", "leetcode"]
  },
  "projects": {
    "estimated_count": 3,
    "status": "Average - Add 2-3 more projects"
  },
  "academics": {
    "cgpa": { "type": "cgpa", "value": 8.2, "found": true },
    "eligibility": { "eligible": true, "student_cgpa": 8.2, "min_required": 7.0 }
  }
}
```
