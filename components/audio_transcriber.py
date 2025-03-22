"""
Speech transcription module using Whisper.
"""

import whisper_timestamped as whisper
import config


class AudioTranscriber:
    """Class for transcribing speech to text using Whisper."""

    def __init__(self):
        """Initialize the Whisper model."""
        print("Loading Whisper model...")
        self.model = whisper.load_model("small")
        self.words = None

    def transcribe(self, audio_file):
        """
        Transcribe an audio file to text.

        Args:
            audio_file (str): Path to the audio file

        Returns:
            dict: The full transcription object
        """
        audio = whisper.load_audio(audio_file)
        transcription = whisper.transcribe(self.model, audio, language="en")
        return transcription

    def extract_words(self, transcription):
        """
        Extract words with their confidence scores and timing information.

        Args:
            transcription (dict): The Whisper transcription object

        Returns:
            list of dict: List of words with their confidence scores and positions
        """
        words_with_confidence = []
        position = 0

        for segment in transcription["segments"]:
            for word in segment["words"]:
                words_with_confidence.append(
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

        self.words = words_with_confidence
        return words_with_confidence
