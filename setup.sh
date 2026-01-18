#!/bin/bash

echo "🚀 Setting up Resume Tailor..."

# Start containers
docker-compose up -d

echo "⏳ Waiting for database to be ready..."
sleep 10

# Setup database
docker-compose exec backend python setup_database.py

# Migrate example data
docker-compose exec backend python migrate_to_postgres.py

# Pull LLM model
echo "📥 Downloading LLM model (this may take a few minutes)..."
docker-compose exec ollama ollama pull llama3.2

echo "✅ Setup complete! Access the app at http://localhost:3000"