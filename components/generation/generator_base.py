"""
Base class for response generation.
"""

from abc import ABC, abstractmethod
import json


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

    @abstractmethod
    def generate_rephrase(self, text, last_ai_response=None):
        """
        Generate a rephrased version of the user's text that is more grammatically correct.

        Args:
            text (str): The user's text to rephrase
            last_ai_response (str, optional): The last AI response for context

        Returns:
            dict: {
                'needs_rephrasing': bool - whether the text needs rephrasing
                'rephrased_text': str - the rephrased text (if needed)
            }
        """
        pass

    def process_rephrase_response(self, response_text):
        """
        Process and parse rephrasing response in a robust way.

        Args:
            response_text (str): The raw response text from the model

        Returns:
            dict: {
                'needs_rephrasing': bool - whether the text needs rephrasing
                'rephrased_text': str - the rephrased text (if needed)
            }
        """
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            print(f"Error in rephrasing response: {response_text}")
            return {"needs_rephrasing": False}
