import runpod
from TTS.api import TTS
import os
import base64
import io
import time
import uuid

# Load the model once when the serverless function starts
#tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", gpu=True)
tts = TTS(model_name="tts_models/pt/cv/vits", gpu=True)

def text_to_speech(text, output_path="output.wav"):
    """
    Convert text to speech and return the audio as base64

    Args:
        text (str): The text to convert to speech
        output_path (str): The path where the temporary audio file will be saved

    Returns:
        str: Base64 encoded audio data
    """
    try:
        # Generate speech
        tts.tts_to_file(text=text, file_path=output_path)

        # Read the generated audio file and convert to base64
        with open(output_path, "rb") as audio_file:
            audio_data = audio_file.read()
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')

        return audio_base64

    finally:
        # Clean up the temporary file
        if os.path.exists(output_path):
            os.remove(output_path)

def handler(event):
    """
    RunPod handler function for processing TTS requests

    Expected input format:
    {
        "input": {
            "text": "Text to convert to speech"
        }
    }

    Returns:
        dict: Contains either the base64 encoded audio or an error message
    """
    try:
        # Get input text
        input_data = event["input"]
        text = input_data.get("text")

        if not text:
            return {"error": "No text provided for TTS conversion"}

        # Generate unique output path for concurrent requests
        unique_id = uuid.uuid4()
        output_path = f"/tmp/output_{unique_id}.wav"

        # Convert text to speech
        audio_base64 = text_to_speech(text, output_path)

        return {
            "output": {
                "audio_base64": audio_base64,
                "mime_type": "audio/wav"
            }
        }

    except Exception as e:
        return {"error": f"Error processing TTS request: {str(e)}"}

# Start the serverless handler
runpod.serverless.start({"handler": handler})
