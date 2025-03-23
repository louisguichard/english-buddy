"""
Response generator using Llama model.
"""

import os
import torch
from transformers import pipeline
import config


class ResponseGenerator:
    """Class for generating responses using the Llama model."""

    def __init__(self):
        """Initialize the Llama model."""
        self.device = config.DEVICE

        # Determine appropriate dtype
        if self.device in ["mps", "cuda"]:
            torch_dtype = torch.float16
        else:  # CPU
            torch_dtype = torch.float32

            # Optimize CPU performance
            if self.device == "cpu":
                torch.set_num_threads(os.cpu_count())
                print(f"Setting {os.cpu_count()} CPU threads for optimal performance")

        # Load the model
        print(f"Loading Llama model: {config.MODEL_ID}...")

        # Use pipeline for more efficient text generation
        self.pipe = pipeline(
            "text-generation",
            model=config.MODEL_ID,
            tokenizer=config.MODEL_ID,
            torch_dtype=torch_dtype,
            device_map="auto",
            token=os.getenv("HF_TOKEN"),
        )

    def generate_response(self, conversation):
        """
        Generate a response using the Llama model.

        Args:
            conversation (list of dict): List of conversation messages with 'role' and 'content' keys

        Returns:
            str: The generated response
        """
        response = self.pipe(
            conversation,
            max_new_tokens=config.MAX_NEW_TOKENS,
            temperature=config.TEMPERATURE,
            top_p=config.TOP_P,
            do_sample=True,
            eos_token_id=self.pipe.tokenizer.eos_token_id,
            return_full_text=False,
        )
        response_text = response[0]["generated_text"]

        return response_text

    def generate_word_definition(self, word, context):
        """
        Generate a definition for a word in its context.

        Args:
            word (str): The word to define
            context (str): The context in which the word appears (the full AI response)

        Returns:
            str: A simplified definition or explanation of the word
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

        response = self.pipe(
            prompt,
            max_new_tokens=config.MAX_NEW_TOKENS,
            temperature=config.TEMPERATURE,
            top_p=config.TOP_P,
            do_sample=True,
            eos_token_id=self.pipe.tokenizer.eos_token_id,
            return_full_text=False,
        )

        definition = response[0]["generated_text"]
        return definition.strip()
