import os
import json
import io
import asyncio
import PyPDF2
import hashlib
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from groq import AsyncGroq

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("WARNING: GROQ_API_KEY not found in environment variables.")
    groq_client = None
else:
    groq_client = AsyncGroq(api_key=GROQ_API_KEY)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================================================================
# SKILL TAXONOMY — used to guide the model toward precise, actionable output
# ==============================================================================

SKILL_TAXONOMY = {
    "software": {
        "hard_skill_categories": [
            "Languages", "Frameworks", "Databases", "Cloud & DevOps",
            "Testing", "Architecture", "Version Control", "APIs"
        ],
        "soft_skill_categories": ["Communication", "Collaboration", "Problem Solving", "Leadership"]
    },
    "data": {
        "hard_skill_categories": [
            "ML Libraries", "Data Processing", "Databases", "Visualization",
            "Statistical Methods", "Big Data Tools", "Cloud ML Platforms"
        ],
        "soft_skill_categories": ["Analytical Thinking", "Storytelling with Data", "Research", "Communication"]
    },
    "design": {
        "hard_skill_categories": [
            "Design Tools", "Prototyping", "User Research", "Design Systems",
            "Accessibility", "Motion Design", "Front-End Basics"
        ],
        "soft_skill_categories": ["Empathy", "Critique", "Presentation", "Collaboration"]
    },
    "default": {
        "hard_skill_categories": [
            "Domain Tools", "Methodologies", "Certifications",
            "Reporting & Analytics", "Communication Platforms"
        ],
        "soft_skill_categories": ["Leadership", "Stakeholder Management", "Decision Making", "Communication"]
    }
}


# ==============================================================================
# FEW-SHOT EXAMPLES — redesigned with explicit THREE-PASS reasoning structure
#
# PASS 1 — INVENTORY: Extract what the resume HAS vs what the JD REQUIRES
# PASS 2 — GAP ANALYSIS: Classify each gap as CRITICAL / MODERATE / MINOR
# PASS 3 — SCORING: Apply rubric scores based on gap severity, not gut feel
#
# This structure forces the model to be systematic and prevents score inflation.
# ==============================================================================

