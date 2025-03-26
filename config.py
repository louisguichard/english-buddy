"""
Configuration settings for the English assistant application.
"""

import os
import torch


# Model provider setting
MODEL_PROVIDER = "local"  # "local" or "openai"

# Model settings
MODEL_ID = "meta-llama/Llama-3.2-3B-Instruct"

# OpenAI settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_STT_MODEL = "whisper-1"

# Device settings
DEVICE = (
    "cuda"
    if torch.cuda.is_available()
    else "mps"
    if torch.backends.mps.is_available()
    else "cpu"
)

# TTS settings
TTS_VOICE = "af_heart"
TTS_SPEED = 1.0

# System prompt for AI assistant
SYSTEM_PROMPT = """You are a friendly AI assistant having a casual spoken conversation with the user in English. Main goals:
- Keep responses informal, clear, and conversational—no formatting.
- Help the user improve spoken English by gently correcting mistakes and suggesting natural expressions. Be concise and direct in corrections.
- Occasionally and proactively ask the user to repeat words or phrases for pronunciation practice if they are not pronounced correctly.
- You can suggest rephrasing if appropriate.
- Keep interactions very concise, supportive, and enjoyable. Avoid being overly repetitive in corrections.
Remember this is an oral conversation, so what you get is a transcription of the conversation, not a text written by the user.
"""

# Generation settings
MAX_NEW_TOKENS = 256
TEMPERATURE = 0.7
TOP_P = 0.9

# Confidence threshold for determining low confidence words
CONFIDENCE_THRESHOLD = 0.5
