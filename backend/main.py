import os
import json
import io
import asyncio
import PyPDF2
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from groq import AsyncGroq

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

# Groq AI Setup
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("WARNING: GROQ_API_KEY not found in environment variables.")
    groq_client = None
else:
    groq_client = AsyncGroq(api_key=GROQ_API_KEY)

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================================================================
# FEW-SHOT EXAMPLES — One per role domain
# Each example shows the model exactly what reasoning + output looks like
# ==============================================================================

FEW_SHOT_EXAMPLES = {

    "software": """
EXAMPLE (Software Engineering Role):
Resume: "Python developer, 3 years Django, built REST APIs, PostgreSQL, B.Sc Computer Science, collaborated on Agile teams"
JD: "Looking for Python backend dev with Django, PostgreSQL, AWS, Docker experience. 3+ years required."

Step-by-step reasoning:
- Technical (50pts): Python ✓, Django ✓, PostgreSQL ✓, REST APIs ✓ — missing AWS and Docker → 38/50
- Experience (30pts): 3 years matches requirement, Agile teamwork is a plus → 26/30
- Education (10pts): B.Sc CS is a direct match → 10/10
- Context (10pts): Backend terminology strong, cloud terminology weak → 7/10
- Total: 81/100

Output:
{
    "calculation_reasoning": "Technical(38/50): Python, Django, PostgreSQL, REST APIs matched. AWS and Docker missing. Experience(26/30): 3 years aligns with requirement, Agile background is a plus. Education(10/10): B.Sc Computer Science is a direct match. Context(7/10): Strong backend terminology, weak cloud/infra terminology.",
    "match_score": 81,
    "missing_skills": ["AWS", "Docker", "CI/CD", "Redis", "Kubernetes"],
    "optimized_bullets": [
        "Deployed Django REST APIs to cloud-ready infrastructure, prepared for AWS EC2 and Lambda migration",
        "Managed PostgreSQL databases with query optimization, aligned with production-scale cloud deployments",
        "Worked in Agile sprints using Git, ready to integrate Docker containerization and CI/CD pipelines"
    ],
    "interview_prep": [
        "Technical: How would you containerize a Django app using Docker and deploy it to AWS?",
        "Behavioral: Tell me about a time you had to debug a critical issue in a production backend system."
    ],
    "salary_range": "$90k - $120k",
    "radar_data": [
        {"subject": "Technical", "A": 76, "B": 100, "fullMark": 100},
        {"subject": "Experience", "A": 87, "B": 100, "fullMark": 100},
        {"subject": "Education", "A": 100, "B": 100, "fullMark": 100},
        {"subject": "Keywords", "A": 70, "B": 100, "fullMark": 100},
        {"subject": "Soft Skills", "A": 80, "B": 100, "fullMark": 100},
        {"subject": "Overall", "A": 81, "B": 100, "fullMark": 100}
    ],
    "suggestions": [
        "Add an AWS or Docker personal project to GitHub to close the biggest skill gap",
        "Mention any CI/CD tools (GitHub Actions, Jenkins) you have used even informally",
        "Include cloud-related keywords like 'scalable', 'containerized', 'deployed' in your resume bullets"
    ],
    "summary": "Strong Python/Django backend developer with solid database and API skills. Closing the AWS and Docker gaps — even through personal projects — would make this candidate highly competitive for this role.",
    "recommended_roles": [
        {"role": "Backend Developer", "match": "85%", "reason": "Core Python/Django/PostgreSQL stack aligns directly"},
        {"role": "API Engineer", "match": "80%", "reason": "REST API experience is directly transferable"},
        {"role": "Junior DevOps Engineer", "match": "55%", "reason": "Backend foundation is solid but cloud/infra skills need development"}
    ]
}
END EXAMPLE
""",

    "data": """
EXAMPLE (Data Science / ML Role):
Resume: "Data analyst, 2 years, Python, Pandas, NumPy, built dashboards in Tableau, basic SQL, BSc Statistics"
JD: "Data Scientist needed with Python, machine learning (scikit-learn, TensorFlow), SQL, 2+ years experience"

Step-by-step reasoning:
- Technical (50pts): Python ✓, Pandas ✓, SQL ✓ — missing scikit-learn, TensorFlow, ML knowledge → 28/50
- Experience (30pts): 2 years matches minimum but role is analyst not scientist → 18/30
- Education (10pts): BSc Statistics is relevant but not CS/ML → 8/10
- Context (10pts): Data terminology present, ML/model terminology absent → 5/10
- Total: 59/100

Output:
{
    "calculation_reasoning": "Technical(28/50): Python, Pandas, SQL matched. Critical ML libraries (scikit-learn, TensorFlow) missing entirely. Experience(18/30): 2 years matches minimum but analyst role differs from scientist responsibilities. Education(8/10): BSc Statistics is relevant but lacks ML/CS depth. Context(5/10): Data analysis terminology strong, machine learning and modeling terminology absent.",
    "match_score": 59,
    "missing_skills": ["scikit-learn", "TensorFlow", "Machine Learning", "Feature Engineering", "Model Deployment"],
    "optimized_bullets": [
        "Applied statistical analysis using Python and Pandas, foundational to building supervised ML models with scikit-learn",
        "Built data pipelines and dashboards, experience transferable to ML feature engineering workflows",
        "Queried large datasets using SQL to derive insights, ready to extend into model training data preparation"
    ],
    "interview_prep": [
        "Technical: How would you approach building a binary classification model using scikit-learn from scratch?",
        "Behavioral: Describe a time your data analysis led to a significant business decision."
    ],
    "salary_range": "$75k - $100k",
    "radar_data": [
        {"subject": "Technical", "A": 56, "B": 100, "fullMark": 100},
        {"subject": "Experience", "A": 60, "B": 100, "fullMark": 100},
        {"subject": "Education", "A": 80, "B": 100, "fullMark": 100},
        {"subject": "Keywords", "A": 50, "B": 100, "fullMark": 100},
        {"subject": "Soft Skills", "A": 75, "B": 100, "fullMark": 100},
        {"subject": "Overall", "A": 59, "B": 100, "fullMark": 100}
    ],
    "suggestions": [
        "Complete a scikit-learn ML project (classification or regression) and publish it on GitHub",
        "Take a free TensorFlow or ML course (Coursera, fast.ai) and list it under certifications",
        "Reframe your analyst experience using ML vocabulary: 'predictive insights', 'model-driven analysis'"
    ],
    "summary": "Solid data analyst with strong Python and SQL fundamentals. The gap to a data scientist role is bridgeable, but requires hands-on ML project experience before this application would be competitive.",
    "recommended_roles": [
        {"role": "Data Analyst", "match": "90%", "reason": "Current skills are a strong match for analyst roles"},
        {"role": "Junior Data Scientist", "match": "62%", "reason": "Statistical foundation is there; needs ML library experience"},
        {"role": "Business Intelligence Developer", "match": "80%", "reason": "Tableau and SQL skills align well with BI roles"}
    ]
}
END EXAMPLE
""",

    "design": """
EXAMPLE (UX/UI Design Role):
Resume: "UI designer, 3 years, Figma, Adobe XD, user research, built design systems, HTML/CSS basics, BDes Visual Communication"
JD: "UX Designer needed with Figma, user research, prototyping, usability testing, experience with design systems. 2+ years."

Step-by-step reasoning:
- Technical (50pts): Figma ✓, Adobe XD ✓, user research ✓, design systems ✓, prototyping ✓ — missing usability testing documentation → 44/50
- Experience (30pts): 3 years exceeds requirement, strong design background → 28/30
- Education (10pts): BDes Visual Communication is a strong match → 10/10
- Context (10pts): Design terminology strong and aligned → 9/10
- Total: 91/100

Output:
{
    "calculation_reasoning": "Technical(44/50): Figma, Adobe XD, user research, design systems, and prototyping all matched. Formal usability testing documentation not explicitly mentioned. Experience(28/30): 3 years exceeds the 2-year requirement with directly relevant design work. Education(10/10): BDes Visual Communication is a direct and strong match. Context(9/10): Design and UX terminology is consistently and correctly used throughout.",
    "match_score": 91,
    "missing_skills": ["Usability Testing Documentation", "Accessibility (WCAG)", "Motion Design", "User Journey Mapping", "A/B Testing"],
    "optimized_bullets": [
        "Conducted user research and synthesized findings into actionable design decisions, including formal usability testing sessions",
        "Built and maintained scalable design systems in Figma, ensuring accessibility compliance across components",
        "Prototyped and iterated on user flows using Figma, validating designs through A/B testing and user feedback"
    ],
    "interview_prep": [
        "Technical: Walk me through how you would conduct a usability test for a new onboarding flow.",
        "Behavioral: Tell me about a time user research changed the direction of a design you were confident in."
    ],
    "salary_range": "$80k - $115k",
    "radar_data": [
        {"subject": "Technical", "A": 88, "B": 100, "fullMark": 100},
        {"subject": "Experience", "A": 93, "B": 100, "fullMark": 100},
        {"subject": "Education", "A": 100, "B": 100, "fullMark": 100},
        {"subject": "Keywords", "A": 90, "B": 100, "fullMark": 100},
        {"subject": "Soft Skills", "A": 88, "B": 100, "fullMark": 100},
        {"subject": "Overall", "A": 91, "B": 100, "fullMark": 100}
    ],
    "suggestions": [
        "Add a case study explicitly documenting a usability testing process with findings and outcomes",
        "Mention WCAG accessibility standards if you have applied them in your design system work",
        "Include any A/B testing or data-driven design decisions in your portfolio write-ups"
    ],
    "summary": "Highly qualified UX/UI designer whose skills closely match this role. A strong candidate who would likely advance through screening; adding explicit usability testing documentation would make this application near-perfect.",
    "recommended_roles": [
        {"role": "UX Designer", "match": "93%", "reason": "All core UX skills including research and systems are present"},
        {"role": "Product Designer", "match": "88%", "reason": "Design system and prototyping experience aligns with product design"},
        {"role": "UI Designer", "match": "95%", "reason": "Visual and tooling skills are an excellent match"}
    ]
}
END EXAMPLE
""",

    "default": """
EXAMPLE (General Professional Role):
Resume: "Project manager, 4 years, led cross-functional teams of 10+, PMP certified, MS Office, JIRA, Agile/Scrum, BSc Business Administration"
JD: "Senior Project Manager needed with 5+ years experience, PMP certification, Agile methodology, stakeholder management, budget control experience."

Step-by-step reasoning:
- Technical (50pts): PMP ✓, JIRA ✓, Agile/Scrum ✓, MS Office ✓ — missing explicit budget control experience → 38/50
- Experience (30pts): 4 years vs 5+ required, team leadership present → 22/30
- Education (10pts): BSc Business Administration is relevant → 9/10
- Context (10pts): Project management terminology strong and appropriate → 9/10
- Total: 78/100

Output:
{
    "calculation_reasoning": "Technical(38/50): PMP certification, JIRA, Agile/Scrum all matched. Budget control and stakeholder management not explicitly stated. Experience(22/30): 4 years is below the 5+ requirement; cross-functional team leadership is a positive indicator. Education(9/10): BSc Business Administration is relevant and appropriate. Context(9/10): Project management and Agile terminology is used correctly and consistently.",
    "match_score": 78,
    "missing_skills": ["Budget Control", "Stakeholder Management", "Risk Management", "MS Project", "Resource Planning"],
    "optimized_bullets": [
        "Led cross-functional teams of 10+ through full project lifecycle with accountability for timeline and budget adherence",
        "Managed stakeholder communications and expectation setting across departments using Agile/Scrum ceremonies",
        "Tracked project risks and mitigation plans using JIRA, ensuring on-time delivery across multiple concurrent projects"
    ],
    "interview_prep": [
        "Technical: How do you manage scope creep in an Agile project while keeping stakeholders aligned?",
        "Behavioral: Describe a project where the budget was at risk. How did you handle it?"
    ],
    "salary_range": "$85k - $115k",
    "radar_data": [
        {"subject": "Technical", "A": 76, "B": 100, "fullMark": 100},
        {"subject": "Experience", "A": 73, "B": 100, "fullMark": 100},
        {"subject": "Education", "A": 90, "B": 100, "fullMark": 100},
        {"subject": "Keywords", "A": 80, "B": 100, "fullMark": 100},
        {"subject": "Soft Skills", "A": 85, "B": 100, "fullMark": 100},
        {"subject": "Overall", "A": 78, "B": 100, "fullMark": 100}
    ],
    "suggestions": [
        "Explicitly mention any budget figures you managed (e.g. '$500k project budget') in your resume",
        "Add a bullet point about stakeholder reporting or executive communications",
        "Consider framing your 4-year experience as covering the equivalent scope of 5+ years given team size"
    ],
    "summary": "Competent and certified project manager with strong Agile and team leadership experience. Slightly below the experience threshold but PMP certification and cross-functional background make this a competitive application worth pursuing.",
    "recommended_roles": [
        {"role": "Project Manager", "match": "85%", "reason": "Core PM skills and certification match well"},
        {"role": "Scrum Master", "match": "80%", "reason": "Agile/Scrum expertise is directly applicable"},
        {"role": "Program Coordinator", "match": "78%", "reason": "Cross-functional coordination experience translates well"}
    ]
}
END EXAMPLE
"""
}


