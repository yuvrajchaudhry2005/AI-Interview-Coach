import os
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk

# Load environment variables if available
load_dotenv()


def speech_to_text_detailed(audio_file, speech_key=None, speech_region=None):
    """
    Converts audio file to text.
    First attempts Azure Cognitive Services Speech if credentials are provided.
    If Azure credentials are not available or fail, gracefully falls back to local Google STT
    via speech_recognition so voice input never fails during demo.
    """
    key = speech_key or os.environ.get("SPEECH_KEY")
    region = speech_region or os.environ.get("SPEECH_REGION")

    # 1. Try Azure Speech SDK if credentials exist
    if key and region and key.strip() and region.strip():
        try:
            speech_config = speechsdk.SpeechConfig(
                subscription=key.strip(),
                region=region.strip()
            )
            audio_config = speechsdk.audio.AudioConfig(
                filename=audio_file
            )
            recognizer = speechsdk.SpeechRecognizer(
                speech_config=speech_config,
                audio_config=audio_config
            )

            result = recognizer.recognize_once()

            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                return result.text, None, "Azure Cognitive Speech"

            elif result.reason == speechsdk.ResultReason.NoMatch:
                return "", "No speech recognized. Please speak clearly into your mic.", "Azure Cognitive Speech"

            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation = result.cancellation_details
                err = cancellation.error_details or cancellation.reason
                print(f"Azure Speech canceled: {err}. Attempting fallback...")

        except Exception as e:
            print(f"Azure Speech error: {e}. Attempting fallback...")

    # 2. Smart Fallback via speech_recognition
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio_data = r.record(source)
        text = r.recognize_google(audio_data)
        return text, None, "Speech Recognizer"
    except Exception as fallback_err:
        return "", f"Speech recognition failed: {fallback_err}", None


def speech_to_text(audio_file, speech_key=None, speech_region=None):
    """Convenience wrapper returning transcribed text directly."""
    text, _, _ = speech_to_text_detailed(audio_file, speech_key, speech_region)
    return text