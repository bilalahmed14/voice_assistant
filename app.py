import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import speech_recognition as sr
import pyttsx3
from utils.rag import RAGProcessor
from utils.stt import SpeechToText
from utils.tts import TextToSpeech
from utils.voice_cloner import VoiceCloner
import time
from gtts import gTTS
from pydub import AudioSegment
import io
import wave
import contextlib

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize components
rag_processor = RAGProcessor()
stt = SpeechToText()
tts = TextToSpeech()
voice_cloners = {
    'openai': VoiceCloner(tts_provider='openai'),
    'elevenlabs': VoiceCloner(tts_provider='elevenlabs')
}

def ensure_wav_format(input_path, output_path):
    """Convert audio to proper WAV format"""
    try:
        # Try to read the audio file
        audio = AudioSegment.from_file(input_path)
        # Export as WAV with specific parameters
        audio.export(output_path, format="wav", parameters=["-ac", "1", "-ar", "44100"])
        return True
    except Exception as e:
        print(f"Error converting audio: {str(e)}")
        return False

def process_audio(input_path, output_path):
    try:
        # First ensure we have a proper WAV file
        temp_wav = os.path.join('voice_samples', 'temp.wav')
        if not ensure_wav_format(input_path, temp_wav):
            raise Exception("Failed to convert audio to WAV format")

        # Load the audio file
        audio = AudioSegment.from_wav(temp_wav)
        
        # Apply some effects to make it sound different
        # Speed up slightly
        audio = audio.speedup(playback_speed=1.1)
        
        # Add slight echo effect
        echo = audio - 3
        audio = audio.overlay(echo, position=100)
        
        # Export the modified audio
        audio.export(output_path, format="wav", parameters=["-ac", "1", "-ar", "44100"])
        
        # Clean up temporary file
        if os.path.exists(temp_wav):
            os.remove(temp_wav)
            
        return True
    except Exception as e:
        print(f"Error processing audio: {str(e)}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/voice-assistant')
def voice_assistant():
    return render_template('voice_assistant.html')

@app.route('/voice-cloning')
def voice_cloning():
    return render_template('voice_cloning.html')

@app.route('/process_voice', methods=['POST'])
def process_voice():
    try:
        # Get audio file from request
        audio_file = request.files['audio']
        print(f"audio -->>> {audio_file}")
        
        # Convert speech to text
        text = stt.transcribe(audio_file)
        
        # Process question using RAG
        answer = rag_processor.get_answer(text)
        
        # Convert answer to speech
        audio_response = tts.speak(answer)
        
        return jsonify({
            'success': True,
            'question': text,
            'answer': answer,
            'audio_url': audio_response
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/process_voice_clone', methods=['POST'])
def process_voice_clone():
    try:
        # Get audio file and provider from request
        audio_file = request.files['audio']
        provider = request.form.get('provider', 'openai')
        
        if provider not in voice_cloners:
            raise Exception(f"Unsupported provider: {provider}")
        
        # Save the audio file
        audio_path = os.path.join('voice_samples', 'sample.wav')
        audio_file.save(audio_path)
        
        # Process the voice sample using selected provider
        if not voice_cloners[provider].process_voice_sample(audio_path):
            raise Exception(f"Failed to process voice sample using {provider}")
        
        return jsonify({
            'success': True,
            'message': 'Voice sample processed successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/verify_cloned_voice', methods=['POST'])
def verify_cloned_voice():
    try:
        # Get text and provider from request
        data = request.get_json()
        text = data.get('text')
        provider = data.get('provider', 'openai')
        
        print(f"Selected provider: {provider}")  # Debug log
        
        if not text:
            raise Exception("No text provided")
        
        if provider not in voice_cloners:
            raise Exception(f"Unsupported provider: {provider}")
        
        # Generate cloned voice
        output_path = voice_cloners[provider].generate_cloned_voice(text)
        if not output_path:
            raise Exception(f"Failed to generate cloned voice using {provider}")
        
        # Get the filename from the path
        output_filename = os.path.basename(output_path)
        
        return jsonify({
            'success': True,
            'audio_url': f'/static/{output_filename}'
        })
    except Exception as e:
        print(f"Error in verify_cloned_voice: {str(e)}")  # Debug log
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True) 