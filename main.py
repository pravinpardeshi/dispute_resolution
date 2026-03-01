
from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from agent import graph
from ocr import extract_text_from_pdf

app = FastAPI()
UPLOAD_DIR = "uploads"

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/submit")
async def submit_dispute(case_id: str = Form(...),
                         customer_claim: str = Form(...),
                         merchant_evidence: str = Form(""),
                         file: UploadFile = File(None)):

    if file:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        merchant_evidence += extract_text_from_pdf(file_path)

    result = graph.invoke({
        "case_id": case_id,
        "customer_claim": customer_claim,
        "merchant_evidence": merchant_evidence,
        "rule_score": 0.0,
        "fraud_score": 0.0,
        "final_decision": {}
    })

    return result["final_decision"]

@app.get("/", response_class=HTMLResponse)
async def home():
    with open("static/index.html", "r") as f:
        return f.read()

app.mount("/static", StaticFiles(directory="static"), name="static")
