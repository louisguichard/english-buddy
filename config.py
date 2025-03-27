"""
Configuration settings for the English assistant application.
"""

import os
import torch
import dotenv

dotenv.load_dotenv()


# Model provider
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "local")

# Local model settings
MODEL_ID = "meta-llama/Llama-3.2-3B-Instruct"
LOCAL_STT_SIZE = "base"  # "small", "tiny", "base"

# OpenAI settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_STT_MODEL = "whisper-1"
OPENAI_CHAT_MODEL = "gpt-4o-mini"
OPENAI_TTS_MODEL = "gpt-4o-mini-tts"

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
OPENAI_TTS_VOICE = "shimmer"
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

# Rephrasing prompt
REPHRASING_PROMPT = """
You are a helpful assistant for English learners. Assess if the user's text needs grammatical improvement. If it does, provide a corrected version that sounds more natural. If it's already grammatically correct and natural, indicate that no rephrasing is needed. Respond in a JSON format with two fields: "needs_rephrasing" (boolean) and "rephrased_text" (string, only include if rephrasing is needed).
"""

# Generation settings
MAX_NEW_TOKENS = 256
TEMPERATURE = 0.7
TOP_P = 0.9

# Confidence threshold for determining low confidence words
CONFIDENCE_THRESHOLD = 0.5
