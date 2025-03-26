"""
Base class for audio transcription.
"""

from abc import ABC, abstractmethod


class TranscriberBase(ABC):
    """Abstract base class for transcribing speech to text."""

    def __init__(self):
        """Initialize the transcriber."""
        self.words = None

    @abstractmethod
    def transcribe(self, audio_file):
        """
        Transcribe an audio file to text.

        Args:
            audio_file (str): Path to the audio file

        Returns:
            str: The transcribed text
        """
        pass

    @abstractmethod
    def extract_words(self, transcription):
        """
        Extract words with their confidence scores and timing information.

        Args:
            transcription (dict): The transcription object

        Returns:
            list of dict: List of words with their confidence scores and positions
        """
        pass
