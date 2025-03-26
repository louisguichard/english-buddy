"""
Base class for response generation.
"""

from abc import ABC, abstractmethod


class GeneratorBase(ABC):
    """Abstract base class for generating responses."""

    @abstractmethod
    def generate_response(self, conversation):
        """
        Generate a response using a language model.

        Args:
            conversation (list of dict): List of conversation messages with 'role' and 'content' keys

        Returns:
            str: The generated response
        """
        pass

    @abstractmethod
    def generate_word_definition(self, word, context):
        """
        Generate a definition for a word in its context.

        Args:
            word (str): The word to define
            context (str): The context in which the word appears (the full AI response)

        Returns:
            str: A simplified definition of the word
        """
        pass
