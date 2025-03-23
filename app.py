"""
Main application for the English conversation assistant.
"""

from flask import Flask, render_template, request, jsonify, send_file
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

# AI is speaking flag
speaking = False


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
    words = transcriber.extract_words(transcription)

    # Return transcription for display
    return jsonify({"transcription": text, "words": words})


@app.route("/api/generate-response", methods=["POST"])
def generate_response():
    """Generate AI response based on the transcription."""
    global conversation

    # Get transcription data
    data = request.json
    text = data.get("transcription")
    low_confidence_words = [
        word["word"] for word in transcriber.words if word["is_low_confidence"]
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
        global speaking
        speaking = True
        synthesizer.speak(response)
        speaking = False

    return resp


@app.route("/api/play-user-word", methods=["POST"])
def play_user_word():
    """Play a specific user word from the last recording."""

    # Get word position from client
    data = request.json
    word_info = data.get("wordInfo")
    position = word_info.get("position")

    # Find word segment
    word_segment = None
    for word_data in transcriber.words:
        if word_data["position"] == position:
            buffer = 0.2  # 200ms buffer
            word_segment = {
                "word": word_data["word"],
                "start": word_data["start"] - buffer,
                "end": word_data["end"] + 2 * buffer,
            }
            break

    if word_segment:
        return jsonify({"success": True, "word_segment": word_segment})
    else:
        return jsonify({"error": "Word segment not found"}), 404


@app.route("/api/play-ai-word", methods=["POST"])
def play_ai_word():
    """Synthesize and play a specific AI word."""
    global speaking
    if not speaking:
        data = request.json
        word = data.get("word")
        speaking = True
        synthesizer.speak(word)
        speaking = False
        return jsonify({"success": True})
    else:
        return jsonify({"error": "AI is already speaking"}), 400


@app.route("/api/get-word-definition", methods=["POST"])
def get_word_definition():
    """Get a definition for a specific word in context."""
    data = request.json
    word = data.get("word")
    context = data.get("context")
    definition = generator.generate_word_definition(word, context)
    return jsonify({"definition": definition})


@app.route("/temp_recording.wav")
def serve_recording():
    """Serve the temporary recording file."""
    return send_file("temp_recording.wav", mimetype="audio/wav")


if __name__ == "__main__":
    app.run()
