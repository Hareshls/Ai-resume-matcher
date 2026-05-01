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

    # Model logic moved to chat_completion call for strictness
    
    try:
        chat_completion = await groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a senior recruiter. Your only output is valid JSON. No conversational text. No preamble."},
                {"role": "user", "content": f"""Analyze this resume against the JD using this RUBRIC:
1. Technical Skills (50pts): Match of tools/languages.
2. Experience (30pts): Role and seniority alignment.
3. Education (10pts): Degree match.
4. Context (10pts): Industry terminology.

Return ONLY a JSON object:
{{
    "calculation_reasoning": "Detailed breakdown of points for each rubric category",
    "match_score": <total_points_out_of_100>,
    "missing_skills": ["Up to 5 technical gaps"],
    "optimized_bullets": ["3 bullets using missing keywords"],
    "interview_prep": ["1 technical, 1 behavioral question"],
    "salary_range": "e.g. $100k - $140k",
    "radar_data": [
        {{"subject": "Technical", "A": <0-100>, "B": 100, "fullMark": 100}},
        {{"subject": "Experience", "A": <0-100>, "B": 100, "fullMark": 100}},
        {{"subject": "Education", "A": <0-100>, "B": 100, "fullMark": 100}},
        {{"subject": "Keywords", "A": <0-100>, "B": 100, "fullMark": 100}},
        {{"subject": "Soft Skills", "A": <0-100>, "B": 100, "fullMark": 100}},
        {{"subject": "Overall", "A": <score>, "B": 100, "fullMark": 100}}
    ],
    "suggestions": ["3 actionable tips"],
    "summary": "2-sentence professional overview",
    "recommended_roles": [
        {{"role": "Title", "match": "XX%", "reason": "alignment logic"}}
    ]
}}

Resume: {resume_text[:3000]}
JD: {job_description[:3000]}
"""}
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
