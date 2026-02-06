import os
import requests
from fastapi import HTTPException

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


def call_llm(prompt: str, model: str = "llama-3.1-8b-instant", temperature: float = 0.3, timeout: int = 60) -> str:
    """Call Groq API and return the response text."""
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY environment variable not set")

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature
    }

    try:
        response = requests.post(
            GROQ_API_URL,
            headers=headers,
            json=payload,
            timeout=timeout
        )

        if response.status_code == 401:
            raise HTTPException(status_code=500, detail="Invalid GROQ_API_KEY")
        elif response.status_code == 429:
            raise HTTPException(status_code=429, detail="Groq rate limit exceeded, try again later")
        elif response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Groq API error: {response.text}")

        return response.json()["choices"][0]["message"]["content"]

    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="LLM request timed out")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"LLM connection error: {str(e)}")


def parse_bullets(llm_output: str, max_bullets: int) -> list:
    """Parse bullet points from LLM output."""
    # First try to find lines starting with bullet markers
    bullets = [
        line.strip().lstrip('•').lstrip('-').lstrip('*').strip()
        for line in llm_output.split('\n')
        if line.strip() and (line.strip().startswith('•') or line.strip().startswith('-') or line.strip().startswith('*'))
    ]

    # If no bullets found, use the entire output as a single bullet
    if not bullets:
        cleaned = llm_output.strip()
        if cleaned:
            bullets = [cleaned]

    return bullets[:max_bullets]
