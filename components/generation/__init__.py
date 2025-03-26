"""
Generation factory module.
"""

from components.generation.local_generator import LocalGenerator
from components.generation.openai_generator import OpenAIGenerator


def get_generator(model_provider="local"):
    """
    Factory function to get the appropriate generator.

    Args:
        model_provider (str): The model provider to use.

    Returns:
        GeneratorBase: An instance of a generator.
    """
    if model_provider == "openai":
        return OpenAIGenerator()
    else:
        return LocalGenerator()
