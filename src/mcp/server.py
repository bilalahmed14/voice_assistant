from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
from typing import List, Optional
import os
import json
from pathlib import Path
import uuid

from src.core.voice_cloner import VoiceCloner
from src.utils.audio_utils import save_audio

app = FastAPI(title="Voice Cloning MCP Server")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize voice cloner
voice_cloner = VoiceCloner()

# Create necessary directories
MODELS_DIR = Path("models")
AUDIO_DIR = Path("audio")
MODELS_DIR.mkdir(exist_ok=True)
AUDIO_DIR.mkdir(exist_ok=True)

class VoiceModel(BaseModel):
    id: str
    name: str
    description: Optional[str] = None

@app.post("/voice/enroll")
async def enroll_voice(
    name: str,
    description: Optional[str] = None,
    files: List[UploadFile] = File(...)
):
    """
    Enroll a new voice model.
    """
    try:
        # Save uploaded files temporarily
        temp_files = []
        for file in files:
            temp_path = f"temp_{file.filename}"
            with open(temp_path, "wb") as f:
                f.write(await file.read())
            temp_files.append(temp_path)
        
        # Create voice model
        voice_model = voice_cloner.create_voice_model(temp_files)
        
        # Generate unique ID
        model_id = f"voice_{len(os.listdir(MODELS_DIR)) + 1}"
        
        # Save model
        model_path = MODELS_DIR / f"{model_id}.json"
        with open(model_path, "w") as f:
            json.dump({
                "id": model_id,
                "name": name,
                "description": description,
                "model": voice_model
            }, f)
        
        # Clean up temp files
        for temp_file in temp_files:
            os.remove(temp_file)
        
        return {"id": model_id, "name": name, "description": description}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/voice/synthesize")
async def synthesize_speech(
    model_id: str = Query(..., description="ID of the voice model to use"),
    text: str = Query(..., description="Text to synthesize")
):
    """
    Synthesize speech using a voice model.
    """
    try:
        # Load voice model
        model_path = MODELS_DIR / f"{model_id}.json"
        if not model_path.exists():
            raise HTTPException(status_code=404, detail="Voice model not found")
        
        with open(model_path, "r") as f:
            model_data = json.load(f)
        
        # Synthesize speech
        audio = voice_cloner.synthesize_speech(text, model_data["model"])
        
        # Save audio to file
        audio_id = str(uuid.uuid4())
        audio_path = AUDIO_DIR / f"{audio_id}.wav"
        save_audio(audio, voice_cloner.sample_rate, str(audio_path))
        
        return {
            "status": "success",
            "audio_id": audio_id,
            "audio_path": str(audio_path)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/voice/audio/{audio_id}")
async def get_audio(audio_id: str):
    """
    Get synthesized audio file.
    """
    audio_path = AUDIO_DIR / f"{audio_id}.wav"
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(str(audio_path))

@app.get("/voice/models")
async def list_voice_models():
    """
    List all available voice models.
    """
    models = []
    for file in MODELS_DIR.glob("*.json"):
        with open(file, "r") as f:
            model_data = json.load(f)
            models.append(VoiceModel(
                id=model_data["id"],
                name=model_data["name"],
                description=model_data.get("description")
            ))
    return models

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 