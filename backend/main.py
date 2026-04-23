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
    Internal Objective: DEEP AUDIT of resume against job description. 
    
    Resume Text:
    {resume_text}
    
    Job Description Text:
    {job_description}
    
    Instruction for AI:
    1. EXHAUSTIVELY list every technical tool, language, and framework mentioned in the Job Description.
    2. CHECK which of those are specifically missing or not demonstrated in the Resume Text.
    3. OUTPUT only those MISSING items as short 1-2 word keywords.
    
    Provide the analysis in JSON format ONLY:
    {{
        "match_score": (integer 0-100),
        "missing_skills": ["Java", "Kubernetes"], (Strictly the result of your deep audit)
        "optimized_bullets": [
             "Spearheaded the integration of [Missing Skill] to optimize backend latency by 15%",
             "Orchestrated [Missing Skill] deployments ensuring 99.9% uptime"
        ], (Professional bullet points to fix the missing skills)
        "interview_prep": [
            "How would you handle [Missing Skill] in a high-concurrency production environment?",
            "Explain a scenario where you'd prefer [Tool A] over [Missing Skill]?"
        ],
        "salary_range": "e.g. $100k - $120k",
        "radar_data": [
            {{"subject": "React", "A": 80, "B": 100, "fullMark": 100}},
            {{"subject": "Node.js", "A": 40, "B": 90, "fullMark": 100}}
        ], (List of 6 key skills comparing Resume [A] vs Job [B])
        "suggestions": ["suggestion1", "suggestion2"],
        "summary": "Match summary.",
        "recommended_roles": [
            {{"role": "Title", "match": "90%", "reason": "Why?"}},
            {{"role": "Title", "match": "75%", "reason": "Why?"}}
        ]
    }}
    """
    
    try:
        chat_completion = await groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0,
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

    analysis = await get_ai_analysis(extracted_resume_text, extracted_job_text)
    
    # Metadata
    analysis["filename"] = resume_file.filename if resume_file else "Manual Input"

    return analysis

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
