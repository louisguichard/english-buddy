"""
Local speech transcription module using Whisper.
"""

import whisper_timestamped as whisper
import config
from components.transcription.transcriber_base import TranscriberBase


class LocalTranscriber(TranscriberBase):
    """Class for transcribing speech to text using local Whisper model."""

    def __init__(self):
        """Initialize the local Whisper model."""
        super().__init__()
        print("Loading local Whisper model...")
        self.model = whisper.load_model(config.LOCAL_STT_SIZE)
        self.transcription = None
        self.words = None

    def transcribe(self, audio_file):
        """
        Transcribe an audio file to text using local Whisper.

        Args:
            audio_file (str): Path to the audio file

        Returns:
            str: The transcribed text
        """
        audio = whisper.load_audio(audio_file)
        self.transcription = whisper.transcribe(self.model, audio, language="en")
        return self.transcription["text"]

    def extract_words(self):
        """
        Extract words with their confidence scores and timing information.

        Returns:
            list of dict: List of words with their confidence scores and positions
        """
        self.words = []
        position = 0

        for segment in self.transcription["segments"]:
            for word in segment["words"]:
                self.words.append(
                    {
                        "word": word["text"],
                        "confidence": word["confidence"],
                        "is_low_confidence": word["confidence"]
                        < config.CONFIDENCE_THRESHOLD,
                        "position": position,
                        "start": word["start"],
                        "end": word["end"],
                    }
                )
                position += 1

        return self.words
