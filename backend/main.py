import os
import json
import re
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

# app setup

def extract_text_from_pdf(file_content):
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

async def get_ai_analysis(resume_text, job_description):
    if not groq_client:
        return {"match_score": 0, "missing_skills": [], "suggestions": [], "summary": "No API Key"}

    prompt = f"""
    Internal Objective: Perform a rigorous ATS (Applicant Tracking System) audit of the provided resume against the job description.
    
    Resume Text:
    {resume_text}
    
    Job Description Text:
    {job_description}
    
    Scoring Rubric (0-100):
    1. Technical Skills Match (50 points): Percentage of required tools, languages, and frameworks present in the resume.
    2. Experience & Role Match (30 points): Alignment of previous roles and years of experience with the JD requirements.
    3. Education & Certifications (10 points): Matching degrees or specific certifications.
    4. Keywords & Context (10 points): Proper use of industry-specific terminology.

    Instructions:
    1. FIRST, perform an internal step-by-step calculation based on the rubric.
    2. EXHAUSTIVELY extract all required skills from the Job Description.
    3. Identify which of these are MISSING or weak in the Resume.
    4. Calculate the 'match_score' strictly based on the rubric.
    5. Ensure the analysis is objective and identical for the same input.

    Provide the analysis in JSON format ONLY:
    {{
        "calculation_reasoning": "Internal step-by-step breakdown of the score based on the rubric",
        "match_score": <calculated_integer_between_0_100>,
        "missing_skills": ["List of 3-7 specific missing technical skills"],
        "optimized_bullets": [
             "Action-oriented bullet points incorporating missing keywords",
             "Example: Leveraged [Missing Skill] to optimize [Process]..."
        ],
        "interview_prep": [
            "Specific technical question based on the JD requirements",
            "Behavioral question relevant to the role"
        ],
        "salary_range": "Estimated based on JD and Role (e.g., $90k - $120k)",
        "radar_data": [
            {{"subject": "Technical", "A": <score>, "B": 100, "fullMark": 100}},
            {{"subject": "Experience", "A": <score>, "B": 100, "fullMark": 100}},
            {{"subject": "Education", "A": <score>, "B": 100, "fullMark": 100}},
            {{"subject": "Keywords", "A": <score>, "B": 100, "fullMark": 100}},
            {{"subject": "Soft Skills", "A": <score>, "B": 100, "fullMark": 100}},
            {{"subject": "Overall", "A": <score>, "B": 100, "fullMark": 100}}
        ],
        "suggestions": ["3 actionable tips to improve the resume match"],
        "summary": "A 2-sentence professional summary of the match quality.",
        "recommended_roles": [
            {{"role": "Primary Target Role", "match": "90%", "reason": "Close alignment with skill X and Y"}},
            {{"role": "Alternative Role", "match": "70%", "reason": "Strong in X but lacks Y"}}
        ]
    }}
    """
    
    try:
        chat_completion = await groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a senior technical recruiter and ATS specialist. Your task is to provide objective, consistent, and data-driven resume analysis. Output MUST be valid JSON only. Do not hallucinate scores; follow the rubric strictly."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant",
            temperature=0,
            seed=42,
            top_p=1,
            max_tokens=4096,
            response_format={"type": "json_object"}
        )
        return json.loads(chat_completion.choices[0].message.content)
    except Exception as e:
        print(f"Groq Error: {e}")
        return {"match_score": 0, "missing_skills": [], "suggestions": [str(e)], "summary": "Failed."}

@app.post("/match")
async def match_resume(
    resume_file: UploadFile = File(None),
    resume_text: str = Form(None),
    job_file: UploadFile = File(None),
    job_description: str = Form(None)
):
    # Validate Resume Input
    if not resume_file and not resume_text:
        raise HTTPException(status_code=400, detail="Either resume file or resume text must be provided")

    # Validate Job Description Input
    if not job_file and not job_description:
        raise HTTPException(status_code=400, detail="Either job file or job description text must be provided")

    # Extract Resume Text
    if resume_file:
        content = await resume_file.read()
        if resume_file.filename.endswith('.pdf'):
            extracted_resume_text = await asyncio.to_thread(extract_text_from_pdf, content)
        elif resume_file.filename.endswith('.txt'):
            extracted_resume_text = content.decode('utf-8')
        else:
            raise HTTPException(status_code=400, detail="Only PDF/TXT supported for resumes")
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
            raise HTTPException(status_code=400, detail="Only PDF/TXT supported for job descriptions")
    else:
        extracted_job_text = job_description

    analysis = await get_ai_analysis(extracted_resume_text.strip(), extracted_job_text.strip())
    
    # Metadata
    analysis["filename"] = resume_file.filename if resume_file else "Manual Input"

    return analysis

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
