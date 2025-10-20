from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import shutil
import uuid
import tempfile
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
import os
import subprocess

app = FastAPI()

os.makedirs("static", exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Geliştirme için tüm kaynaklara izin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

scaled_images = []

@app.get("/")
def root():
    return {"message": "Successfully Created!!"}

@app.post("/process")
async def process_file(file: UploadFile = File(...)):
    with tempfile.TemporaryDirectory() as tmpdir:
        unique_name = f"{uuid.uuid4().hex}.jpg"
        input_path = os.path.join(tmpdir, unique_name) 
        output_path = os.path.join(tmpdir, f"processed_{unique_name}")

        with open(input_path, "wb") as f:
            f.write(await file.read())

        command = [
            "ffmpeg",
            "-i", input_path,
            "-vf", f"scale=-1:5000:flags=lanczos",
            "-y",
            output_path,
        ]

        subprocess.run(command, check=True)

        final_path = os.path.join("static", f"processed_{unique_name}")
        shutil.move(output_path, final_path)

        return FileResponse(
            final_path,
            media_type="image/jpeg",
            filename="processed.jpg"
        )
