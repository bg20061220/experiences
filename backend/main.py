from dotenv import load_dotenv
load_dotenv()  # Load .env before other imports

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import experiences, search, generate

app = FastAPI(title="Resume Tailor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://resumetailorai.vercel.app",
        "https://resumetailorai-9pzkpka42-bhavya-goels-projects.vercel.app",
    ],
    allow_origin_regex=r"https://resumetailorai.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(experiences.router)
app.include_router(search.router)
app.include_router(generate.router)


@app.get("/")
def root():
    return {"message : Resume Tailor API"}


@app.get("/health")
def health():
    return {"status": "healthy"}
