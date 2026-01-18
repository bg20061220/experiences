import json
import os
import psycopg2
from sentence_transformers import SentenceTransformer
from pgvector.psycopg2 import register_vector

# Load embedding model
embedder = SentenceTransformer("all-MiniLM-L6-v2")

def embed(text):
    return embedder.encode(text).tolist()

# Connect to PostgreSQL
db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/resume_tailor")

conn = psycopg2.connect(db_url)
register_vector(conn)
cur = conn.cursor()

# Process both Projects and Roles folders
folders = ["/app/example-data/Projects", "/app/example-data/Roles"]
for folder in folders:
    for filename in os.listdir(folder):
        if not filename.endswith(".json"):
            continue
        
        filepath = os.path.join(folder, filename)
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Generate embedding from content
        content = data.get("content", "")
        embedding = embed(content)
        
        # Insert into PostgreSQL
        cur.execute("""
            INSERT INTO projects (id, type, title, date_range, skills, industry, tags, content, embedding)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, (
            data["id"],
            data["type"],
            data["title"],
            data.get("date_range"),
            data.get("skills", []),
            data.get("industry", []),
            data.get("tags", []),
            content,
            embedding
        ))
        
        print(f"✅ Inserted: {data['title']}")

conn.commit()
cur.close()
conn.close()
print("Migration complete!")