"""
OpenAI speech transcription module using OpenAI Whisper API.
"""

from openai import OpenAI
import config
from components.transcription.transcriber_base import TranscriberBase


class OpenAITranscriber(TranscriberBase):
    """Class for transcribing speech to text using OpenAI Whisper API."""

    def __init__(self):
        """Initialize the OpenAI client."""
        super().__init__()
        print(f"Using OpenAI {config.OPENAI_STT_MODEL} API...")
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.transcription = None
        self.word_position = 0

    def transcribe(self, audio_file):
        """
        Transcribe an audio file to text using OpenAI API.

        Args:
            audio_file (str): Path to the audio file

        Returns:
            str: The transcribed text
        """
        with open(audio_file, "rb") as audio:
            # Get word-level timestamps with verbose_json format
            self.transcription = self.client.audio.transcriptions.create(
                file=audio,
                model=config.OPENAI_STT_MODEL,
                response_format="verbose_json",
                timestamp_granularities=["word"],
                language="en",
            )
            return self.transcription.text

    def extract_words(self):
        """
        Extract words with their confidence scores and timing information.

        Returns:
            list of dict: List of words with their confidence scores and positions
        """
        self.words = []

        for position, word in enumerate(self.transcription.words):
            self.words.append(
                {
                    "word": word["word"],
                    "confidence": 1,  # confidence is not available using this model
                    "is_low_confidence": False,
                    "position": position,
                    "start": word["start"],
                    "end": word["end"],
                }
            )
        return self.words
