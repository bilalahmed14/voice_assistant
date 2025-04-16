import requests
import json
from typing import List, Optional
import os
import tempfile
import sounddevice as sd
import soundfile as sf
from pathlib import Path

class VoiceCloningClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def enroll_voice(self, name: str, audio_files: List[str], description: str = None) -> dict:
        """
        Enroll a new voice model.
        
        Args:
            name: Name of the voice model
            audio_files: List of paths to audio files
            description: Optional description of the voice model
            
        Returns:
            Dictionary containing the voice model information
        """
        files = []
        for audio_file in audio_files:
            if not os.path.exists(audio_file):
                raise FileNotFoundError(f"Audio file not found: {audio_file}")
            files.append(("files", open(audio_file, "rb")))
        
        data = {"name": name}
        if description:
            data["description"] = description
        
        response = requests.post(
            f"{self.base_url}/voice/enroll",
            data=data,
            files=files
        )
        
        # Close all file handles
        for _, file in files:
            file.close()
        
        if response.status_code != 200:
            raise Exception(f"Error enrolling voice: {response.text}")
        
        return response.json()
    
    def synthesize_speech(self, model_id: str, text: str, play_audio: bool = True) -> dict:
        """
        Synthesize speech using a voice model.
        
        Args:
            model_id: ID of the voice model to use
            text: Text to synthesize
            play_audio: Whether to play the audio after synthesis
            
        Returns:
            Dictionary containing the synthesis result
        """
        # Send parameters as query parameters
        params = {
            "model_id": model_id,
            "text": text
        }
        
        response = requests.post(
            f"{self.base_url}/voice/synthesize",
            params=params
        )
        
        if response.status_code != 200:
            raise Exception(f"Error synthesizing speech: {response.text}")
        
        result = response.json()
        
        if play_audio:
            self.play_audio(result["audio_id"])
        
        return result
    
    def play_audio(self, audio_id: str):
        """
        Play synthesized audio.
        
        Args:
            audio_id: ID of the audio file to play
        """
        # Download audio file
        response = requests.get(f"{self.base_url}/voice/audio/{audio_id}")
        if response.status_code != 200:
            raise Exception(f"Error downloading audio: {response.text}")
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_file.write(response.content)
            temp_path = temp_file.name
        
        try:
            # Play audio
            data, samplerate = sf.read(temp_path)
            sd.play(data, samplerate)
            sd.wait()  # Wait until audio is finished playing
        finally:
            # Clean up temporary file
            os.unlink(temp_path)
    
    def list_voice_models(self) -> List[dict]:
        """
        List all available voice models.
        
        Returns:
            List of voice model dictionaries
        """
        response = requests.get(f"{self.base_url}/voice/models")
        
        if response.status_code != 200:
            raise Exception(f"Error listing voice models: {response.text}")
        
        return response.json()

def main():
    # Create client
    client = VoiceCloningClient()
    
    # List available voice models
    print("\nAvailable voice models:")
    models = client.list_voice_models()
    print(json.dumps(models, indent=2))
    
    # Example: Clone a new voice
    print("\nExample 1: Clone a new voice")
    print("To clone a voice, you need audio samples (WAV files) of the target voice.")
    print("Example command:")
    print('client.enroll_voice(')
    print('    name="John Doe",')
    print('    audio_files=["sample1.wav", "sample2.wav"],')
    print('    description="John Doe\'s voice model"')
    print(')')
    
    # Example: Use an existing voice model
    print("\nExample 2: Use an existing voice model")
    if models:
        print("Using the first available voice model...")
        model_id = models[0]["id"]
        text = "Hello! This is a test of the voice synthesis system."
        print(f"Synthesizing: '{text}'")
        try:
            result = client.synthesize_speech(
                model_id=model_id,
                text=text
            )
            print("Speech synthesized successfully!")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("No voice models available.")
    
    # Interactive mode
    print("\nWould you like to:")
    print("1. Clone a new voice (requires WAV files)")
    print("2. Synthesize speech with an existing voice")
    print("3. Exit")
    
    choice = input("Enter your choice (1-3): ")
    
    if choice == "1":
        name = input("Enter a name for the voice model: ")
        print("Enter paths to WAV files (one per line, empty line to finish):")
        audio_files = []
        while True:
            path = input("WAV file path (or empty to finish): ")
            if not path:
                break
            audio_files.append(path)
        
        if audio_files:
            description = input("Enter a description (optional): ")
            try:
                result = client.enroll_voice(name, audio_files, description)
                print("Voice enrolled successfully!")
                print(json.dumps(result, indent=2))
            except Exception as e:
                print(f"Error: {e}")
        else:
            print("No audio files provided.")
    
    elif choice == "2":
        if not models:
            print("No voice models available.")
            return
        
        print("\nAvailable voices:")
        for i, model in enumerate(models):
            print(f"{i+1}. {model['name']}")
        
        model_idx = int(input("Choose a voice (enter number): ")) - 1
        if 0 <= model_idx < len(models):
            text = input("Enter text to synthesize: ")
            try:
                result = client.synthesize_speech(
                    model_id=models[model_idx]["id"],
                    text=text
                )
                print("Speech synthesized successfully!")
            except Exception as e:
                print(f"Error: {e}")
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main() 