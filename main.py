"""
Main application for the English conversation assistant.
"""

import sys
from components.audio_recorder import AudioRecorder
from components.audio_transcriber import AudioTranscriber
from components.response_generator import ResponseGenerator
from components.speech_synthesizer import SpeechSynthesizer

import config


def main():
    """Main application entry point."""

    # Initialize components
    recorder = AudioRecorder()
    transcriber = AudioTranscriber()
    generator = ResponseGenerator()
    synthesizer = SpeechSynthesizer()

    print("English conversation assistant ready!")

    # Start conversation
    conversation = [{"role": "system", "content": config.SYSTEM_PROMPT}]

    try:
        while True:
            # Record user's speech
            audio_file = recorder.record()

            # Transcribe to text
            transcription = transcriber.transcribe(audio_file)
            text = transcription["text"]
            print(f"You said: {text}")

            # Detect low confidence words
            low_confidence_words = transcriber.get_low_confidence_words(transcription)
            if low_confidence_words:
                print(
                    f"Words that might be mispronounced: {', '.join(low_confidence_words)}"
                )
                text += f"\nNote: The following words were not clearly pronounced and understood: {', '.join(low_confidence_words)}"

            # Add to conversation history
            conversation.append(
                {
                    "role": "user",
                    "content": text,
                }
            )

            # Generate response
            print("Generating response...")
            response = generator.generate_response(conversation)
            conversation.append({"role": "assistant", "content": response})
            print(f"Assistant: {response}")

            # Speak the response
            print("Speaking...")
            synthesizer.speak(response)
    except KeyboardInterrupt:
        print("\nExiting application...")
        sys.exit(0)


if __name__ == "__main__":
    main()