# ==============================================================================
# ROLE DETECTOR — Picks the right few-shot example based on the job description
# ==============================================================================

def pick_few_shot_example(job_description: str) -> str:
    jd_lower = job_description.lower()

    software_keywords = [
        "python", "java", "javascript", "backend", "frontend", "fullstack",
        "full-stack", "software engineer", "developer", "api", "django",
        "react", "node", "devops", "cloud", "aws", "docker", "kubernetes"
    ]
    data_keywords = [
        "data scientist", "machine learning", "ml engineer", "deep learning",
        "tensorflow", "pytorch", "scikit", "nlp", "data analyst", "analytics",
        "pandas", "numpy", "big data", "spark", "hadoop", "ai engineer"
    ]
    design_keywords = [
        "ux", "ui", "user experience", "user interface", "figma", "sketch",
        "adobe xd", "product designer", "interaction design", "usability",
        "wireframe", "prototype", "design system", "visual design"
    ]

    if any(kw in jd_lower for kw in software_keywords):
        return FEW_SHOT_EXAMPLES["software"]
    elif any(kw in jd_lower for kw in data_keywords):
        return FEW_SHOT_EXAMPLES["data"]
    elif any(kw in jd_lower for kw in design_keywords):
        return FEW_SHOT_EXAMPLES["design"]
    else:
        return FEW_SHOT_EXAMPLES["default"]


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
# CORE AI ANALYSIS — Few-Shot + Chain-of-Thought + Role-Specific Example
# ==============================================================================

