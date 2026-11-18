"""Clip API scaffold. Media processing workers are intentionally separate from HTTP."""
from enum import Enum
from pathlib import Path
from uuid import uuid4
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="Clip API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to the deployed frontend origin before production.
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
MAX_UPLOAD_BYTES = 1_000_000_000
ALLOWED_TYPES = {"video/mp4", "video/quicktime", "video/webm"}

class JobStatus(str, Enum):
    queued = "queued"
    processing = "processing"
    complete = "complete"
    failed = "failed"

class AnalyzeRequest(BaseModel):
    source_url: str | None = None
    signals: list[str] = Field(default_factory=lambda: ["gaming", "reaction", "speech", "action"])
    clip_count: int = Field(default=10, ge=1, le=30)
    max_clip_seconds: int = Field(default=45, ge=10, le=180)
    aspect_ratio: str = "9:16"

jobs: dict[str, dict] = {}

@app.get("/health")
def health():
    return {"ok": True, "service": "clip-api", "version": "0.1.0"}

@app.post("/api/uploads")
async def upload_video(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(415, "Supported formats: MP4, MOV, WEBM")
    job_id = str(uuid4())
    suffix = Path(file.filename or "upload.mp4").suffix.lower()
    if suffix not in {".mp4", ".mov", ".webm"}:
        suffix = ".mp4"
    destination = UPLOAD_DIR / f"{job_id}{suffix}"
    size = 0
    try:
        with destination.open("wb") as output:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_UPLOAD_BYTES:
                    raise HTTPException(413, "Upload exceeds 1 GB limit")
                output.write(chunk)
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    jobs[job_id] = {"id": job_id, "status": JobStatus.queued, "filename": file.filename,
                    "bytes": size, "clips": [], "message": "Upload received; worker not connected yet."}
    return jobs[job_id]

@app.post("/api/analyze")
def create_analysis(request: AnalyzeRequest):
    if not request.source_url:
        raise HTTPException(400, "Provide an uploaded media ID or an authorized source URL.")
    if not request.source_url.startswith(("https://", "http://")):
        raise HTTPException(400, "Only HTTP(S) source URLs are accepted.")
    job_id = str(uuid4())
    jobs[job_id] = {"id": job_id, "status": JobStatus.queued, "request": request.model_dump(),
                    "clips": [], "message": "Queued; connect a media worker to process this job."}
    return jobs[job_id]

@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    if job_id not in jobs:
        raise HTTPException(404, "Job not found")
    return jobs[job_id]
