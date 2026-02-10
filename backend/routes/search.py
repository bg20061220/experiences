from fastapi import APIRouter, Depends, Request
from models import SearchRequest
from database import get_db
from utils.embeddings import get_embedding
from dependencies.auth import get_current_user
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/api", tags=["search"])

SIMILARITY_THRESHOLD = 0


@router.post("/search")
@limiter.limit("10/minute")
def search_experiences(
    body: SearchRequest,
    request: Request,
    user_id: str = Depends(get_current_user),
):
    query_embedding = get_embedding(body.query, input_type="search_query")

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, type, title, date_range, content, skills
        FROM experiences
        WHERE user_id = %s
        ORDER BY embedding <=> %s::vector
        LIMIT 3
    """, (user_id, query_embedding))

    results = []
    for row in cur.fetchall():
        results.append({
            "id": row[0],
            "type": row[1],
            "title": row[2],
            "date_range": row[3],
            "content": row[4],
            "skills": row[5]
        })

    cur.close()
    conn.close()

    if not results:
        return {
            "results": [],
            "message": "No experiences found matching your query. Try broader search terms."
        }

    return {"results": results}
