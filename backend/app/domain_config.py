# app/domain_config.py
# -------------------------------------------------------
# College Department → Job Roles → Required Skills
# 
# NOTE: This is SAMPLE DATA.
# When you get your college PDF → replace the jobs and
# required_skills with your actual data.
# 
# Structure:
# DEPARTMENT_JOBS[dept] = {
#   "jobs": [...],
#   "required_skills": [...],
#   "min_cgpa": float,
#   "certifications": [...],
#   "detect_keywords": [...]   ← used for auto-detection
# }
# -------------------------------------------------------

DEPARTMENT_JOBS = {

    "CSE": {
        "label": "Computer Science & Engineering",
        "detect_keywords": [
            "computer science", "cse", "software engineering", "b.tech cse",
            "be cse", "computer engineering"
        ],
        "jobs": [
            "Software Developer",
            "Full Stack Developer",
            "Backend Developer",
            "Frontend Developer",
            "DevOps Engineer",
            "Cloud Engineer",
            "Mobile App Developer",
            "Software Test Engineer",
            "System Analyst",
            "Product Manager"
        ],
        "required_skills": {
            "Software Developer": [
                "python", "java", "javascript", "data structures", "algorithms",
                "oop", "git", "sql", "rest api", "problem solving"
            ],
            "Full Stack Developer": [
                "react", "nodejs", "express", "mongodb", "sql", "html", "css",
                "javascript", "git", "rest api", "docker"
            ],
            "Backend Developer": [
                "python", "java", "fastapi", "django", "flask", "postgresql",
                "redis", "docker", "rest api", "microservices", "git"
            ],
            "Frontend Developer": [
                "react", "html", "css", "javascript", "typescript", "tailwind",
                "figma", "responsive design", "git", "nextjs"
            ],
            "DevOps Engineer": [
                "docker", "kubernetes", "aws", "ci/cd", "jenkins", "linux",
                "terraform", "ansible", "git", "python", "shell scripting"
            ],
            "Cloud Engineer": [
                "aws", "azure", "gcp", "docker", "kubernetes", "terraform",
                "linux", "networking", "python", "security"
            ],
        },
        "min_cgpa": 6.5,
        "certifications": [
            "AWS Certified", "Google Cloud", "Azure Fundamentals",
            "Oracle Java", "Meta Frontend Developer", "NPTEL Python"
        ],
        "dsa_platforms": ["leetcode", "hackerrank", "codeforces", "geeksforgeeks", "codechef"],
        "min_projects": 3,
        "recommended_projects": 5
    },

    "IT": {
        "label": "Information Technology",
        "detect_keywords": [
            "information technology", "b.tech it", "be it", "bsc it", " it "
        ],
        "jobs": [
            "Software Developer",
            "Web Developer",
            "Database Administrator",
            "Network Engineer",
            "IT Support Engineer",
            "Cybersecurity Analyst",
            "ERP Consultant",
            "Business Analyst",
            "System Administrator",
            "QA Engineer"
        ],
        "required_skills": {
            "Web Developer": [
                "html", "css", "javascript", "react", "php", "mysql",
                "nodejs", "git", "rest api", "bootstrap"
            ],
            "Database Administrator": [
                "mysql", "postgresql", "oracle", "mongodb", "sql", "backup",
                "performance tuning", "plsql", "linux", "indexing"
            ],
            "QA Engineer": [
                "selenium", "testing", "manual testing", "test cases",
                "jira", "postman", "api testing", "python", "automation", "sql"
            ],
            "Cybersecurity Analyst": [
                "networking", "ethical hacking", "linux", "firewalls",
                "penetration testing", "siem", "python", "cryptography"
            ],
        },
        "min_cgpa": 6.0,
        "certifications": [
            "CompTIA Security+", "Cisco CCNA", "CEH", "ISTQB",
            "AWS Cloud Practitioner", "NPTEL", "Google IT Support"
        ],
        "dsa_platforms": ["hackerrank", "leetcode", "geeksforgeeks"],
        "min_projects": 3,
        "recommended_projects": 5
    },

    "AIDS": {
        "label": "Artificial Intelligence & Data Science",
        "detect_keywords": [
            "artificial intelligence", "data science", "aids", "ai and ds",
            "ai & ds", "b.tech aids", "machine learning"
        ],
        "jobs": [
            "Data Scientist",
            "Machine Learning Engineer",
            "AI Engineer",
            "Data Analyst",
            "NLP Engineer",
            "Computer Vision Engineer",
            "MLOps Engineer",
            "Business Intelligence Analyst",
            "Research Scientist",
            "Prompt Engineer"
        ],
        "required_skills": {
            "Data Scientist": [
                "python", "pandas", "numpy", "scikit-learn", "statistics",
                "machine learning", "sql", "matplotlib", "seaborn", "jupyter"
            ],
            "Machine Learning Engineer": [
                "python", "tensorflow", "pytorch", "scikit-learn", "mlflow",
                "docker", "aws", "feature engineering", "model deployment", "git"
            ],
            "AI Engineer": [
                "python", "llm", "langchain", "rag", "transformers", "openai",
                "fastapi", "vector database", "prompt engineering", "huggingface"
            ],
            "Data Analyst": [
                "python", "sql", "excel", "tableau", "power bi", "statistics",
                "pandas", "data visualization", "google sheets", "communication"
            ],
            "NLP Engineer": [
                "python", "nlp", "transformers", "bert", "spacy", "nltk",
                "pytorch", "huggingface", "text classification", "rag"
            ],
        },
        "min_cgpa": 7.0,
        "certifications": [
            "Google Data Analytics", "IBM Data Science", "DeepLearning.AI",
            "Kaggle Certifications", "AWS ML Specialty", "TensorFlow Developer"
        ],
        "dsa_platforms": ["kaggle", "leetcode", "hackerrank"],
        "min_projects": 4,
        "recommended_projects": 6
    },

    "ECE": {
        "label": "Electronics & Communication Engineering",
        "detect_keywords": [
            "electronics", "communication engineering", "ece", "b.tech ece",
            "be ece", "vlsi", "embedded systems"
        ],
        "jobs": [
            "Embedded Systems Engineer",
            "VLSI Design Engineer",
            "IoT Developer",
            "Signal Processing Engineer",
            "Hardware Engineer",
            "Network Engineer",
            "RF Engineer",
            "Software Developer",
            "Test Engineer",
            "Telecom Engineer"
        ],
        "required_skills": {
            "Embedded Systems Engineer": [
                "c", "c++", "arm", "rtos", "microcontroller", "arduino",
                "raspberry pi", "i2c", "spi", "uart", "pcb design"
            ],
            "IoT Developer": [
                "python", "arduino", "raspberry pi", "mqtt", "aws iot",
                "sensors", "c", "embedded c", "networking", "firebase"
            ],
            "Software Developer": [
                "python", "java", "c++", "git", "sql", "algorithms",
                "data structures", "rest api", "oop", "problem solving"
            ],
        },
        "min_cgpa": 6.5,
        "certifications": [
            "NPTEL Embedded Systems", "Cisco CCNA", "Texas Instruments",
            "ARM Cortex", "AWS IoT", "MATLAB Certifications"
        ],
        "dsa_platforms": ["hackerrank", "leetcode", "geeksforgeeks"],
        "min_projects": 3,
        "recommended_projects": 5
    },

    "EEE": {
        "label": "Electrical & Electronics Engineering",
        "detect_keywords": [
            "electrical", "eee", "b.tech eee", "be eee",
            "electrical engineering", "power systems"
        ],
        "jobs": [
            "Electrical Engineer",
            "Power Systems Engineer",
            "Automation Engineer",
            "PLC Programmer",
            "SCADA Engineer",
            "Software Developer",
            "Data Analyst",
            "Embedded Engineer",
            "Energy Consultant",
            "Control Systems Engineer"
        ],
        "required_skills": {
            "Automation Engineer": [
                "plc", "scada", "hmi", "python", "autocad", "electrical drawings",
                "siemens", "allen bradley", "control systems", "sensors"
            ],
            "Software Developer": [
                "python", "java", "c++", "git", "sql", "algorithms",
                "data structures", "matlab", "oop", "problem solving"
            ],
            "Data Analyst": [
                "python", "excel", "sql", "power bi", "tableau",
                "statistics", "pandas", "data visualization", "matlab"
            ],
        },
        "min_cgpa": 6.0,
        "certifications": [
            "NPTEL Power Systems", "Siemens TIA Portal", "AutoCAD",
            "MATLAB Simulink", "Google Data Analytics", "Python for Engineers"
        ],
        "dsa_platforms": ["hackerrank", "geeksforgeeks"],
        "min_projects": 2,
        "recommended_projects": 4
    },

    "CYBER": {
        "label": "Cyber Security",
        "detect_keywords": [
            "cyber security", "cybersecurity", "cyber", "information security",
            "b.tech cyber", "ethical hacking"
        ],
        "jobs": [
            "Cybersecurity Analyst",
            "Penetration Tester",
            "Security Operations Center (SOC) Analyst",
            "Network Security Engineer",
            "Incident Response Analyst",
            "Malware Analyst",
            "Cloud Security Engineer",
            "Application Security Engineer",
            "Forensic Analyst",
            "GRC Analyst"
        ],
        "required_skills": {
            "Cybersecurity Analyst": [
                "networking", "linux", "python", "siem", "firewalls",
                "vulnerability assessment", "wireshark", "nmap", "incident response"
            ],
            "Penetration Tester": [
                "kali linux", "metasploit", "burp suite", "nmap", "python",
                "networking", "web vulnerabilities", "owasp", "reporting", "ethical hacking"
            ],
            "SOC Analyst": [
                "siem", "splunk", "log analysis", "networking", "threat hunting",
                "incident response", "python", "vulnerability management", "linux"
            ],
        },
        "min_cgpa": 6.5,
        "certifications": [
            "CEH", "CompTIA Security+", "CompTIA CySA+",
            "OSCP", "Google Cybersecurity", "EC-Council"
        ],
        "dsa_platforms": ["hackthebox", "tryhackme", "picoctf", "leetcode"],
        "min_projects": 3,
        "recommended_projects": 5
    },

    "MECH": {
        "label": "Mechanical Engineering",
        "detect_keywords": [
            "mechanical", "mech", "b.tech mech", "be mech",
            "mechanical engineering", "automobile"
        ],
        "jobs": [
            "Mechanical Design Engineer",
            "Manufacturing Engineer",
            "CAD/CAM Engineer",
            "Quality Engineer",
            "Production Engineer",
            "Automation Engineer",
            "Software Developer",
            "Data Analyst",
            "Maintenance Engineer",
            "R&D Engineer"
        ],
        "required_skills": {
            "Mechanical Design Engineer": [
                "autocad", "solidworks", "catia", "ansys", "3d modeling",
                "gd&t", "fea", "product design", "manufacturing processes"
            ],
            "Software Developer": [
                "python", "c++", "matlab", "git", "problem solving",
                "data structures", "oop", "algorithms", "sql"
            ],
        },
        "min_cgpa": 6.0,
        "certifications": [
            "CATIA Certification", "SolidWorks CSWA", "ANSYS",
            "AutoCAD", "Six Sigma", "Python for Engineers"
        ],
        "dsa_platforms": ["hackerrank", "geeksforgeeks"],
        "min_projects": 2,
        "recommended_projects": 4
    },

    "CIVIL": {
        "label": "Civil Engineering",
        "detect_keywords": [
            "civil engineering", "b.tech civil", "be civil", "structural",
            "construction", "surveying"
        ],
        "jobs": [
            "Structural Engineer",
            "Site Engineer",
            "Construction Engineer",
            "Transportation Engineer",
            "Geotechnical Engineer",
            "Environmental Engineer",
            "Water Resources Engineer",
            "Quantity Surveyor",
            "Project Engineer",
            "Urban Planning Engineer"
        ],
        "required_skills": {
            "Structural Engineer": ["staad pro", "etabs", "autocad", "concrete design", "steel design"],
            "Site Engineer": ["autocad", "project management", "surveying", "estimation"],
            "Construction Engineer": ["autocad", "primavera", "construction management", "billing"],
            "Project Engineer": ["primavera", "ms project", "planning", "scheduling"]
        },
        "min_cgpa": 6.5,
        "certifications": [
            "AutoCAD", "STAAD Pro", "Primavera", "Revit",
            "Project Management Professional (PMP)", "NPTEL Civil"
        ],
        "dsa_platforms": ["geeksforgeeks", "hackerrank"],
        "min_projects": 2,
        "recommended_projects": 4
    }
}

