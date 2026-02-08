from fastapi import APIRouter, HTTPException, Depends
from models import GenerateRequest
from database import get_db
from utils.llm import call_llm, parse_bullets
from dependencies.auth import get_current_user

router = APIRouter(prefix="/api", tags=["generate"])


@router.post("/generate")
def generate_bullets(
    request: GenerateRequest,
    user_id: str = Depends(get_current_user),
):
    if not request.experience_ids:
        raise HTTPException(
            status_code=400,
            detail="Please select at least one experience to generate bullets from."
        )

    conn = get_db()
    cur = conn.cursor()

    # Fetch selected experiences
    placeholders = ','.join(['%s'] * len(request.experience_ids))
    cur.execute(f"""
        SELECT title, content, skills
        FROM experiences
        WHERE id IN ({placeholders}) AND user_id = %s
    """, (*request.experience_ids, user_id))

    rows = cur.fetchall()

    cur.close()
    conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail="No experiences found")

    # Generate bullets for each project separately
    projects = []
    for row in rows:
        project_name = row[0]
        project_context = f"Project: {row[0]}\nContent: {row[1]}\nSkills: {', '.join(row[2] or [])}"

        prompt = f"""You are a professional resume writer. Create 3 compelling resume bullet points based STRICTLY on the candidate's experience provided below. DO NOT invent or add any information not present in the experience.

JOB DESCRIPTION: {request.job_description}

Candidate's ACTUAL Experience:
{project_context}

Generate 3 bullet points that:
- Start with strong action verbs
- Use ONLY information from the candidate's experience above
- Quantify achievements where possible but not necessary if none are available dont add them.
- Highlight relevant skills from the job description
- Are specific and results-oriented
- Are ATS-friendly: use standard job-related keywords from the job description, avoid graphics/symbols/columns, and use clear straightforward language that applicant tracking systems can parse

Return ONLY the 3 bullet points, one per line, each starting with •"""

        llm_output = call_llm(prompt)
        bullets = parse_bullets(llm_output, 3)

        projects.append({
            "project": project_name,
            "bullets": bullets
        })

    return {"projects": projects}