async def get_ai_analysis(resume_text: str, job_description: str) -> dict:
    if not groq_client:
        return {
            "match_score": 0,
            "missing_skills": [],
            "suggestions": [],
            "summary": "No API Key configured."
        }

    # Pick the best few-shot example for this job description
    few_shot_example = pick_few_shot_example(job_description)

    system_prompt = f"""You are a senior recruiter and ATS (Applicant Tracking System) expert with 15 years of experience.
Your only output is valid JSON. No conversational text. No preamble. No markdown.

Study the following example carefully. Follow the EXACT same step-by-step reasoning approach and output structure:

{few_shot_example}

Key rules:
- Always reason through each rubric category step by step BEFORE assigning a score.
- Be specific and honest. Do not inflate scores.
- missing_skills should be real, actionable technical gaps — not soft skills.
- optimized_bullets must naturally incorporate missing keywords.
- salary_range must reflect the role, seniority, and location context if mentioned.
- recommended_roles must include 3 roles with realistic match percentages.
"""

    user_prompt = f"""Now analyze the resume below against the job description using this RUBRIC:

RUBRIC:
1. Technical Skills (50pts): Match of required tools, languages, frameworks, and certifications.
2. Experience (30pts): Years of experience, role alignment, seniority match, and team scope.
3. Education (10pts): Degree relevance and level match.
4. Context (10pts): Use of industry-specific terminology and domain familiarity.

INSTRUCTIONS:
- Think step by step through each rubric category.
- Show your detailed reasoning inside "calculation_reasoning".
- Then return the complete JSON object.

Return ONLY a JSON object with this exact structure:
{{
    "calculation_reasoning": "Detailed step-by-step breakdown of points per rubric category",
    "match_score": <total_points_out_of_100>,
    "missing_skills": ["Up to 5 specific technical gaps from the JD"],
    "optimized_bullets": ["3 resume bullets naturally using missing keywords"],
    "interview_prep": ["1 technical question", "1 behavioral question"],
    "salary_range": "e.g. $90k - $120k",
    "radar_data": [
        {{"subject": "Technical", "A": <0-100>, "B": 100, "fullMark": 100}},
        {{"subject": "Experience", "A": <0-100>, "B": 100, "fullMark": 100}},
        {{"subject": "Education", "A": <0-100>, "B": 100, "fullMark": 100}},
        {{"subject": "Keywords", "A": <0-100>, "B": 100, "fullMark": 100}},
        {{"subject": "Soft Skills", "A": <0-100>, "B": 100, "fullMark": 100}},
        {{"subject": "Overall", "A": <match_score>, "B": 100, "fullMark": 100}}
    ],
    "suggestions": ["3 specific, actionable improvement tips"],
    "summary": "2-sentence professional overview of the match quality",
    "recommended_roles": [
        {{"role": "Job Title", "match": "XX%", "reason": "Why this role fits"}},
        {{"role": "Job Title", "match": "XX%", "reason": "Why this role fits"}},
        {{"role": "Job Title", "match": "XX%", "reason": "Why this role fits"}}
    ]
}}

Resume:
{resume_text[:3000]}

Job Description:
{job_description[:3000]}
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
            max_tokens=2000,
            response_format={"type": "json_object"}
        )
        return json.loads(chat_completion.choices[0].message.content)

    except Exception as e:
        print(f"Groq Error: {e}")
        return {
            "match_score": 0,
            "missing_skills": [],
            "suggestions": [str(e)],
            "summary": "Analysis failed. Please try again."
        }


# ==============================================================================
# API ENDPOINT
# ==============================================================================

@app.post("/match")
async def match_resume(
    resume_file: UploadFile = File(None),
    resume_text: str = Form(None),
    job_file: UploadFile = File(None),
    job_description: str = Form(None)
):
    # --- Validate Resume Input ---
    if not resume_file and not resume_text:
        raise HTTPException(
            status_code=400,
            detail="Either a resume file (PDF/TXT) or resume text must be provided."
        )

    # --- Validate Job Description Input ---
    if not job_file and not job_description:
        raise HTTPException(
            status_code=400,
            detail="Either a job description file (PDF/TXT) or job description text must be provided."
        )

    # --- Extract Resume Text ---
    if resume_file:
        content = await resume_file.read()
        if resume_file.filename.endswith('.pdf'):
            extracted_resume_text = await asyncio.to_thread(extract_text_from_pdf, content)
        elif resume_file.filename.endswith('.txt'):
            extracted_resume_text = content.decode('utf-8')
        else:
            raise HTTPException(status_code=400, detail="Only PDF and TXT formats are supported for resumes.")
    else:
        extracted_resume_text = resume_text

    # --- Extract Job Description Text ---
    if job_file:
        content = await job_file.read()
        if job_file.filename.endswith('.pdf'):
            extracted_job_text = await asyncio.to_thread(extract_text_from_pdf, content)
        elif job_file.filename.endswith('.txt'):
            extracted_job_text = content.decode('utf-8')
        else:
            raise HTTPException(status_code=400, detail="Only PDF and TXT formats are supported for job descriptions.")
    else:
        extracted_job_text = job_description

    # --- Validate non-empty content ---
    if not extracted_resume_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from the resume. Please check the file.")
    if not extracted_job_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from the job description. Please check the file.")

    # --- Run AI Analysis ---
    analysis = await get_ai_analysis(extracted_resume_text.strip(), extracted_job_text.strip())

    # --- Attach metadata ---
    analysis["filename"] = resume_file.filename if resume_file else "Manual Input"
    analysis["detected_role_category"] = _detect_role_label(extracted_job_text)

    return analysis


def _detect_role_label(job_description: str) -> str:
    """Returns a human-readable label for the detected role category."""
    jd_lower = job_description.lower()
    if any(kw in jd_lower for kw in ["python", "backend", "frontend", "software engineer", "developer", "aws", "docker"]):
        return "Software Engineering"
    elif any(kw in jd_lower for kw in ["data scientist", "machine learning", "tensorflow", "pytorch", "nlp"]):
        return "Data Science / ML"
    elif any(kw in jd_lower for kw in ["ux", "ui", "figma", "product designer", "usability"]):
        return "UX / UI Design"
    else:
        return "General Professional"


# ==============================================================================
# ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)