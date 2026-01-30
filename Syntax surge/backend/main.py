from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from groq import Groq
import os, re
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Serve frontend as static
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------- ROUTES FOR PAGES --------
@app.get("/")
def login_page():
    return FileResponse("../frontend/login.html")

@app.get("/dashboard")
def dashboard():
    return FileResponse("../frontend/index.html")

# -------- AI SETUP --------
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL_NAME = "llama-3.3-70b-versatile"

class CodeRequest(BaseModel):
    code: str

@app.post("/api/review")
def review_code(req: CodeRequest):
    if not req.code.strip():
        raise HTTPException(status_code=400, detail="Empty code")

    prompt = f"""
Review the code and list issues.

## 🔴 Critical Issues
## 🟠 High Priority
## 🟡 Medium Priority
## 🟢 Low Priority

Code:
{req.code}
"""

    res = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1500,
    )

    return {"result": res.choices[0].message.content}