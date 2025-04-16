import torch
import torchaudio
import numpy as np
import librosa
from pathlib import Path
from typing import Optional, Tuple, List, Dict
import os
import pyttsx3
import json

from ..utils.audio_utils import load_audio_file, preprocess_audio, extract_mel_spectrogram

class VoiceCloner:
    def __init__(self, device: str = "cuda" if torch.cuda.is_available() else "cpu"):
        """
        Initialize the voice cloning system.
        
        Args:
            device: The device to run the model on (cuda or cpu)
        """
        self.device = device
        self.sample_rate = 22050  # Standard sample rate for voice cloning
        self.models_dir = Path("models")
        self.models_dir.mkdir(exist_ok=True)
        
        # Initialize TTS engine
        self.tts_engine = pyttsx3.init()
        
        # Get available voices
        self.voices = self.tts_engine.getProperty('voices')
        
        # Set default voice
        if self.voices:
            self.tts_engine.setProperty('voice', self.voices[0].id)
            
        # Initialize pre-trained models
        self._init_pretrained_models()
    
    def _init_pretrained_models(self):
        """Initialize pre-trained voice models from system voices."""
        for voice in self.voices:
            model_path = self.models_dir / f"voice_{voice.id.split('\\')[-1]}.json"
            if not model_path.exists():
                # Create a model for each system voice
                model_data = {
                    "id": f"voice_{voice.id.split('\\')[-1]}",
                    "name": voice.name,
                    "description": f"System voice: {voice.name}",
                    "model": {
                        "voice_id": voice.id,
                        "sample_rate": self.sample_rate,
                        "is_system_voice": True
                    }
                }
                
                with open(model_path, "w") as f:
                    json.dump(model_data, f, indent=2)
    
    def extract_voice_embedding(self, audio_path: str) -> np.ndarray:
        """
        Extract voice embedding from audio file.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Voice embedding as numpy array
        """
        # Load and preprocess audio
        waveform, _ = load_audio_file(audio_path, self.sample_rate)
        waveform = preprocess_audio(waveform, self.sample_rate)
        
        # Extract mel spectrogram
        mel_spec = extract_mel_spectrogram(waveform, self.sample_rate)
        
        # Convert to numpy array
        mel_spec = mel_spec.squeeze().numpy()
        
        # Use mel spectrogram as a simple voice embedding
        return mel_spec
    
    def create_voice_model(self, audio_samples: List[str]) -> dict:
        """
        Create a voice model from multiple audio samples.
        
        Args:
            audio_samples: List of paths to audio samples
            
        Returns:
            Dictionary containing the voice model
        """
        embeddings = []
        for sample in audio_samples:
            embedding = self.extract_voice_embedding(sample)
            embeddings.append(embedding)
        
        # Average the embeddings to create a single voice model
        voice_model = {
            'embeddings': np.mean(embeddings, axis=0),
            'sample_rate': self.sample_rate,
            'is_system_voice': False
        }
        return voice_model
    
    def synthesize_speech(self, text: str, voice_model: dict) -> torch.Tensor:
        """
        Synthesize speech from text using a voice model.
        
        Args:
            text: Text to synthesize
            voice_model: Voice model dictionary
            
        Returns:
            Synthesized audio as torch tensor
        """
        # If it's a system voice, use its voice_id
        if voice_model.get('is_system_voice', False):
            self.tts_engine.setProperty('voice', voice_model['voice_id'])
        
        # Save speech to temporary file
        temp_file = "temp_speech.wav"
        self.tts_engine.save_to_file(text, temp_file)
        self.tts_engine.runAndWait()
        
        # Load the generated audio
        waveform, sample_rate = torchaudio.load(temp_file)
        
        # Clean up temporary file
        os.remove(temp_file)
        
        return waveform 