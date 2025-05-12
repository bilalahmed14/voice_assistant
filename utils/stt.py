import speech_recognition as sr
import tempfile
import os
import subprocess

class SpeechToText:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def transcribe(self, audio_file) -> str:
        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_file:
            audio_file.save(temp_file.name)
            temp_file.close()  # Ensure the file is closed
            
            # Convert WebM to WAV using ffmpeg
            wav_file = temp_file.name.replace('.webm', '.wav')
            try:
                subprocess.run([
                    'ffmpeg', '-i', temp_file.name,
                    '-acodec', 'pcm_s16le',
                    '-ar', '44100',
                    '-ac', '1',
                    wav_file
                ], check=True, capture_output=True)
                
                # Use the WAV file for recognition
                with sr.AudioFile(wav_file) as source:
                    audio_data = self.recognizer.record(source)
                    try:
                        text = self.recognizer.recognize_google(audio_data)
                        return text
                    except sr.UnknownValueError:
                        raise ValueError("Could not understand audio")
                    except sr.RequestError as e:
                        raise ValueError(f"Could not request results; {str(e)}")
            finally:
                # Clean up temporary files
                os.unlink(temp_file.name)
                if os.path.exists(wav_file):
                    os.unlink(wav_file) 