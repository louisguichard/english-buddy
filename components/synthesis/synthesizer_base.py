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

    def speak(self, audio_data):
        """
        Play the audio data.

        Args:
            audio_data (numpy.ndarray): The audio data to play
        """
        sd.play(audio_data, samplerate=24000)
        sd.wait()
