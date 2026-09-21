import os
import azure.cognitiveservices.speech as speechsdk


def speech_to_text(audio_file):

    speech_config = speechsdk.SpeechConfig(
        subscription=os.environ["SPEECH_KEY"],
        region=os.environ["SPEECH_REGION"]
    )

    audio_config = speechsdk.audio.AudioConfig(
        filename=audio_file
    )

    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        audio_config=audio_config
    )

    result = recognizer.recognize_once()

    print("Speech result reason:", result.reason)

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Recognized text:", result.text)
        return result.text

    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("Azure could not recognize the speech.")
        return ""

    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation = result.cancellation_details
        print("Speech recognition canceled.")
        print("Reason:", cancellation.reason)
        print("Error details:", cancellation.error_details)
        return ""

    return ""