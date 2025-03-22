"""
Main application for the English conversation assistant.
"""

from flask import Flask, render_template, request, jsonify
import base64
from components.audio_transcriber import AudioTranscriber
from components.response_generator import ResponseGenerator
from components.speech_synthesizer import SpeechSynthesizer
import config

app = Flask(__name__)

# Initialize components
print("Initializing components...")
transcriber = AudioTranscriber()
generator = ResponseGenerator()
synthesizer = SpeechSynthesizer()

# Create an in-memory conversation history
conversation = [{"role": "system", "content": config.SYSTEM_PROMPT}]


@app.route("/")
def index():
    """Serve the main page."""
    return render_template("index.html")


@app.route("/api/process-audio", methods=["POST"])
def process_audio():
    """Process audio data and return AI response."""
    # Get audio data from request
    audio_data = request.json.get("audio")
    audio_binary = base64.b64decode(audio_data.split(",")[1])

    # Save audio to temporary file
    temp_file = "temp_recording.wav"
    with open(temp_file, "wb") as f:
        f.write(audio_binary)

    # Transcribe audio
    transcription = transcriber.transcribe(temp_file)
    text = transcription["text"]
    words_with_confidence = transcriber.extract_confidence(transcription)

    # Return transcription for display
    return jsonify(
        {"transcription": text, "wordsWithConfidence": words_with_confidence}
    )


@app.route("/api/generate-response", methods=["POST"])
def generate_response():
    """Generate AI response based on the transcription."""
    global conversation

    # Get transcription data
    data = request.json
    text = data.get("transcription")
    words_with_confidence = data.get("wordsWithConfidence", [])
    low_confidence_words = [
        word["word"] for word in words_with_confidence if word["is_low_confidence"]
    ]
    if low_confidence_words:
        user_content = f"{text}\nNote to the assistant: The following words were mispronounced and may have been mistranscribed: {', '.join(low_confidence_words)}"
    else:
        user_content = text

    conversation.append({"role": "user", "content": user_content})

    # Generate response
    response = generator.generate_response(conversation)
    conversation.append({"role": "assistant", "content": response})
    resp = jsonify({"response": response})

    # Synthesize speech
    @resp.call_on_close
    def on_close():
        synthesizer.speak(response)

    return resp


if __name__ == "__main__":
    app.run()
