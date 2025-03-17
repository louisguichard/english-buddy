"""
Speech synthesis module using Kokoro TTS.
"""

import numpy as np
import sounddevice as sd
from kokoro import KPipeline
import config


class SpeechSynthesizer:
    """Class for text-to-speech conversion."""

    def __init__(self):
        """Initialize the TTS engine."""
        print("Loading TTS model...")
        self.tts_pipeline = KPipeline(lang_code="a")

    def speak(self, text):
        """
        Convert text to speech and play it.

        Args:
            text (str): The text to speak
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

        # Play the audio
        sd.play(speech_output, samplerate=24000)
        sd.wait()
