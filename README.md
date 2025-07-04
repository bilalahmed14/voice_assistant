# AI Voice Assistant with Voice Cloning

DEMO = https://www.linkedin.com/posts/bilalahmed384_ai-voicetechnology-machinelearning-activity-7330209998641229824-f6am?utm_source=share&utm_medium=member_desktop&rcm=ACoAADGxNmwBZ_et5WuburdmkbQWuBUF_pyd-20

A powerful web application that combines an AI voice assistant with voice cloning capabilities. The application features two main components: an interactive voice assistant and a voice cloning studio.

## Features

### 1. Voice Assistant
- Real-time speech-to-text conversion
- Natural language processing with RAG (Retrieval-Augmented Generation)
- Text-to-speech response generation
- Interactive chat interface
- Quick-access suggestion chips for common queries
- Knowledge base management for custom information
- Keyboard shortcuts (spacebar for recording)

### 2. Voice Cloning Studio
- Support for multiple TTS providers (OpenAI and ElevenLabs)
- Voice sample recording and processing
- Custom voice generation
- Adjustable voice settings (style and speech rate)
- Real-time API verification
- Sample text for voice recording
- Audio playback for recorded and generated voices

## Setup

### Prerequisites
- Python 3.8 or higher
- Virtual environment (recommended)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd voice_assistant
```

2. Create and activate a virtual environment:
```bash
python -m venv appenv
# Windows
.\appenv\Scripts\activate
# Unix/MacOS
source appenv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up API keys:
Create a `.env` file in the root directory and add your API keys:
```env
OPENAI_API_KEY=your_openai_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
```

Alternatively, you can input the API keys directly in the voice cloning interface.

### Running the Application

1. Start the Flask server:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

### Voice Assistant
1. Click the microphone button or press spacebar to start recording
2. Speak your query clearly
3. Wait for the assistant's response
4. The response will be displayed in the chat and played back as audio

### Voice Cloning
1. Select your preferred TTS provider (OpenAI or ElevenLabs)
2. Enter your API key and verify the connection
3. Record a voice sample using the provided sample text
4. Process the voice sample
5. Test the cloned voice by entering custom text
6. Adjust voice settings as needed
7. Generate and play the cloned voice output

### Knowledge Base
- Upload text files (.txt or .md) to customize the assistant's knowledge
- The assistant will use this information to provide more accurate responses
- Supports context-aware responses using RAG technology


