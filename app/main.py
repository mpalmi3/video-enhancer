import json
import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.services.transcribe import transcribe
from app.services.cleanup import cleanup_script
from app.services.tts import generate_voiceover, VOICES
from app.services.captions import generate_srt
from app.services.video import extract_audio, assemble_video, get_video_duration

load_dotenv()

app = FastAPI(title="Video Enhancer")

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOADS_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "output"
STATIC_DIR = Path(__file__).resolve().parent / "static"

UPLOADS_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# In-memory job store
jobs: dict[str, dict] = {}


class GenerateRequest(BaseModel):
    script: str
    segments: list[dict]
    voice: str = "nova"


@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    index_path = STATIC_DIR / "index.html"
    return HTMLResponse(content=index_path.read_text(encoding="utf-8"))


@app.post("/upload")
async def upload_video(file: UploadFile):
    if not file.filename:
        raise HTTPException(400, "No file provided")

    job_id = uuid.uuid4().hex[:12]
    job_dir = UPLOADS_DIR / job_id
    job_dir.mkdir(exist_ok=True)

    ext = Path(file.filename).suffix
    video_path = job_dir / f"original{ext}"

    with open(video_path, "wb") as f:
        content = await file.read()
        f.write(content)

    jobs[job_id] = {
        "video_path": str(video_path),
        "status": "uploaded",
    }

    return {"job_id": job_id, "filename": file.filename}


@app.post("/transcribe/{job_id}")
async def transcribe_video(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")

    video_path = job["video_path"]

    # Extract audio
    audio_path = extract_audio(video_path)
    job["audio_path"] = audio_path

    # Get original video duration
    duration = get_video_duration(video_path)
    job["original_duration"] = duration

    # Transcribe
    result = transcribe(audio_path)
    job["raw_transcript"] = result["text"]
    job["raw_segments"] = result["segments"]

    # Cleanup with GPT-4o-mini
    cleaned = cleanup_script(result["text"], result["segments"])
    job["cleaned_text"] = cleaned["cleaned_text"]
    job["cleaned_segments"] = cleaned["segments"]
    job["status"] = "transcribed"

    return {
        "raw_transcript": result["text"],
        "cleaned_text": cleaned["cleaned_text"],
        "segments": cleaned["segments"],
    }


@app.post("/generate/{job_id}")
async def generate_video(job_id: str, req: GenerateRequest):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    if req.voice not in VOICES:
        raise HTTPException(400, f"Voice must be one of: {VOICES}")

    job_dir = UPLOADS_DIR / job_id
    output_dir = OUTPUT_DIR / job_id
    output_dir.mkdir(exist_ok=True)

    # Generate TTS audio
    tts_path = str(output_dir / "voiceover.mp3")
    generate_voiceover(req.script, req.voice, tts_path)
    job["tts_path"] = tts_path

    # Generate SRT captions
    srt_path = str(output_dir / "captions.srt")
    generate_srt(
        req.segments,
        srt_path,
        tts_audio_path=tts_path,
        original_duration=job.get("original_duration"),
    )
    job["srt_path"] = srt_path

    # Assemble final video
    final_path = str(output_dir / "final.mp4")
    assemble_video(job["video_path"], tts_path, srt_path, final_path)
    job["output_path"] = final_path
    job["status"] = "complete"

    return {"status": "complete", "job_id": job_id}


@app.get("/preview/{job_id}")
async def preview_video(job_id: str):
    job = jobs.get(job_id)
    if not job or "output_path" not in job:
        raise HTTPException(404, "Video not ready")

    return FileResponse(
        job["output_path"],
        media_type="video/mp4",
        headers={"Accept-Ranges": "bytes"},
    )


@app.get("/download/{job_id}")
async def download_video(job_id: str):
    job = jobs.get(job_id)
    if not job or "output_path" not in job:
        raise HTTPException(404, "Video not ready")

    return FileResponse(
        job["output_path"],
        media_type="video/mp4",
        filename=f"enhanced_{job_id}.mp4",
    )
