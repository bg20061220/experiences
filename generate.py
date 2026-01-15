# generate.py
import requests

def generate_resume_bullets(chunk, model="llama2:7b"):
    prompt = f"""
You are an expert resume writer.

Using ONLY the information below, generate 3 concise, ATS-friendly resume bullet points.

Experience:
{chunk}

Rules:
- ONLY use the information provided; do NOT invent numbers, tools, or outcomes
- One bullet per line, plain text only
- DO NOT use brackets, quotes, parentheses, or any list/tuple notation
- Start with strong action verbs
- Focus on technical impact
- Keep each bullet ≤ 20 words
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False
        }
    )

    text = response.json()["response"]
    # Clean up output
    text = text.replace("[","").replace("]","").replace("(","").replace(")","").replace("'","")
    bullets = [line.strip("- ").strip() for line in text.splitlines() if line.strip()]
    return bullets


if __name__ == "__main__":
    first_experience = " Put the experience here."


    bullets = generate_resume_bullets(first_experience)
    print("Generated Resume Bullets:\n")
    for b in bullets:
        print(f"- {b}")
