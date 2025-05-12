import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import speech_recognition as sr
import pyttsx3
from utils.rag import RAGProcessor
from utils.stt import SpeechToText
from utils.tts import TextToSpeech

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize components
rag_processor = RAGProcessor()
stt = SpeechToText()
tts = TextToSpeech()

@app.route('/')
def index():
    return render_template('index.html')

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

if __name__ == '__main__':
    app.run(debug=True) 