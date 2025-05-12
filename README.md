# Voice-Based AI Agent with RAG

This project demonstrates a voice-based AI agent that can answer questions based on a provided knowledge base using Retrieval-Augmented Generation (RAG).

## Features

- Voice input (Speech-to-Text)
- Knowledge base integration with vector embeddings
- RAG-based question answering
- Voice output (Text-to-Speech)
- Modern web interface

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
4. Place your knowledge base documents in the `knowledge_base` directory
5. Run the application:
   ```bash
   python app.py
   ```

## Usage

1. Open your web browser and navigate to `http://localhost:5000`
2. Click the microphone button to start recording your question
3. Wait for the system to process your question and provide a voice response
4. The transcribed question and answer will be displayed on the screen

## Project Structure

- `app.py`: Main Flask application
- `knowledge_base/`: Directory for knowledge base documents
- `static/`: Static files (CSS, JavaScript)
- `templates/`: HTML templates
- `utils/`: Utility functions for RAG, STT, and TTS 