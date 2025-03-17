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
        self.model = whisper.load_model("tiny")

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

    def extract_confidence(self, transcription):
        """
        Extract confidence scores for each word in the transcription.

        Args:
            transcription (dict): The Whisper transcription object

        Returns:
            list of dict: List of words with their confidence scores
        """
        words_with_confidence = []
        for segment in transcription["segments"]:
            for word in segment["words"]:
                words_with_confidence.append(
                    {
                        "word": word["text"],
                        "confidence": word["confidence"],
                        "is_low_confidence": word["confidence"]
                        < config.CONFIDENCE_THRESHOLD,
                    }
                )
        return words_with_confidence

    def get_low_confidence_words(self, transcription):
        """
        Get a list of words with low confidence scores.

        Args:
            transcription (dict): The Whisper transcription object

        Returns:
            list of str: List of low confidence words
        """
        words_with_confidence = self.extract_confidence(transcription)
        return [
            word["word"] for word in words_with_confidence if word["is_low_confidence"]
        ]
