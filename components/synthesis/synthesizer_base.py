"""
Base class for speech synthesis.
"""

from abc import ABC, abstractmethod
import sounddevice as sd


class SynthesizerBase(ABC):
    """Abstract base class for text-to-speech conversion."""

    @abstractmethod
    def generate_audio(self, text):
        """
        Convert text to speech.

        Args:
            text (str): The text to speak

        Returns:
            numpy.ndarray: The audio data
        """
        pass

    def speak(self, text):
        """
        Convert text to speech and play it.

        Args:
            text (str): The text to speak
        """
        audio_data = self.generate_audio(text)
        sd.play(audio_data, samplerate=24000)
        sd.wait()