FEW_SHOT_EXAMPLES = {

    "software": """
===== FEW-SHOT EXAMPLE: SOFTWARE ENGINEERING =====

RESUME TEXT:
"Python developer with 3 years of experience building REST APIs using Django and Flask. Worked with PostgreSQL, Redis caching, and Git-based workflows. Deployed services to internal servers. Collaborated in Agile sprint teams. B.Sc Computer Science."

JOB DESCRIPTION:
"Backend Python Engineer — 3+ years required. Must have: Django or FastAPI, PostgreSQL, AWS (EC2/Lambda/S3), Docker, CI/CD pipelines. Nice to have: Redis, Kubernetes, Terraform."

--- PASS 1: INVENTORY ---
Resume HAS:    Python ✓ | Django ✓ | Flask ✓ | PostgreSQL ✓ | Redis ✓ | REST APIs ✓ | Git ✓ | Agile ✓ | B.Sc CS ✓
JD REQUIRES:   Python ✓ | Django ✓ | PostgreSQL ✓ | AWS ✗ | Docker ✗ | CI/CD ✗ | FastAPI (has Django — partial ✓)
JD NICE-TO-HAVE: Redis ✓ | Kubernetes ✗ | Terraform ✗

--- PASS 2: GAP ANALYSIS ---
CRITICAL GAPS (required, completely absent):
  - AWS (EC2, Lambda, S3) — core deployment requirement, no equivalent found
  - Docker — containerization, zero evidence of container usage
  - CI/CD pipelines — "deployed to internal servers" suggests manual deployment, no automation

MODERATE GAPS (required, partially covered):
  - FastAPI — candidate has Django/Flask, transferable but not the same

MINOR GAPS (nice-to-have, absent):
  - Kubernetes — orchestration, not required
  - Terraform — IaC, not required

STRENGTHS PRESENT:
  - Core Python/Django/PostgreSQL stack: strong match
  - Redis caching experience (nice-to-have): bonus point
  - Agile experience: team culture match

--- PASS 3: SCORING RUBRIC ---
Technical Skills (50 pts):
  Core language/framework: Python + Django = 18/20
  Database: PostgreSQL + Redis = 9/10
  Cloud/DevOps (AWS + Docker + CI/CD all missing): 4/15
  APIs and architecture: REST APIs solid = 4/5
  → Technical subtotal: 35/50

Experience (30 pts):
  Years: 3 years = meets minimum = 16/20
  Role alignment: Backend dev = direct match = 8/10
  → Experience subtotal: 24/30

Education (10 pts):
  B.Sc Computer Science = direct match = 10/10

Context/Terminology (10 pts):
  Strong backend language, cloud/infra terminology absent = 6/10

TOTAL: 35 + 24 + 10 + 6 = 75/100

OUTPUT JSON:
{
    "calculation_reasoning": "PASS 1 — Inventory: Python, Django, PostgreSQL, Redis, REST APIs, Git, Agile found in resume. AWS, Docker, CI/CD absent entirely. PASS 2 — Critical gaps: AWS (required deployment platform, no equivalent), Docker (containerization, zero evidence), CI/CD (manual deployment pattern detected). Moderate gaps: FastAPI listed but Django covers similar ground. Redis is a bonus as a nice-to-have. PASS 3 — Technical(35/50): Core Python/Django/DB stack scores well (31/35), cloud/DevOps block drags score down (4/15 due to 3 critical absences). Experience(24/30): 3 years meets minimum, backend role is direct alignment. Education(10/10): B.Sc CS is a perfect match. Context(6/10): Backend terminology solid, cloud vocabulary entirely missing. Final: 75/100.",
    "match_score": 75,
    "main_skills": [
        { "skill": "Python", "status": "matched", "weight": "critical" },
        { "skill": "Django", "status": "matched", "weight": "critical" },
        { "skill": "PostgreSQL", "status": "matched", "weight": "critical" },
        { "skill": "REST APIs", "status": "matched", "weight": "critical" },
        { "skill": "Redis", "status": "matched", "weight": "nice-to-have" },
        { "skill": "Agile/Scrum", "status": "matched", "weight": "moderate" },
        { "skill": "Git", "status": "matched", "weight": "moderate" }
    ],
    "missing_skills": [
        { "skill": "AWS (EC2, Lambda, S3)", "severity": "critical", "reason": "Primary deployment platform in JD; no cloud experience found" },
        { "skill": "Docker", "severity": "critical", "reason": "Containerization required; manual server deployment pattern detected" },
        { "skill": "CI/CD Pipelines", "severity": "critical", "reason": "Automation required; no mention of GitHub Actions, Jenkins, or CircleCI" },
        { "skill": "Kubernetes", "severity": "minor", "reason": "Nice-to-have orchestration tool; not blocking" },
        { "skill": "Terraform", "severity": "minor", "reason": "Nice-to-have IaC; not blocking" }
    ],
    "optimized_bullets": [
        { "topic": "AWS & DOCKER", "bullet": "Deployed Django REST APIs to production environments; actively building AWS (EC2/Lambda) and Docker containerization skills to support cloud-native deployments" },
        { "topic": "POSTGRESQL", "bullet": "Managed PostgreSQL and Redis caching layers for high-read endpoints, aligning with cloud-scale database patterns used on AWS RDS" },
        { "topic": "CI/CD", "bullet": "Collaborated in Agile sprints using Git branching strategies; integrating GitHub Actions CI/CD workflows for automated testing and deployment" }
    ],
    "interview_prep": [
        { "question": "You have a Django app running locally. Walk me through exactly how you would containerize it with Docker and deploy it to AWS EC2.", "topic": "Docker/AWS", "difficulty": "Hard" },
        { "question": "Given that you lack CI/CD experience, how would you design a basic GitHub Actions workflow to run tests and deploy?", "topic": "CI/CD", "difficulty": "Medium" },
        { "question": "Tell me about a time a bug you introduced reached production. How did you detect it, fix it, and prevent it from happening again?", "topic": "Debugging", "difficulty": "Medium" },
        { "question": "Describe a situation where you had to learn a new framework or technology quickly to meet a project deadline.", "topic": "Adaptability", "difficulty": "Easy" }
    ],
    "salary_range": "$90,000 - $120,000",
    "sub_scores": {
        "Technical": 35,
        "Experience": 24,
        "Education": 10,
        "Keywords": 6
    },
    "radar_data": [
        { "subject": "Technical", "A": 70, "B": 100, "fullMark": 100 },
        { "subject": "Experience", "A": 80, "B": 100, "fullMark": 100 },
        { "subject": "Education", "A": 100, "B": 100, "fullMark": 100 },
        { "subject": "Keywords", "A": 65, "B": 100, "fullMark": 100 },
        { "subject": "Soft Skills", "A": 78, "B": 100, "fullMark": 100 },
        { "subject": "Overall", "A": 75, "B": 100, "fullMark": 100 }
    ],
    "suggestions": [
        "Deploy a side project to AWS using EC2 or Lambda + API Gateway; document it on GitHub. This single action closes your biggest critical gap.",
        "Dockerize one of your existing Django projects (Dockerfile + docker-compose.yml) and push it to Docker Hub. Employers test this in screening rounds.",
        "Add a GitHub Actions workflow (.github/workflows/ci.yml) to any public repo with automated testing — this directly addresses the CI/CD gap with a real, verifiable artifact."
    ],
    "summary": "Strong Python/Django backend developer with a solid foundation in databases and API design. Three critical cloud and DevOps gaps (AWS, Docker, CI/CD) are preventing a higher score — but all three are learnable through targeted side projects and are not experience-year issues.",
    "recommended_roles": [
        { "role": "Backend Python Developer", "match": "85%", "reason": "Core Python/Django/PostgreSQL stack is a direct match for mid-tier backend roles" },
        { "role": "API Engineer", "match": "80%", "reason": "REST API design and backend logic experience transfers directly" },
        { "role": "Junior DevOps Engineer", "match": "42%", "reason": "Backend foundation exists but cloud, Docker, and CI/CD skills need significant development first" }
    ]
}

===== END EXAMPLE =====
""",

    "data": """
===== FEW-SHOT EXAMPLE: DATA SCIENCE / ML =====

RESUME TEXT:
"Data analyst with 2 years of experience. Python, Pandas, NumPy, SQL, built dashboards in Tableau. Conducted A/B tests and statistical significance analysis. BSc Statistics."

JOB DESCRIPTION:
"Data Scientist — 2+ years. Must have: Python, scikit-learn, machine learning model building (classification/regression), SQL, statistical analysis. Nice to have: TensorFlow or PyTorch, MLflow, cloud ML (SageMaker or Vertex AI)."

--- PASS 1: INVENTORY ---
Resume HAS:    Python ✓ | Pandas ✓ | NumPy ✓ | SQL ✓ | Tableau ✓ | A/B Testing ✓ | Statistical Analysis ✓ | BSc Statistics ✓
JD REQUIRES:   Python ✓ | scikit-learn ✗ | ML model building ✗ | SQL ✓ | Statistical analysis ✓
JD NICE-TO-HAVE: TensorFlow ✗ | PyTorch ✗ | MLflow ✗ | SageMaker ✗ | Vertex AI ✗

--- PASS 2: GAP ANALYSIS ---
CRITICAL GAPS:
  - scikit-learn — the foundational ML library for this role; completely absent
  - ML model building — no classification or regression model mentioned anywhere
  - Feature engineering — no mention of feature selection, encoding, or pipelines

MODERATE GAPS:
  - Model evaluation (precision/recall/ROC) — statistical analysis present but no ML metrics

MINOR GAPS:
  - TensorFlow/PyTorch — nice-to-have, not blocking
  - MLflow — nice-to-have experiment tracking
  - Cloud ML — nice-to-have

STRENGTHS:
  - Python + Pandas + NumPy: strong data manipulation foundation
  - SQL: solid and required
  - A/B Testing + Stats: transferable to experimental design in ML
  - BSc Statistics: directly relevant educational foundation

--- PASS 3: SCORING RUBRIC ---
Technical (50pts):
  Python + Pandas + NumPy (data layer) = 12/15
  ML libraries (scikit-learn absent entirely) = 2/15
  SQL = 8/10
  Visualization/Tooling = 5/10
  → Technical subtotal: 27/50

Experience (30pts):
  Years: 2 years meets minimum = 14/20
  Role alignment: Analyst ≠ Scientist; scope is narrower = 6/10
  → Experience subtotal: 20/30

Education (10pts):
  BSc Statistics = strong match for data science = 9/10

Context (10pts):
  Data analysis terminology strong; ML modeling vocabulary absent = 5/10

TOTAL: 27 + 20 + 9 + 5 = 61/100

OUTPUT JSON:
{
    "calculation_reasoning": "PASS 1 — Python, Pandas, NumPy, SQL, A/B Testing, BSc Statistics present. scikit-learn, model building, feature engineering entirely absent. PASS 2 — Critical gaps: scikit-learn (no ML library found), ML model building (no classification/regression project mentioned), feature engineering (not referenced). Moderate: no model evaluation metrics (precision/recall). PASS 3 — Technical(27/50): Data manipulation stack is solid (25/40) but ML library block scores near zero (2/10). Experience(20/30): 2 years meets minimum but analyst vs scientist role scope penalized. Education(9/10): BSc Statistics is highly relevant. Context(5/10): Analysis vocabulary strong, modeling vocabulary absent. Total: 61/100.",
    "match_score": 61,
    "main_skills": [
        { "skill": "Python", "status": "matched", "weight": "critical" },
        { "skill": "SQL", "status": "matched", "weight": "critical" },
        { "skill": "Statistical Analysis", "status": "matched", "weight": "critical" },
        { "skill": "Pandas / NumPy", "status": "matched", "weight": "critical" },
        { "skill": "A/B Testing", "status": "matched", "weight": "moderate" },
        { "skill": "Tableau", "status": "matched", "weight": "moderate" }
    ],
    "missing_skills": [
        { "skill": "scikit-learn", "severity": "critical", "reason": "Primary ML library for the role; no evidence of model building" },
        { "skill": "ML Model Building (Classification/Regression)", "severity": "critical", "reason": "Core job function; no model mentioned anywhere in resume" },
        { "skill": "Feature Engineering", "severity": "critical", "reason": "Required for model prep; not referenced at all" },
        { "skill": "Model Evaluation Metrics (Precision/Recall/AUC)", "severity": "moderate", "reason": "Statistical background present but ML-specific metrics absent" },
        { "skill": "TensorFlow or PyTorch", "severity": "minor", "reason": "Nice-to-have deep learning; not blocking for this role" },
        { "skill": "MLflow", "severity": "minor", "reason": "Experiment tracking; not blocking" }
    ],
    "optimized_bullets": [
        { "topic": "SCIKIT-LEARN", "bullet": "Applied statistical analysis and A/B testing using Python and Pandas; extending this foundation to build classification models with scikit-learn (logistic regression, random forests)" },
        { "topic": "FEATURE ENGINEERING", "bullet": "Queried and cleaned large datasets using SQL and Pandas for reporting pipelines; aligned with feature engineering workflows for ML model training datasets" },
        { "topic": "MODEL EVALUATION", "bullet": "Conducted significance testing and data interpretation for business insights; translating these skills into model evaluation using precision, recall, and ROC-AUC metrics" }
    ],
    "interview_prep": [
        { "question": "You have a labeled dataset of customer churn (yes/no). Walk me through the full pipeline — from raw data to a deployed scikit-learn model — including how you'd handle class imbalance.", "topic": "ML Pipeline", "difficulty": "Hard" },
        { "question": "Without scikit-learn experience, how would you mathematically explain how a random forest or logistic regression model works?", "topic": "ML Algorithms", "difficulty": "Hard" },
        { "question": "Describe a time your data analysis directly changed a business decision. What was the question, what did you find, and how did you communicate it?", "topic": "Impact", "difficulty": "Medium" },
        { "question": "Tell me about a time you found an error in your own analysis after you had already presented the results. How did you handle it?", "topic": "Integrity", "difficulty": "Medium" }
    ],
    "salary_range": "$80,000 - $105,000",
    "sub_scores": {
        "Technical": 27,
        "Experience": 20,
        "Education": 9,
        "Keywords": 5
    },
    "radar_data": [
        { "subject": "Technical", "A": 54, "B": 100, "fullMark": 100 },
        { "subject": "Experience", "A": 67, "B": 100, "fullMark": 100 },
        { "subject": "Education", "A": 90, "B": 100, "fullMark": 100 },
        { "subject": "Keywords", "A": 50, "B": 100, "fullMark": 100 },
        { "subject": "Soft Skills", "A": 75, "B": 100, "fullMark": 100 },
        { "subject": "Overall", "A": 61, "B": 100, "fullMark": 100 }
    ],
    "suggestions": [
        "Build and publish a complete ML project on GitHub: load a public dataset (e.g. Titanic or Iris), apply scikit-learn classification, evaluate with precision/recall/confusion matrix, and document everything in a README.",
        "Add 'Machine Learning' as a skill only after completing the above — recruiters verify claims; a live GitHub project is your proof.",
        "Reframe your A/B testing experience using ML vocabulary: 'designed controlled experiments', 'evaluated statistical significance', 'informed predictive model selection' — this bridges analyst → scientist on paper."
    ],
    "summary": "Solid data analyst with strong Python and SQL fundamentals and a highly relevant statistics degree. The gap to a data scientist role is real but bridgeable — the missing piece is hands-on ML model building, which a single focused project can demonstrate.",
    "recommended_roles": [
        { "role": "Data Analyst", "match": "92%", "reason": "Current SQL, Python, stats, and visualization skills are an excellent analyst fit" },
        { "role": "Junior Data Scientist", "match": "64%", "reason": "Statistical foundation is strong; needs one ML project to become competitive" },
        { "role": "BI / Analytics Engineer", "match": "82%", "reason": "Tableau, SQL, and data pipeline experience directly match BI engineering roles" }
    ]
}

===== END EXAMPLE =====
""",

    "design": """
===== FEW-SHOT EXAMPLE: UX / UI DESIGN =====

RESUME TEXT:
"UI Designer with 3 years of experience. Proficient in Figma and Adobe XD. Conducted user interviews and usability tests. Built and maintained a component-based design system. HTML/CSS basics. BDes Visual Communication."

JOB DESCRIPTION:
"UX Designer — 2+ years. Must have: Figma, user research, prototyping, usability testing with documented outcomes, design systems. Nice to have: WCAG accessibility standards, motion design, A/B testing."

--- PASS 1: INVENTORY ---
Resume HAS:    Figma ✓ | Adobe XD ✓ | User Interviews ✓ | Usability Testing ✓ | Design Systems ✓ | HTML/CSS ✓ | BDes ✓
JD REQUIRES:   Figma ✓ | User Research ✓ | Prototyping (implied in Figma use — partial ✓) | Usability Testing ✓ | Documented Outcomes (not stated ✗) | Design Systems ✓
JD NICE-TO-HAVE: WCAG ✗ | Motion Design ✗ | A/B Testing ✗

--- PASS 2: GAP ANALYSIS ---
CRITICAL GAPS:
  - Documented usability testing outcomes — testing mentioned but results/reports/artifacts not referenced

MODERATE GAPS:
  - Prototyping (interactive) — Figma implies this but it's not called out explicitly
  - WCAG accessibility — nice-to-have but increasingly expected in senior roles

MINOR GAPS:
  - Motion design — nice-to-have, niche
  - A/B testing — nice-to-have

STRENGTHS:
  - Figma, Adobe XD, user research, usability testing, design systems all present
  - Experience exceeds minimum requirement
  - BDes directly matches field

--- PASS 3: SCORING RUBRIC ---
Technical (50pts):
  Design tools (Figma, Adobe XD) = 14/15
  User research and testing = 12/15
  Design systems = 10/10
  Prototyping (not explicit) = 7/10
  → Technical subtotal: 43/50

Experience (30pts):
  3 years exceeds 2-year requirement = 20/20
  Role alignment: UI → UX, slight breadth question = 8/10
  → Experience subtotal: 28/30

Education (10pts):
  BDes Visual Communication = direct field match = 10/10

Context (10pts):
  Strong UX/design terminology throughout = 9/10

TOTAL: 43 + 28 + 10 + 9 = 90/100

OUTPUT JSON:
{
    "calculation_reasoning": "PASS 1 — Figma, Adobe XD, user interviews, usability testing, design systems, HTML/CSS, BDes all confirmed. Documented outcomes from testing not explicitly stated. Prototyping not called out independently. PASS 2 — Critical: documented usability outcomes missing (recruiter will look for this). Moderate: prototyping not explicitly named; WCAG increasingly expected. PASS 3 — Technical(43/50): all major tools present, small deduction for non-explicit prototyping and absent accessibility. Experience(28/30): 3 years exceeds requirement, minor deduction for UI→UX transition framing. Education(10/10): BDes is a direct match. Context(9/10): UX terminology is precise and appropriate. Total: 90/100.",
    "match_score": 90,
    "main_skills": [
        { "skill": "Figma", "status": "matched", "weight": "critical" },
        { "skill": "User Research / Interviews", "status": "matched", "weight": "critical" },
        { "skill": "Usability Testing", "status": "matched", "weight": "critical" },
        { "skill": "Design Systems", "status": "matched", "weight": "critical" },
        { "skill": "Adobe XD", "status": "matched", "weight": "moderate" },
        { "skill": "HTML / CSS", "status": "matched", "weight": "moderate" }
    ],
    "missing_skills": [
        { "skill": "Documented Usability Testing Outcomes", "severity": "critical", "reason": "Testing is mentioned but results, reports, or artifacts not referenced — recruiters expect evidence" },
        { "skill": "WCAG Accessibility Standards", "severity": "moderate", "reason": "Nice-to-have but increasingly required in design systems work; not mentioned" },
        { "skill": "Interactive Prototyping (explicit)", "severity": "moderate", "reason": "Figma implies this but it is not stated — add explicitly to avoid filtering" },
        { "skill": "Motion / Micro-Interaction Design", "severity": "minor", "reason": "Nice-to-have for senior UX roles" },
        { "skill": "A/B Testing", "severity": "minor", "reason": "Nice-to-have for data-informed design; not present" }
    ],
    "optimized_bullets": [
        { "topic": "USABILITY TESTING", "bullet": "Conducted usability testing sessions with 5-8 participants per round; synthesized findings into prioritized issue reports with design recommendations, reducing task error rates by 30%" },
        { "topic": "ACCESSIBILITY", "bullet": "Built and maintained a Figma component library and design system with WCAG 2.1 AA accessibility compliance across all interactive states" },
        { "topic": "PROTOTYPING", "bullet": "Created high-fidelity interactive prototypes in Figma for user testing and stakeholder review, iterating based on validated usability findings" }
    ],
    "interview_prep": [
        { "question": "Walk me through a usability test you ran end-to-end — how did you recruit participants, what was your test script, and how did you document and prioritize your findings?", "topic": "Testing", "difficulty": "Hard" },
        { "question": "How do you ensure your components meet WCAG 2.1 AA accessibility standards during the design phase?", "topic": "Accessibility", "difficulty": "Medium" },
        { "question": "Tell me about a time user research directly contradicted your design instincts. What did you do, and what was the outcome?", "topic": "Conflict", "difficulty": "Medium" },
        { "question": "Can you give an example of a time when you had to convince stakeholders to invest in UX improvements?", "topic": "Communication", "difficulty": "Easy" }
    ],
    "salary_range": "$85,000 - $115,000",
    "sub_scores": {
        "Technical": 43,
        "Experience": 28,
        "Education": 10,
        "Keywords": 9
    },
    "radar_data": [
        { "subject": "Technical", "A": 86, "B": 100, "fullMark": 100 },
        { "subject": "Experience", "A": 93, "B": 100, "fullMark": 100 },
        { "subject": "Education", "A": 100, "B": 100, "fullMark": 100 },
        { "subject": "Keywords", "A": 88, "B": 100, "fullMark": 100 },
        { "subject": "Soft Skills", "A": 90, "B": 100, "fullMark": 100 },
        { "subject": "Overall", "A": 90, "B": 100, "fullMark": 100 }
    ],
    "suggestions": [
        "Add a portfolio case study that explicitly documents your usability testing process: recruitment criteria, test script structure, findings summary, and what changed in the design as a result.",
        "Add 'WCAG 2.1 AA' to your design system work if you applied any accessibility rules — this single keyword catches many ATS filters in modern UX roles.",
        "Replace 'usability tests' with 'moderated usability testing sessions with synthesized findings' in your resume — the specificity shows process maturity, not just tool familiarity."
    ],
    "summary": "Highly qualified UX/UI designer whose skills closely match this role. A strong candidate who would likely advance past ATS screening; the only meaningful gap is explicitly documenting usability testing outcomes, which a portfolio case study update can resolve immediately.",
    "recommended_roles": [
        { "role": "UX Designer", "match": "92%", "reason": "Research, testing, and design systems experience aligns precisely with UX scope" },
        { "role": "Product Designer", "match": "87%", "reason": "Design system and prototyping skills match product design expectations" },
        { "role": "UI Designer", "match": "96%", "reason": "Visual tooling, component systems, and HTML/CSS are an excellent UI match" }
    ]
}

===== END EXAMPLE =====
""",

    "default": """
===== FEW-SHOT EXAMPLE: GENERAL PROFESSIONAL =====

RESUME TEXT:
"Project Manager with 4 years of experience leading cross-functional teams of 10+ people. PMP certified. Used JIRA for sprint tracking, managed delivery timelines, Agile/Scrum methodology. BSc Business Administration."

JOB DESCRIPTION:
"Senior Project Manager — 5+ years required. Must have: PMP certification, Agile/Scrum, stakeholder management, budget ownership, risk management. Tools: JIRA, MS Project. Nice to have: PRINCE2, resource planning."

--- PASS 1: INVENTORY ---
Resume HAS:    PMP ✓ | JIRA ✓ | Agile/Scrum ✓ | Cross-functional teams ✓ | BSc Business Administration ✓ | Delivery timelines ✓
JD REQUIRES:   PMP ✓ | Agile/Scrum ✓ | Stakeholder Management ✗ (not stated) | Budget Ownership ✗ | Risk Management ✗ | 5+ years ✗ (has 4)
JD NICE-TO-HAVE: PRINCE2 ✗ | Resource Planning ✗ | MS Project ✗

--- PASS 2: GAP ANALYSIS ---
CRITICAL GAPS:
  - Budget ownership — no financial accountability mentioned; key senior PM differentiator
  - Stakeholder management — cross-functional teams present but stakeholder reporting not stated
  - Risk management — risk register, mitigation plans not mentioned
  - Experience: 4 years vs 5+ required = 1-year shortfall

MODERATE GAPS:
  - MS Project — listed as required tool alongside JIRA; only JIRA found
  - Resource planning — not mentioned in context of team allocation or capacity

MINOR GAPS:
  - PRINCE2 — nice-to-have framework
  - Advanced reporting (executive dashboards) — implied but not stated

STRENGTHS:
  - PMP certified: strong differentiator
  - JIRA + Agile/Scrum: direct match
  - Cross-functional team leadership: relevant evidence
  - BSc Business Administration: appropriate background

--- PASS 3: SCORING RUBRIC ---
Technical (50pts):
  Certifications (PMP) = 13/15
  Methodology (Agile/Scrum) = 10/10
  Tools (JIRA ✓, MS Project ✗) = 8/15
  Process (budget, risk, stakeholder absent) = 4/10
  → Technical subtotal: 35/50

Experience (30pts):
  Years: 4 vs 5+ = 1-year gap = 13/20
  Scope: cross-functional leadership = 9/10
  → Experience subtotal: 22/30

Education (10pts):
  BSc Business Administration = relevant match = 9/10

Context (10pts):
  PM terminology mostly correct; financial/risk vocabulary missing = 7/10

TOTAL: 35 + 22 + 9 + 7 = 73/100

OUTPUT JSON:
{
    "calculation_reasoning": "PASS 1 — PMP, JIRA, Agile/Scrum, cross-functional team leadership, BSc Business confirmed. Budget ownership, stakeholder management, risk management absent. 4 years vs 5+ required. PASS 2 — Critical gaps: budget ownership (no financial figure or P&L mentioned), stakeholder management (not stated explicitly), risk management (no risk register or mitigation referenced), 1-year experience shortfall. Moderate: MS Project absent, resource planning not mentioned. PASS 3 — Technical(35/50): PMP and Agile strong; process and tooling gaps moderate. Experience(22/30): experience gap and scope gap penalized. Education(9/10): relevant degree. Context(7/10): core PM language correct, financial and risk vocabulary missing. Total: 73/100.",
    "match_score": 73,
    "main_skills": [
        { "skill": "PMP Certification", "status": "matched", "weight": "critical" },
        { "skill": "Agile / Scrum", "status": "matched", "weight": "critical" },
        { "skill": "JIRA", "status": "matched", "weight": "critical" },
        { "skill": "Cross-Functional Team Leadership", "status": "matched", "weight": "critical" },
        { "skill": "Delivery Timeline Management", "status": "matched", "weight": "moderate" }
    ],
    "missing_skills": [
        { "skill": "Budget Ownership", "severity": "critical", "reason": "No financial accountability or budget figure mentioned; key senior PM requirement" },
        { "skill": "Stakeholder Management", "severity": "critical", "reason": "Cross-functional teamwork present but stakeholder reporting/alignment not stated" },
        { "skill": "Risk Management", "severity": "critical", "reason": "Risk register, issue log, or mitigation planning not mentioned" },
        { "skill": "MS Project", "severity": "moderate", "reason": "Listed as required tool in JD; only JIRA found in resume" },
        { "skill": "Resource Planning", "severity": "moderate", "reason": "Capacity and resource allocation not mentioned despite team leadership" },
        { "skill": "PRINCE2", "severity": "minor", "reason": "Nice-to-have framework; not blocking" }
    ],
    "optimized_bullets": [
        { "topic": "BUDGETING", "bullet": "Owned end-to-end delivery of cross-functional projects with budget accountability up to $X, managing stakeholder expectations through weekly executive status reports" },
        { "topic": "RISK MANAGEMENT", "bullet": "Maintained a live risk register and issue log across concurrent sprints in JIRA, escalating critical path risks with documented mitigation plans" },
        { "topic": "RESOURCE PLANNING", "bullet": "Led resource planning and capacity allocation for teams of 10+, coordinating with department heads to resolve resourcing conflicts across parallel workstreams" }
    ],
    "interview_prep": [
        { "question": "You are managing a $500k project that is 3 weeks behind schedule. Budget is fixed. Walk me through how you communicate this to stakeholders and what options you present.", "topic": "Communication", "difficulty": "Hard" },
        { "question": "How do you manage a risk register, and can you describe a time when you used one to prevent a project delay?", "topic": "Risk", "difficulty": "Medium" },
        { "question": "Tell me about a significant project risk you identified early. How did you escalate it, what was your mitigation plan, and what was the outcome?", "topic": "Mitigation", "difficulty": "Medium" },
        { "question": "Describe a situation where you had to manage conflict between two key stakeholders with opposing priorities.", "topic": "Conflict", "difficulty": "Easy" }
    ],
    "salary_range": "$90,000 - $120,000",
    "sub_scores": {
        "Technical": 35,
        "Experience": 22,
        "Education": 9,
        "Keywords": 7
    },
    "radar_data": [
        { "subject": "Technical", "A": 70, "B": 100, "fullMark": 100 },
        { "subject": "Experience", "A": 73, "B": 100, "fullMark": 100 },
        { "subject": "Education", "A": 90, "B": 100, "fullMark": 100 },
        { "subject": "Keywords", "A": 72, "B": 100, "fullMark": 100 },
        { "subject": "Soft Skills", "A": 82, "B": 100, "fullMark": 100 },
        { "subject": "Overall", "A": 73, "B": 100, "fullMark": 100 }
    ],
    "suggestions": [
        "Add a concrete budget figure to at least one resume bullet (e.g. 'managed project budget of $350k') — this is the single most important missing keyword for senior PM screening.",
        "Include a bullet that explicitly mentions stakeholder reporting format: 'delivered weekly executive dashboards to C-suite stakeholders tracking RAG status, milestones, and risks'.",
        "Add 'risk register', 'issue log', and 'mitigation planning' to your JIRA experience bullet — these terms catch ATS filters for senior PM roles and are demonstrably true given your delivery work."
    ],
    "summary": "Experienced and certified project manager with strong Agile and team leadership credentials. Three critical vocabulary and evidence gaps (budget, stakeholder, risk) are suppressing an otherwise competitive profile — all three can be addressed with targeted resume rewrites without overstating experience.",
    "recommended_roles": [
        { "role": "Project Manager", "match": "85%", "reason": "PMP, Agile, JIRA, and team leadership directly match mid-senior PM requirements" },
        { "role": "Scrum Master", "match": "80%", "reason": "Agile/Scrum methodology and sprint tracking experience are directly applicable" },
        { "role": "Program Manager", "match": "65%", "reason": "Cross-functional leadership present; needs demonstrated budget and stakeholder management at scale" }
    ]
}

===== END EXAMPLE =====
"""
}


