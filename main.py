from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
import shutil
import uuid
import tempfile
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
import os
import subprocess
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Geliştirme için tüm kaynaklara izin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Successfully Created!!"}

def check_ffmpeg():
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        return True
    except FileNotFoundError:
        return False

@app.post("/process")
async def process_file(file: UploadFile = File(...)):
    with tempfile.TemporaryDirectory() as tmpdir:
        # unique_name = f"{uuid.uuid4().hex}.jpg"
        input_path = os.path.join(tmpdir, "input.jpg") 
        output_path = os.path.join(tmpdir, "output.jpg")

        content = await file.read()
        with open(input_path, "wb") as f:
            f.write(content)

        command = [
            "ffmpeg",
            "-i", input_path,
            "-vf", f"scale=-1:5000:flags=lanczos",
            "-q:v", "2",
            "-y",
            output_path,
        ]

        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            with open(output_path, "rb") as f:
                processed_image = f.read()
            return StreamingResponse(
                io.BytesIO(processed_image),
                media_type="image/jpeg",
                headers={
                    "Content-Disposition": "inline; filename=processed.jpg"
                }
            )
        except subprocess.CalledProcessError as e:
            return {
                "error": "FFmpeg processing failed",
                "details": e.stderr
            }
        except FileNotFoundError:
            return {
                "error": "FFmpeg not found please install it",
            }
