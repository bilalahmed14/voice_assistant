# Voice Cloning MCP Server

A voice cloning system that allows users to clone voices and generate speech using the cloned voices through an MCP (Media Control Protocol) server.

## Features

- Voice enrollment and model creation
- Text-to-Speech with cloned voices
- MCP server integration
- Voice model management

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install additional system dependencies:
- FFmpeg
- PortAudio

## Project Structure

```
voice_cloning/
├── src/
│   ├── core/           # Core voice cloning functionality
│   ├── mcp/            # MCP server implementation
│   ├── tools/          # MCP tools (Voice Enrollment, TTS)
│   └── utils/          # Utility functions
├── models/             # Pre-trained models and voice models
├── tests/              # Test files
└── docs/               # Documentation
```

## Usage

1. Start the MCP server:
```bash
python src/mcp/server.py
```

2. Use the MCP client to interact with the server:
```bash
python src/mcp/client.py
```

## License

MIT License 