# ==============================================================================
# ROLE DETECTOR
# ==============================================================================

def pick_few_shot_example(job_description: str) -> tuple[str, str]:
    jd_lower = job_description.lower()

    software_keywords = [
        "python", "java", "javascript", "typescript", "backend", "frontend",
        "fullstack", "full-stack", "software engineer", "developer", "api",
        "django", "fastapi", "flask", "react", "node", "devops", "cloud",
        "aws", "docker", "kubernetes", "microservices", "rest", "graphql"
    ]
    data_keywords = [
        "data scientist", "machine learning", "ml engineer", "deep learning",
        "tensorflow", "pytorch", "scikit", "nlp", "data analyst", "analytics",
        "pandas", "numpy", "big data", "spark", "hadoop", "ai engineer",
        "llm", "computer vision", "feature engineering"
    ]
    design_keywords = [
        "ux", "ui", "user experience", "user interface", "figma", "sketch",
        "adobe xd", "product designer", "interaction design", "usability",
        "wireframe", "prototype", "design system", "visual design", "hci"
    ]

    if any(kw in jd_lower for kw in software_keywords):
        return FEW_SHOT_EXAMPLES["software"], "Software Engineering"
    elif any(kw in jd_lower for kw in data_keywords):
        return FEW_SHOT_EXAMPLES["data"], "Data Science / ML"
    elif any(kw in jd_lower for kw in design_keywords):
        return FEW_SHOT_EXAMPLES["design"], "UX / UI Design"
    else:
        return FEW_SHOT_EXAMPLES["default"], "General Professional"


