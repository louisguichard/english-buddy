"""
Synthesis factory module.
"""

from components.synthesis.local_synthesizer import LocalSynthesizer
from components.synthesis.openai_synthesizer import OpenAISynthesizer


def get_synthesizer(model_provider="local"):
    """
    Factory function to get the appropriate synthesizer.

    Args:
        model_provider (str): The model provider to use.

    Returns:
        SynthesizerBase: An instance of a synthesizer.
    """
    if model_provider == "openai":
        return OpenAISynthesizer()
    else:
        return LocalSynthesizer()
