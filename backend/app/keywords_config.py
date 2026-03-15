# app/keywords_config.py
# -------------------------------------------------------
# Section-wise keywords for Resume Scoring
# Add / remove keywords based on your job domain
# -------------------------------------------------------

SECTION_KEYWORDS = {
    "contact_info": {
        "weight": 10,
        "keywords": [
            "email", "phone", "linkedin", "github", "portfolio",
            "address", "mobile", "contact", "website", "twitter"
        ]
    },
    "summary": {
        "weight": 10,
        "keywords": [
            "summary", "objective", "profile", "about", "overview",
            "career objective", "professional summary", "introduction"
        ]
    },
    "skills": {
        "weight": 25,
        "keywords": [
            # Programming Languages
            "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
            "kotlin", "swift", "php", "ruby", "scala", "r",
            # Web
            "react", "angular", "vue", "node.js", "nodejs", "html", "css",
            "fastapi", "django", "flask", "express", "nextjs", "tailwind",
            # Data / AI / ML
            "machine learning", "deep learning", "nlp", "computer vision",
            "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy",
            "data analysis", "data science", "llm", "rag", "transformers",
            # Cloud & DevOps
            "aws", "azure", "gcp", "docker", "kubernetes", "ci/cd",
            "jenkins", "github actions", "terraform", "linux",
            # Databases
            "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
            "firebase", "dynamodb", "sqlite",
            # Tools
            "git", "jira", "figma", "postman", "swagger", "rest api", "graphql"
        ]
    },
    "experience": {
        "weight": 30,
        "keywords": [
            "experience", "work experience", "employment", "professional experience",
            "internship", "intern", "job", "company", "organization",
            "developed", "built", "designed", "implemented", "led", "managed",
            "collaborated", "achieved", "improved", "optimized", "deployed",
            "created", "maintained", "responsible", "worked", "contributed",
            "years", "months", "full-time", "part-time", "remote", "onsite"
        ]
    },
    "education": {
        "weight": 15,
        "keywords": [
            "education", "degree", "bachelor", "master", "phd", "b.tech", "m.tech",
            "b.e", "m.e", "b.sc", "m.sc", "mba", "diploma",
            "university", "college", "institute", "school",
            "gpa", "cgpa", "percentage", "graduated", "pursuing",
            "computer science", "information technology", "engineering"
        ]
    },
    "projects": {
        "weight": 20,
        "keywords": [
            "project", "projects", "personal project", "academic project",
            "github", "deployed", "built", "developed", "created",
            "live", "demo", "link", "repository", "source code",
            "tech stack", "technologies used", "tools used"
        ]
    },
    "certifications": {
        "weight": 10,
        "keywords": [
            "certification", "certificate", "certified", "course",
            "aws certified", "google certified", "microsoft certified",
            "coursera", "udemy", "edx", "nptel", "linkedin learning",
            "hackerrank", "leetcode", "badge", "credential"
        ]
    },
    "achievements": {
        "weight": 10,
        "keywords": [
            "achievement", "award", "honor", "recognition", "winner",
            "hackathon", "competition", "rank", "scholarship",
            "publication", "research", "paper", "presented", "speaker"
        ]
    }
}

# ATS (Applicant Tracking System) critical keywords - these MUST be present
ATS_CRITICAL = [
    "email", "phone", "linkedin",
    "experience", "education", "skills",
    "python", "javascript", "git"
]

# Ideal resume format for RAG knowledge base
IDEAL_RESUME_FORMAT = """
IDEAL RESUME FORMAT AND BEST PRACTICES:

1. CONTACT INFORMATION:
   - Full Name prominently displayed
   - Professional email address
   - Phone number with country code
   - LinkedIn profile URL
   - GitHub/Portfolio URL
   - City, State (no full address needed)

2. PROFESSIONAL SUMMARY (3-4 lines):
   - Mention years of experience
   - Key skills and technologies
   - What value you bring
   - Career goal aligned with job

3. TECHNICAL SKILLS (categorized):
   - Programming Languages: Python, JavaScript, Java...
   - Frameworks: React, FastAPI, Django...
   - Tools & Technologies: Git, Docker, AWS...
   - Databases: MySQL, MongoDB, PostgreSQL...

4. WORK EXPERIENCE (reverse chronological):
   - Company Name | Job Title | Start Date – End Date | Location
   - Use bullet points with ACTION VERBS
   - Include quantifiable achievements (%, numbers, scale)
   - 3-5 bullets per role
   - Show impact: "Improved performance by 40%"

5. PROJECTS (2-4 projects):
   - Project Name | Tech Stack Used
   - 2-3 bullet points explaining what + impact
   - Include GitHub/Live link

6. EDUCATION:
   - Degree | Institution | Year | CGPA/Percentage

7. CERTIFICATIONS (if any):
   - Certificate Name | Issuer | Year

8. ACHIEVEMENTS (optional but powerful):
   - Hackathons, awards, publications

FORMATTING RULES:
- Keep to 1 page (fresher) or max 2 pages
- Use consistent fonts
- No photos, no graphics in ATS resumes
- Use bullet points not paragraphs
- Quantify everything possible
- Use keywords from job description
"""