# ==============================================================================
# PDF EXTRACTOR
# ==============================================================================

def extract_text_from_pdf(file_content: bytes) -> str:
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
    text = ""
    for page in pdf_reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted
    return text


# ==============================================================================
# CORE AI ANALYSIS — Three-Pass Few-Shot + Strict JSON Schema
# ==============================================================================

async def get_ai_analysis(resume_text: str, job_description: str) -> dict:
    if not groq_client:
        return {
            "match_score": 0,
            "missing_skills": [],
            "main_skills": [],
            "suggestions": [],
            "summary": "No API Key configured."
        }

    few_shot_example, role_label = pick_few_shot_example(job_description)

    # --------------------------------------------------------------------------
    # SYSTEM PROMPT: Sets the persona, methodology, and absolute output rules
    # --------------------------------------------------------------------------
    system_prompt = f"""You are a senior technical recruiter and ATS specialist with 15 years of experience screening resumes for engineering, data, design, and business roles.

YOUR OUTPUT RULE: Return ONLY a valid JSON object. No prose. No preamble. No explanation outside the JSON. No markdown code blocks. Just the raw JSON object.

YOUR METHODOLOGY — Three-Pass Reasoning:
You MUST reason in exactly three passes before producing the score:

PASS 1 — INVENTORY
  Extract and list every hard skill, soft skill (e.g. Leadership, Communication), tool, certification, degree, and year of experience from the resume.
  Extract every required AND nice-to-have hard/soft skill, tool, and qualification from the job description.
  Mark each item: present ✓ or absent ✗.

PASS 2 — GAP ANALYSIS
  Classify every absent JD requirement as:
    - CRITICAL: required, completely absent, no transferable equivalent
    - MODERATE: required but partially covered, or nice-to-have but important
    - MINOR: nice-to-have, unlikely to block hiring
  CRITICAL EXPERIENCE RULE: If the JD asks for a specific Years of Experience (e.g., "5 years") and the resume has significantly less (e.g., "6 months"), you MUST flag this as a CRITICAL gap in missing_skills.
  NEVER mark a skill as missing if a strong equivalent exists in the resume.

PASS 3 — SCORE CALCULATION (strictly follow this rubric):
  Technical Skills  → 50 points max
    Critical gaps each cost 5-10 pts depending on weight in JD
    Moderate gaps cost 2-4 pts
    Minor gaps cost 0-1 pts
  Experience Match  → 30 points max
    Years match/exceed: 20/20 | 1 year short: 13/20 | 2+ years short: 8/20
    Role alignment: direct = 10/10 | adjacent = 6/10 | distant = 2/10
  Education         → 10 points max
    Direct match: 10 | Related field: 8 | Unrelated: 4 | None stated: 3
  Context/Terminology → 10 points max
    Strong domain vocabulary use: 8-10 | Weak/absent: 3-5

Score = sum of four categories. DO NOT round up to make the candidate look better. Be honest.

---

Study this complete worked example for the detected role type. Follow the IDENTICAL structure in your output:

{few_shot_example}

---

KEY OUTPUT RULES:
1. "main_skills": List ONLY skills (BOTH technical and soft skills like Leadership/Communication) that ARE present in the resume AND required/relevant to the JD. Each must have: skill name (CRITICAL: EXTRACT 1-3 WORDS ONLY. DO NOT COPY PHRASES. Example: "Django" not "Django or similar"), status ("matched"), and weight ("critical" | "moderate" | "nice-to-have").
2. "missing_skills": List ONLY skills (BOTH technical and soft skills) or experience requirements absent from the resume that appear in the JD. Each must have: skill name (CRITICAL: EXTRACT 1-3 WORDS ONLY. Example: "CI/CD" or "5 Years Experience"), severity ("critical" | "moderate" | "minor"), and a one-sentence reason explaining WHY it matters for this specific role.
3. "optimized_bullets": 3 resume bullets formatted as objects with a "topic" (e.g. "LEADERSHIP") and the "bullet" text itself.
4. "interview_prep": 4 structured questions formatted as objects with a "question", "topic", and "difficulty" (Easy/Medium/Hard).
5. "suggestions": 3 concrete, specific action items. Each must tell the candidate EXACTLY what to build, write, or do — not generic advice.
6. "match_score": An integer 0-100 computed strictly from the Pass 3 rubric. Not a feeling.
7. "sub_scores": A dictionary with the exact points scored in Technical, Experience, Education, and Keywords.
8. "radar_data": Each "A" value must match the sub-score from Pass 3 (scaled to 100). They must NOT all be close to each other.
"""

    # --------------------------------------------------------------------------
    # USER PROMPT: Delivers the actual resume + JD and requests structured output
    # --------------------------------------------------------------------------
    user_prompt = f"""Analyze this resume against this job description using the three-pass methodology.

=== RESUME ===
{resume_text[:3500]}

=== JOB DESCRIPTION ===
{job_description[:3000]}

=== REQUIRED OUTPUT STRUCTURE ===
Return a JSON object with EXACTLY these fields (no additions, no omissions):

{{
    "calculation_reasoning": "PASS 1: [list what resume HAS and what JD requires, marked ✓/✗]. PASS 2: [classify each gap as CRITICAL/MODERATE/MINOR with one-line reason]. PASS 3: [show exact point math per category: Technical X/50, Experience X/30, Education X/10, Context X/10, Total X/100]",

    "match_score": <integer 0-100, computed from rubric>,

    "main_skills": [
        {{ "skill": "Skill Name", "status": "matched", "weight": "critical|moderate|nice-to-have" }}
    ],

    "missing_skills": [
        {{ "skill": "Skill Name", "severity": "critical|moderate|minor", "reason": "One sentence: why this gap matters for THIS role" }}
    ],

    "optimized_bullets": [
        {{ "topic": "TOPIC NAME", "bullet": "Bullet 1 — real experience reframed..." }}
    ],

    "interview_prep": [
        {{ "question": "Question text...", "topic": "Skill topic", "difficulty": "Hard" }}
    ],

    "salary_range": "$XX,000 - $XX,000",
    
    "sub_scores": {{
        "Technical": <points out of 50>,
        "Experience": <points out of 30>,
        "Education": <points out of 10>,
        "Keywords": <points out of 10>
    }},

    "radar_data": [
        {{ "subject": "Technical", "A": <0-100 from rubric>, "B": 100, "fullMark": 100 }},
        {{ "subject": "Experience", "A": <0-100 from rubric>, "B": 100, "fullMark": 100 }},
        {{ "subject": "Education", "A": <0-100 from rubric>, "B": 100, "fullMark": 100 }},
        {{ "subject": "Keywords", "A": <0-100>, "B": 100, "fullMark": 100 }},
        {{ "subject": "Soft Skills", "A": <0-100>, "B": 100, "fullMark": 100 }},
        {{ "subject": "Overall", "A": <match_score>, "B": 100, "fullMark": 100 }}
    ],

    "suggestions": [
        "Suggestion 1: exact action — what to build, what to write, what to add, where to put it",
        "Suggestion 2: same specificity",
        "Suggestion 3: same specificity"
    ],

    "summary": "2 sentences. First: honest assessment of match quality. Second: the single most impactful thing the candidate can do right now.",

    "recommended_roles": [
        {{ "role": "Job Title", "match": "XX%", "reason": "Specific reason based on their actual skills" }},
        {{ "role": "Job Title", "match": "XX%", "reason": "Specific reason" }},
        {{ "role": "Job Title", "match": "XX%", "reason": "Specific reason" }}
    ]
}}
"""

    try:
        chat_completion = await groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0,
            seed=42,
            top_p=0.1,
            max_tokens=2500,
            response_format={"type": "json_object"}
        )
        raw_content = chat_completion.choices[0].message.content
        print("RAW LLM OUTPUT:\n", raw_content)
        result = json.loads(raw_content)

        # Normalize any dicts that should be lists
        list_fields = [
            "main_skills", "missing_skills", "optimized_bullets", 
            "interview_prep", "radar_data", "suggestions", "recommended_roles"
        ]
        for field in list_fields:
            if isinstance(result.get(field), dict):
                result[field] = list(result[field].values())

        # Ensure all required fields exist to prevent frontend crashes or missing sections
        default_result = {
            "calculation_reasoning": "Reasoning missing.",
            "match_score": 0,
            "main_skills": [],
            "missing_skills": [],
            "optimized_bullets": [],
            "interview_prep": [],
            "salary_range": "Not provided",
            "radar_data": [],
            "suggestions": [],
            "summary": "Analysis completed, but some fields are missing.",
            "recommended_roles": []
        }
        for key, default_val in default_result.items():
            if key not in result or result[key] is None:
                result[key] = default_val

        return result

    except Exception as e:
        print(f"Groq Error: {e}")
        error_msg = str(e)
        if "429" in error_msg or "rate limit" in error_msg.lower():
            raise HTTPException(status_code=429, detail="Your daily AI tokens have been completed. Please try again later.")
        elif "decommissioned" in error_msg.lower():
            raise HTTPException(status_code=400, detail="The AI model is decommissioned. Please update the model in main.py.")
        else:
            raise HTTPException(status_code=500, detail="Analysis failed. Please try again.")


