import sounddevice as sd
import soundfile as sf
import numpy as np
import speech_recognition as sr
from io import BytesIO
import os

from openai import OpenAI

OpenAI.api_key = os.environ["OPENAI_API_KEY"]
client = OpenAI()

def get_prompt():
    audio_file = open("audio/input.mp3", "rb")
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        response_format="text"
    )
    return transcript



def get_input_file(threshold=0.15, silence_duration=1.5, max_duration=10):
    recognizer = sr.Recognizer()
    with sr.Microphone() as mic:
        print("Listening for speech...")
        # Adjust the recognizer sensitivity to ambient noise
        recognizer.adjust_for_ambient_noise(mic)
        started = False
        start_time = None
        last_time = None
        audio_frames = []

        recording = True

        def callback(indata, frames, time, status):
            nonlocal started, start_time, last_time, audio_frames, recording
            start_time = time.inputBufferAdcTime
            if np.any(indata > threshold):
                if not started:
                    print("Starting recording...")
                    started = True
                last_time = time.inputBufferAdcTime
            if started:
                audio_frames.append(indata.copy())
                if time.inputBufferAdcTime - last_time > silence_duration:
                    recording = False
                    print("Silence: Stopping recording...")
                    raise sd.CallbackAbort
            
            if time.inputBufferAdcTime - start_time > max_duration:
                recording = False
                print("Max duration reached: Stopping recording...")
                raise sd.CallbackAbort

        with sd.InputStream(callback=callback, channels=1):
            cnt = 0
            while True:
                if not recording:
                    break
                
                cnt += 1
                if cnt % 30000000 == 0:
                    cnt = 0
                    print("Still listening...")
            print("Stopped listening")            
                
        print("Processing")
        if audio_frames:
            audio_data = np.concatenate(audio_frames, axis=0)
            # print("Finished cat")
            with BytesIO() as f:
                sf.write(f, audio_data, samplerate=44100, format='WAV')
                f.seek(0)
                # print("Finished write")
                with sr.AudioFile(f) as source:
                    audio = recognizer.record(source)
                    # print("Finished record")
                    file_path = "audio/input.mp3"
                    # Remove the existing file if it exists
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    with open(file_path, "wb") as mp3_file:
                        mp3_file.write(audio.get_wav_data(convert_rate=16000, convert_width=2))
            print("Audio saved as input.mp3")
        else:
            print("No speech detected")
        return 1
    
    
get_input_file()
print(get_prompt())