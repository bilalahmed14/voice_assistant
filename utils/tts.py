import pyttsx3
import tempfile
import os

class TextToSpeech:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Speed of speech
        self.engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)

    def speak(self, text: str) -> str:
        # Create a temporary file for the audio
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            # Save the audio to the temporary file
            self.engine.save_to_file(text, temp_file.name)
            self.engine.runAndWait()
            
            # Return the path to the temporary file
            return temp_file.name 