# ==============================================================================
# API ENDPOINT
# ==============================================================================

# Global cache to prevent AI fluctuations on identical inputs
analysis_cache = {}

@app.post("/match")
async def match_resume(
    resume_file: UploadFile = File(None),
    resume_text: str = Form(None),
    job_file: UploadFile = File(None),
    job_description: str = Form(None)
):
    if not resume_file and not resume_text:
        raise HTTPException(
            status_code=400,
            detail="Either a resume file (PDF/TXT) or resume text must be provided."
        )
    if not job_file and not job_description:
        raise HTTPException(
            status_code=400,
            detail="Either a job description file (PDF/TXT) or job description text must be provided."
        )

    # Extract Resume Text
    if resume_file:
        content = await resume_file.read()
        if resume_file.filename.endswith('.pdf'):
            extracted_resume_text = await asyncio.to_thread(extract_text_from_pdf, content)
        elif resume_file.filename.endswith('.txt'):
            extracted_resume_text = content.decode('utf-8')
        else:
            raise HTTPException(status_code=400, detail="Only PDF and TXT formats are supported.")
    else:
        extracted_resume_text = resume_text

    # Extract Job Description Text
    if job_file:
        content = await job_file.read()
        if job_file.filename.endswith('.pdf'):
            extracted_job_text = await asyncio.to_thread(extract_text_from_pdf, content)
        elif job_file.filename.endswith('.txt'):
            extracted_job_text = content.decode('utf-8')
        else:
            raise HTTPException(status_code=400, detail="Only PDF and TXT formats are supported.")
    else:
        extracted_job_text = job_description

    if not extracted_resume_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from resume.")
    if not extracted_job_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from job description.")

    # Create a unique hash for the current input combination
    input_text = extracted_resume_text.strip() + "|||" + extracted_job_text.strip()
    input_hash = hashlib.md5(input_text.encode('utf-8')).hexdigest()

    # Check cache to guarantee deterministic results for the exact same inputs
    if input_hash in analysis_cache:
        analysis = analysis_cache[input_hash]
    else:
        analysis = await get_ai_analysis(extracted_resume_text.strip(), extracted_job_text.strip())
        analysis_cache[input_hash] = analysis

    _, role_label = pick_few_shot_example(extracted_job_text)
    analysis["filename"] = resume_file.filename if resume_file else "Manual Input"
    analysis["detected_role_category"] = role_label

    return analysis


# ==============================================================================
# ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)