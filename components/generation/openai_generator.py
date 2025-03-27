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
        system_content = config.REPHRASING_PROMPT
        if last_ai_response:
            system_content += (
                f'\nHere is the last AI response for context: "{last_ai_response}"'
            )

        prompt = [
            {
                "role": "system",
                "content": system_content,
            },
            {
                "role": "user",
                "content": text,
            },
        ]

        response = self.client.chat.completions.create(
            model=config.OPENAI_CHAT_MODEL,
            messages=prompt,
            max_tokens=config.MAX_NEW_TOKENS,
            response_format={"type": "json_object"},
        )

        response_text = response.choices[0].message.content
        return self.process_rephrase_response(response_text)