# -------------------------------------------------------
# Placement-specific general skills (all departments)
# -------------------------------------------------------
PLACEMENT_GENERAL_SKILLS = {
    "office_tools": {
        "label": "Office Tools",
        "weight": 8,
        "keywords": [
            "microsoft excel", "excel", "ms excel", "vlookup", "pivot table",
            "microsoft word", "ms word", "word",
            "microsoft powerpoint", "powerpoint", "ppt", "ms office",
            "google sheets", "google docs", "google slides",
            "data entry", "spreadsheet"
        ]
    },
    "communication": {
        "label": "Communication Skills",
        "weight": 8,
        "keywords": [
            "communication", "english", "oral communication", "written communication",
            "presentation", "public speaking", "technical writing",
            "report writing", "documentation", "team collaboration",
            "interpersonal", "leadership", "problem solving", "critical thinking",
            "time management", "adaptability"
        ]
    },
    "programming_basics": {
        "label": "Programming Basics",
        "weight": 15,
        "keywords": [
            "python", "java", "javascript", "c", "c++", "c#",
            "programming", "coding", "algorithm", "data structures",
            "oop", "object oriented", "functions", "arrays", "loops",
            "debugging", "logic building"
        ]
    },
    "dsa_aptitude": {
        "label": "DSA & Aptitude",
        "weight": 12,
        "keywords": [
            "leetcode", "hackerrank", "geeksforgeeks", "codechef", "codeforces",
            "hackerearth", "competitive programming", "data structures",
            "algorithms", "dynamic programming", "problem solving",
            "aptitude", "logical reasoning", "quantitative", "dsa",
            "binary search", "sorting", "graph", "tree", "linked list"
        ]
    },
    "portfolio": {
        "label": "Portfolio & Online Presence",
        "weight": 10,
        "keywords": [
            "github", "linkedin", "portfolio", "website", "blog",
            "kaggle", "stackoverflow", "behance", "dribbble",
            "open source", "contribution", "gitlab", "bitbucket"
        ]
    },
    "academics": {
        "label": "Academic Performance",
        "weight": 10,
        "keywords": [
            "cgpa", "gpa", "percentage", "marks", "grade",
            "first class", "distinction", "merit", "rank",
            "academic achievement", "semester"
        ]
    }
}

# CGPA extraction pattern
CGPA_PATTERN = r'(?:cgpa|gpa|score)[:\s]*([0-9]+\.?[0-9]*)'
PERCENTAGE_PATTERN = r'([0-9]+\.?[0-9]*)\s*%'
