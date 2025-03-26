"""
OpenAI response generation using the OpenAI API.
"""

from openai import OpenAI
import config
from components.generation.generator_base import GeneratorBase


class OpenAIGenerator(GeneratorBase):
    """Class for generating responses using OpenAI models."""

    def __init__(self):
        """Initialize the OpenAI client."""
        print(f"Using OpenAI {config.OPENAI_CHAT_MODEL} API...")
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)

    def generate_response(self, conversation):
        """
        Generate a response using the OpenAI chat API.

        Args:
            conversation (list of dict): List of conversation messages with 'role' and 'content' keys

        Returns:
            str: The generated response
        """
        response = self.client.chat.completions.create(
            model=config.OPENAI_CHAT_MODEL,
            messages=conversation,
            max_tokens=config.MAX_NEW_TOKENS,
        )
        return response.choices[0].message.content

    def generate_word_definition(self, word, context):
        """
        Generate a definition for a word in its context.

        Args:
            word (str): The word to define
            context (str): The context in which the word appears (the full AI response)

        Returns:
            str: A simplified definition of the word
        """
        prompt = [
            {
                "role": "system",
                "content": "You are a helpful assistant that provides simple, clear definitions of words in context.",
            },
            {
                "role": "user",
                "content": f'Define the word "{word}" as it is used in this context: "{context}". Keep the definition concise, at most 2 short sentences. Focus on how the word is used in this specific context. Use simple language suitable for English learners.',
            },
        ]

        response = self.client.chat.completions.create(
            model=config.OPENAI_CHAT_MODEL,
            messages=prompt,
            max_tokens=config.MAX_NEW_TOKENS,
        )

        return response.choices[0].message.content
