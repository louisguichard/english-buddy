"""
Local speech synthesis module using Kokoro TTS.
"""

import numpy as np
from kokoro import KPipeline
import config
from components.synthesis.synthesizer_base import SynthesizerBase


class LocalSynthesizer(SynthesizerBase):
    """Class for text-to-speech conversion using local Kokoro TTS."""

    def __init__(self):
        """Initialize the local TTS engine."""
        print("Loading local TTS model...")
        self.tts_pipeline = KPipeline(lang_code="a")

    def generate_audio(self, text):
        """
        Convert text to speech using local Kokoro TTS.

        Args:
            text (str): The text to convert to speech

        Returns:
            numpy.ndarray: The audio data
        """
        generator = self.tts_pipeline(
            text, voice=config.TTS_VOICE, speed=config.TTS_SPEED, split_pattern=r"\n+"
        )

        speech_segments = []
        for _, _, audio in generator:
            speech_segments.append(audio)

        speech_output = (
            np.concatenate(speech_segments)
            if len(speech_segments) > 1
            else speech_segments[0]
        )

        return speech_output
