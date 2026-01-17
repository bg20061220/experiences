from fastapi import FastAPI , HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel 
from typing import List , Optional 
import psycopg2
from sentence_transformers import SentenceTransformer
from pgvector.psycopg2 import register_vector
import requests 

app = FastAPI(title = "Resume Tailor API")

app.add_middleware(
    CORSMiddleware, 
    allow_origins = ["*"],
    allow_methods = ["*"],
    allow_headers = ["*"],
)

embedder = SentenceTransformer("all-MiniLM-L6-v2")

def get_db():
    conn = psycopg2.connect(
        host="localhost",
        database="resume_tailor",
        user="postgres",
        password="postgres"
    )
    register_vector(conn)
    return conn

class SearchRequest(BaseModel):
    query : str 
    limit : int = 5 

class ProjectData(BaseModel):
    id : str 
    type : str 
    title : str 
    date_range : Optional[str] = None 
    skills : List[str] = []
    industry : List[str] = []
    tags : List[str] = []
    content : str 

class GenerateRequest(BaseModel):
    job_description : str 
    num_bullets : int = 1

@app.get("/")
def root():
    return {"message : Resume Tailor API"}

@app.post("/api/projects")
def add_project(project : ProjectData):
    embedding = embedder.encode(project.content).tolist()
    conn = get_db()
    cur = conn.cursor()

    try : 
        cur.execute(""" 
        INSERT INTO projects (id , type , title , date_range , skills , industry , tags , content , embedding)
        VALUES(%s , %s , %s , %s , %s , %s , %s , %s , %s)
        """ , (
            project.id , 
            project.type , 
            project.title , 
            project.date_range , 
            project.skills , 
            project.industry , 
            project.tags , 
            project.content, 
            embedding
        ))
        conn.commit()
        return {"status" : "success" , "id" : project.id}
    except Exception as e : 
        conn.rollback()
        raise HTTPException(status_code=400 , details = str(e))
    finally : 
        cur.close()
        conn.close()

@app.post("/api/generate")
def generate_bullets(request : GenerateRequest):
    query_embedding = embedder.encode(request.job_description).tolist()
    conn = get_db()
    cur = conn.cursor()

    cur.execute(""" 
     SELECT title, content , skills, 
                     1 - (embedding <=> %s::vector) as similarity
     FROM projects
     ORDER BY embedding <=> %s::vector
     LIMIT 3
    """ , (query_embedding , query_embedding))

    relevant = cur.fetchall()
    cur.close()
    conn.close()

    if not relevant : 
        return {"bullets " : [] , "message" : "No relevant projects found"}
    context = "\n\n".join([
        f"Project: {row[0]}\nContent: {row[1]}\nSkills: {', '.join(row[2])}\nRelevance: {row[3]:.0%}"
        for row in relevant
    ])
    prompt = f"""You are a professional resume writer. Create {request.num_bullets} compelling resume bullet points based on this job description and the candidate's experience.
    JOB DESCRIPTION  : {request.job_description}
    Candidate's Experience : {context}

    Generate bullet points that : 
    - Start with strong action verbs 
    - Quantify achievements where possible
    - Highlight relevant skills from the job description
    - Are specifc and result-oriented

    Return ONLY the bullet points, one per line starting with • """

    try : 
        response = requests.post(
            "http://localhost:11434/api/generate",
            json = {"model" : "llama3.2" , "prompt" : prompt , "stream" :False},
            timeout = 240
        )
        llm_output = response.json()['response']

        # Parsing Bullets 
        bullets = [
            line.strip().lstrip('•').lstrip('-').strip()
            for line in llm_output.split('\n')
            if line.strip() and (line.strip().startswith('•') or line.strip().startswith('-'))
        ]
        
        return {"bullets": bullets[:request.num_bullets]}
    
    except Exception as e :
        raise HTTPException(status_code = 500 , detail = f"LLM error : {str(e)}")

@app.delete("/api/projects/{project_id}")
def delete_project(project_id : str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute ("DELETE FROM projects WHERE id = %s" , (project_id))
    deleted = cur.rowcount

    conn.commit()
    cur.close()
    conn.close()

    if deleted == 0 :
        raise HTTPException(status_code=404 , details = "Project not found")
    return {"status" : "deleted" , "id" : project_id}
@app.post("/api/search")
def search_projects(request : SearchRequest):
    query_embedding = embedder.encode(request.query).tolist()

    conn = get_db()
    cur  = conn.cursor()
    
    cur.execute("""
   SELECT id , type , title , content , skills , 1 - (embedding <=>%s::vector) as similarity 
    FROM projects 
    ORDER BY embedding <=> %s::vector
    LIMIT %s
        """ , (query_embedding  , query_embedding , request.limit))
    

    results = []

    for row in cur.fetchall():
         results.append({
        "id" : row[0],
        "type" : row[1],
        "title" : row[2],
        "content" : row[3],
        "skills" : row[4],
        "similarity" : row[5]
        })

    cur.close()
    conn.close()
    
    return {"results" : results}


@app.get("/api/projects")
def get_all_projects(): 
    conn = get_db()
    cur = conn.cursor()

    cur.execute(""" 
         SELECT id , type , title , date_range , skills , industry , tags 
         FROM projects 
         ORDER BY date_range DESC
    """)

    results = []
    for row in cur.fetchall():
        results.append({
            "id" : row[0],
            "type" : row[1],
            "title" : row[2],
            "date_range" : row[3],
            "skills" : row[4],
            "industry" : row[5],
            "tags" : row[6]
        })

    cur.close() 
    conn.close()

    return {"projects" : results , "count" : len(results)}

@app.get("/health") 
def health():
    return {"status" : "healthy"}



