# English Assistant

A web application for practicing English conversation skills. The application can use either local models or OpenAI APIs.

## Architecture

The application follows a modular architecture with three main component types:

1. **Transcription** - Convert speech to text (local Whisper small or OpenAI Whisper API)
2. **Generation** - Generate AI responses (local Llama 3.2 3B or OpenAI GPT-4o-mini API)
3. **Synthesis** - Convert text to speech (Local Kokoro TTS or OpenAI GPT-4o-mini-TTS API)


## Setup

### Prerequisites

A Hugging Face token with access to the Llama 3.2 model (if using local models) or an OpenAI API key (if using OpenAI APIs).

### Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:

If using local models:
```bash
export HF_TOKEN="your_huggingface_token"
```

If using OpenAI APIs:
```bash
export OPENAI_API_KEY="your_openai_api_key"
```

Note: You will have to choose your model provider by editing the `config.py` file.

3. Run the web application:
```bash
python app.py
```

Then open your browser and navigate to http://127.0.0.1:5000