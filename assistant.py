import os
import threading
import numpy as np
import torch
import pyaudio
import wave
import sounddevice as sd
from transformers import AutoModelForCausalLM, AutoTokenizer
import whisper_timestamped as whisper
from kokoro import KPipeline


device = (
    "cuda"
    if torch.cuda.is_available()
    else "mps"
    if torch.backends.mps.is_available()
    else "cpu"
)
print(f"Using device: {device}")

# Whisper model
print("Loading Whisper model...")
whisper_model = whisper.load_model("tiny")

# Llama model
print("Loading Llama model...")
llama_tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-3B-Instruct")
llama_model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.2-3B-Instruct",
    token=os.getenv("HF_TOKEN"),
).to(device)

# Kokoro TTS model
print("Loading Kokoro TTS model...")
kokoro_pipeline = KPipeline(lang_code="a")


def record_audio(filename="temp_recording.wav"):
    """Record audio from the microphone until Enter is pressed"""
    # Recording parameters
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024

    # Initialize PyAudio
    audio = pyaudio.PyAudio()
    stream = audio.open(
        format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK
    )

    frames = []
    recording = True

    def record():
        while recording:
            data = stream.read(CHUNK)
            frames.append(data)

    # Start recording in a separate thread
    print("Listening... Press Enter to stop.")
    record_thread = threading.Thread(target=record)
    record_thread.start()

    # Wait for user to press Enter
    input()
    recording = False

    # Wait for the recording thread to finish
    record_thread.join()

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save the recorded data to a WAV file
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b"".join(frames))

    return filename


def transcribe_audio(audio_file):
    """Transcribe audio file to text using Whisper"""
    audio = whisper.load_audio(audio_file)
    transcription = whisper.transcribe(whisper_model, audio, language="en")
    return transcription, transcription["text"]


def extract_confidence(transcription):
    """Extract confidence from transcription"""
    words_with_confidence = []
    for segment in transcription["segments"]:
        for word in segment["words"]:
            words_with_confidence.append(
                {
                    "word": word["text"],
                    "confidence": word["confidence"],
                    "is_low_confidence": word["confidence"] < 0.4,
                }
            )
    return words_with_confidence


def generate_response(conversation_history):
    """Generate response using Llama 3.2"""

    system_prompt = """You are a friendly AI assistant having a casual spoken conversation with the user in English. Main goals:
- Keep responses informal, clear, and conversational—no formatting.
- Help the user improve spoken English by gently correcting mistakes and suggesting natural expressions.
- Occasionally ask the user to repeat words they've mispronounced to practice pronunciation.

Example:
User: "I yesterday go cinema and watched good movie."
AI: "Nice! Yesterday you went to the cinema and watched a good movie? What movie did you see?"

Always keep interactions concise, supportive, and enjoyable."""

    # Build prompt
    prompt = f"<|system|>\n{system_prompt}\n"
    for message in conversation_history:
        role = message["role"]
        content = message["content"]

        if role == "user":
            prompt += f"<|user|>\n{content}\n"
            # Add information about low confidence words if available
            if message["low_confidence"]:
                low_confidence_words = ", ".join(
                    [f"'{word}'" for word in message["low_confidence"]]
                )
                prompt += f"Note: The following words were not clearly pronounced: {low_confidence_words}]\n"
        elif role == "assistant":
            prompt += f"<|assistant|>\n{content}\n"
    prompt += "<|assistant|>"

    # Generate response
    inputs = llama_tokenizer(prompt, return_tensors="pt").to(device)
    output = llama_model.generate(
        **inputs, max_new_tokens=256, temperature=0.7, top_p=0.9, do_sample=True
    )
    response_text = llama_tokenizer.decode(output[0], skip_special_tokens=True)
    response_text = response_text.split("<|assistant|>")[-1].strip()

    return response_text


def speak_text(text):
    """Convert text to speech using Kokoro TTS"""
    generator = kokoro_pipeline(text, voice="af_heart", speed=1, split_pattern=r"\n+")

    speech_segments = []
    for _, _, audio in generator:
        speech_segments.append(audio)

    speech_output = (
        np.concatenate(speech_segments)
        if len(speech_segments) > 1
        else speech_segments[0]
    )

    # Play the audio
    sd.play(speech_output, samplerate=24000)
    sd.wait()


def main():
    conversation_history = []

    while True:
        try:
            # Record user's speech
            audio_file = record_audio()

            # Transcribe to text
            print("Processing...")
            transcription, transcription_text = transcribe_audio(audio_file)

            # Extract words with low confidence
            words_with_confidence = extract_confidence(transcription)
            low_confidence_words = [
                word["word"]
                for word in words_with_confidence
                if word["is_low_confidence"]
            ]

            conversation_history.append(
                {
                    "role": "user",
                    "content": transcription_text,
                    "low_confidence": low_confidence_words,
                }
            )
            print(f"You said: {transcription_text}")

            if low_confidence_words:
                print(f"Low confidence words: {', '.join(low_confidence_words)}")

            # Generate response
            response = generate_response(conversation_history)
            conversation_history.append({"role": "assistant", "content": response})
            print(f"Assistant: {response}")

            # Speak the response
            print("Speaking...")
            speak_text(response)

        except KeyboardInterrupt:
            print("\nExiting...")
            break


if __name__ == "__main__":
    main()
