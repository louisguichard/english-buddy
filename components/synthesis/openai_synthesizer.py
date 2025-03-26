"""
OpenAI speech synthesis module using OpenAI TTS API.
"""

import soundfile as sf
from openai import OpenAI
import config
from components.synthesis.synthesizer_base import SynthesizerBase


class OpenAISynthesizer(SynthesizerBase):
    """Class for text-to-speech conversion using OpenAI TTS API."""

    def __init__(self):
        """Initialize the OpenAI client."""
        print(f"Using {config.OPENAI_TTS_MODEL} API...")
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)

    def generate_audio(self, text):
        """
        Convert text to speech using OpenAI TTS API.

        Args:
            text (str): The text to convert to speech

        Returns:
            numpy.ndarray: The audio data
        """
        # Generate speech
        response = self.client.audio.speech.create(
            model=config.OPENAI_TTS_MODEL, voice=config.OPENAI_TTS_VOICE, input=text
        )

        # Save the audio to a temporary file
        temp_path = "temp_response.mp3"
        response.stream_to_file(temp_path)

        # Load the audio
        data, _ = sf.read(temp_path)
        return data
