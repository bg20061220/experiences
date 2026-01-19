# Resume Tailor - AI-Powered Resume Customization Tool

Automatically tailor your resume to any job description using vector search and local LLMs.

## Features
- 🔍 Vector similarity search with pgvector
- 🤖 Local LLM integration (Ollama + llama3.2)
- 🎯 Smart matching of experience to job requirements
- 🚀 Fully containerized with Docker
- 🔒 100% local - your data never leaves your machine

## Prerequisites
- Docker Desktop ( Download link https://www.docker.com/products/docker-desktop/) 
- (Optional) NVIDIA GPU for faster LLM inference

## Quick Start

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/Resume-Tailor-Ai-
cd Resume-Tailor-Ai-
```

2. **Add your data:**
   - Replace files in `example-data/Projects/` and `example-data/Roles/` with your own JSON files
   - Follow the same format as the example files

3. **Run setup script:**
```bash
chmod +x setup.sh
./setup.sh
```

4. **Access the app:**
   - Open http://localhost:3000 in your browser

## Usage

1. Paste a job description
2. Click "Find Relevant Experience"
3. Select a project from the top 3 matches
4. Get AI-generated, tailored resume bullets

## Manual Setup (if setup.sh doesn't work)
```bash
# Start containers
docker-compose up -d --build

# Wait 10 seconds for DB to start
sleep 10

# Setup database
docker-compose exec backend python setup_database.py
docker-compose exec backend python migrate_to_postgres.py

# Download LLM model
docker-compose exec ollama ollama pull llama3.2
```

## Stopping the App
```bash
docker-compose down
```

## Tech Stack
- **Backend**: FastAPI + PostgreSQL + pgvector
- **Frontend**: React
- **Embeddings**: sentence-transformers (MiniLM)
- **LLM**: Ollama (llama3.2)

## Architecture
```
Frontend (React) → Backend (FastAPI) → PostgreSQL + pgvector
                                    ↓
                                 Ollama (LLM)
```

## License
MIT
