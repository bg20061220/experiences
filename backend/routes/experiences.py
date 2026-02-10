from fastapi import APIRouter, HTTPException, Depends, Request
from models import ProjectData, BatchExperienceRequest
from database import get_db
from utils.embeddings import get_embedding, get_embeddings_batch
from dependencies.auth import get_current_user
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/api", tags=["experiences"])


@router.post("/experiences")
@limiter.limit("15/minute")
def add_experience(
    project: ProjectData,
    request: Request,
    user_id: str = Depends(get_current_user),
):
    embedding = get_embedding(project.content)
    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute("""
        INSERT INTO experiences (id, user_id, type, title, date_range, skills, industry, tags, content, embedding)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            project.id,
            user_id,
            project.type,
            project.title,
            project.date_range,
            project.skills,
            project.industry,
            project.tags,
            project.content,
            embedding
        ))
        conn.commit()
        return {"status": "success", "id": project.id}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while processing your request")
    finally:
        cur.close()
        conn.close()


@router.post("/experiences/batch")
@limiter.limit("5/minute")
def add_experiences_batch(
    body: BatchExperienceRequest,
    request: Request,
    user_id: str = Depends(get_current_user),
):
    if not body.experiences:
        raise HTTPException(status_code=400, detail="No experiences provided")

    texts = [exp.content for exp in body.experiences]
    embeddings = get_embeddings_batch(texts)

    conn = get_db()
    cur = conn.cursor()

    try:
        for exp, embedding in zip(body.experiences, embeddings):
            cur.execute("""
            INSERT INTO experiences (id, user_id, type, title, date_range, skills, industry, tags, content, embedding)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                exp.id,
                user_id,
                exp.type,
                exp.title,
                exp.date_range,
                exp.skills,
                exp.industry,
                exp.tags,
                exp.content,
                embedding
            ))
        conn.commit()
        return {"status": "success", "count": len(body.experiences)}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while processing your request")
    finally:
        cur.close()
        conn.close()


@router.get("/experiences")
def get_all_experiences(user_id: str = Depends(get_current_user)):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
         SELECT id, type, title, date_range, skills, industry, tags, content
         FROM experiences
         WHERE user_id = %s
         ORDER BY date_range DESC
    """, (user_id,))

    results = []
    for row in cur.fetchall():
        results.append({
            "id": row[0],
            "type": row[1],
            "title": row[2],
            "date_range": row[3],
            "skills": row[4],
            "industry": row[5],
            "tags": row[6],
            "content": row[7]
        })

    cur.close()
    conn.close()

    return {"experiences": results, "count": len(results)}


@router.put("/experiences/{experience_id}")
@limiter.limit("15/minute")
def update_experience(
    experience_id: str,
    project: ProjectData,
    request: Request,
    user_id: str = Depends(get_current_user),
):
    embedding = get_embedding(project.content)
    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute("""
            UPDATE experiences
            SET type = %s, title = %s, date_range = %s, skills = %s,
                industry = %s, tags = %s, content = %s, embedding = %s
            WHERE id = %s AND user_id = %s
        """, (
            project.type,
            project.title,
            project.date_range,
            project.skills,
            project.industry,
            project.tags,
            project.content,
            embedding,
            experience_id,
            user_id
        ))

        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Experience not found")

        conn.commit()
        return {"status": "updated", "id": experience_id}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while processing your request")
    finally:
        cur.close()
        conn.close()


@router.delete("/experiences/{experience_id}")
@limiter.limit("15/minute")
def delete_experience(
    experience_id: str,
    request: Request,
    user_id: str = Depends(get_current_user),
):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM experiences WHERE id = %s AND user_id = %s",
        (experience_id, user_id)
    )
    deleted = cur.rowcount

    conn.commit()
    cur.close()
    conn.close()

    if deleted == 0:
        raise HTTPException(status_code=404, detail="Experience not found")
    return {"status": "deleted", "id": experience_id}
