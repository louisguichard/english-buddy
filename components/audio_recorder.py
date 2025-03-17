"""
Audio recorder module that handles recording speech from the microphone.
"""

import threading
import pyaudio
import wave


class AudioRecorder:
    """Class for recording audio from microphone."""

    def __init__(self):
        """Initialize audio recorder."""

    def record(self, filename="temp_recording.wav"):
        """
        Record audio from the microphone until Enter is pressed.

        Args:
            filename (str): Path to save the recording

        Returns:
            str: Path to the saved recording
        """
        # Initialize PyAudio
        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=44100,
            input=True,
            frames_per_buffer=1024,
        )

        frames = []
        recording = True

        def record_audio():
            while recording:
                data = stream.read(1024)
                frames.append(data)

        # Start recording in a separate thread
        print("Listening... Press Enter to stop.")
        record_thread = threading.Thread(target=record_audio)
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
            wf.setnchannels(1)
            wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b"".join(frames))

        return filename


# Simple usage example
if __name__ == "__main__":
    recorder = AudioRecorder()
    filename = recorder.record()
    print(f"Audio saved to: {filename}")
