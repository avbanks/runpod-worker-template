import runpod
from TTS.api import TTS
import os
import base64
import io

# If your handler runs inference on a model, load the model here.
# You will want models to be loaded into memory before starting serverless.
tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", gpu=True)

def text_to_speech(text, output_path="output.wav"):
    """Convert text to speech and return the audio as base64"""
    # Generate speech
    tts.tts_to_file(text=text, file_path=output_path)

    # Read the generated audio file and convert to base64
    with open(output_path, "rb") as audio_file:
        audio_data = audio_file.read()
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')

    # Clean up the temporary file
    os.remove(output_path)

    return audio_base64

#def handler(job):
#    """ Handler function that will be used to process jobs. """
#    job_input = job['input']
#
#    name = job_input.get('name', 'World')
#
#    return f"Hello, {name}!"

def handler(event):
    """
    RunPod handler function for processing TTS requests

    Expected input format:
    {
        "input": {
            "text": "Text to convert to speech",
            "language": "en"  # optional, defaults to English
        }
    }
    """
    try:
        # Get input text
        input_data = event["input"]
        text = input_data.get("text")

        if not text:
            return {
                "error": "No text provided for TTS conversion"
            }

        # Generate unique output path for concurrent requests
        output_path = f"/tmp/output_{time.time()}.wav"

        # Convert text to speech
        audio_base64 = text_to_speech(text, output_path)

        return {
            "output": {
                "audio_base64": audio_base64,
                "mime_type": "audio/wav"
            }
        }

    except Exception as e:
        return {
            "error": f"Error processing TTS request: {str(e)}"
        }

runpod.serverless.start({"handler": handler})
