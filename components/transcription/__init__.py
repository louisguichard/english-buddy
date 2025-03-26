"""
Transcription factory module.
"""

from components.transcription.local_transcriber import LocalTranscriber
from components.transcription.openai_transcriber import OpenAITranscriber


def get_transcriber(model_provider="local"):
    """
    Factory function to get the appropriate transcriber.

    Args:
        model_provider (str): The model provider to use.

    Returns:
        TranscriberBase: An instance of a transcriber.
    """
    if model_provider == "openai":
        return OpenAITranscriber()
    else:
        return LocalTranscriber()
