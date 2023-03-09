import json
import os
import openai
from datetime import datetime, timedelta
import http.client, urllib.request, urllib.parse, urllib.error
from dotenv import load_dotenv
import asyncio

from azure.cognitiveservices.speech import (
    AudioDataStream,
    SpeechConfig,
    SpeechSynthesizer,
    SpeechSynthesisOutputFormat,
)
from azure.cognitiveservices.speech.audio import AudioOutputConfig
import azure.cognitiveservices.speech as speechsdk


def get_speech_keys():
    """Retrieve Keys for Azure Speech"""
    load_dotenv()

    key = os.getenv("SPEECH_KEY")
    region = os.getenv("SPEECH_LOCATION")

    return key, region

def get_openai_key():
    """Retrieve Keys for Open AI"""
    load_dotenv()

    key = os.getenv("OPENAI_KEY")

    return key

def speak(text):
    """Read out input text on the local system playback device
    Keyword arguments:
    text -- a string of text to be read
    """
    key, region = get_speech_keys()
    speech_config = SpeechConfig(subscription=key, region=region)
    speech_config.speech_synthesis_voice_name = "en-GB-RyanNeural"
    audio_config = AudioOutputConfig(use_default_speaker=True)
    synthesizer = SpeechSynthesizer(
        speech_config=speech_config, audio_config=audio_config
    )
    return synthesizer.speak_text(text)


def ask_openai_chat(chat_log):
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=chat_log
    )

    return str(response['choices'][0]['message']['content'])


def recognize_from_microphone():
    # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    key,region = get_speech_keys()
    speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
    speech_config.speech_recognition_language="en-US"

    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    print("Speak into your microphone.")
    speech_recognition_result = speech_recognizer.recognize_once_async().get()

    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Recognized: {}".format(speech_recognition_result.text))
    elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
    elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_recognition_result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
            print("Did you set the speech resource key and region values?")

    return speech_recognition_result.text

# Continuous loop starts here
run = True

openai.api_key = (get_openai_key())
user_chat = [{"role": "system", "content": "You are a helpful assistant. Keep responses short and chatty, keep it fun"}]

while run == True:

    user_chat.append({"role":"user","content":str(recognize_from_microphone())})

    response = ask_openai_chat(user_chat)
    speak(response)
    user_chat.append({"role":"system","content":response})

    if response == 'end chat':
        break

    continue