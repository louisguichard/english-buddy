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
