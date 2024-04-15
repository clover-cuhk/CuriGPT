import sounddevice as sd
import soundfile as sf
from scipy.io.wavfile import write
import numpy as np
import os
from pynput import keyboard
from pydub import AudioSegment
from pydub.playback import play
import openai
from openai import OpenAI

# Load your OpenAI API key from an environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI()
user_input_filename = '/home/zhuoli/CuriGPT/assets/chat_audio/user_input.wav'
curigpt_output_filename = 'assets/chat_audio/curigpt_output.mp3'


def record_audio_test():
    duration = 5  # 录制时长（秒）
    sample_rate = 16000  # 采样率

    # 录制麦克风音频
    print(f"开始录音，请说话...(时长为{duration}秒)")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
    sd.wait()
    sf.write(user_input_filename, audio, sample_rate)



# def record_audio(sample_rate=44100, duration=5):
#     print(sd.query_devices())
#
#     device_index = 0
#
#     # Variable to keep track of whether recording is active
#     is_recording = False
#     # Create a numpy array to store the recorded audio data
#     # audio_frames = np.zeros((int(sample_rate * duration), 1), dtype='float32')
#
#
#     # Define the callback function for key press
#     def on_press(key):
#         nonlocal is_recording, audio_frames
#         if key == keyboard.Key.enter and not is_recording:
#             is_recording = True
#             print("Recording... Release 'Enter' to stop.")
#             # Start non-blocking recording
#             sd.rec(samplerate=sample_rate, channels=1, dtype='float32', out=audio_frames, blocking=True)
#             # audio_frames = sd.rec(duration * sample_rate, samplerate=sample_rate, channels=1, dtype='float32', blocking=False, device_index=device_index)
#             # print("audio_frames", audio_frames)
#         else:
#             print("Recording is already in progress...")
#
#     # Define the callback function for key release
#     def on_release(key):
#         nonlocal is_recording
#         if key == keyboard.Key.enter and is_recording:
#             # Stop recording
#             sd.stop()
#             is_recording = False
#             print("Recording stopped.")
#             # write(user_input_filename, sample_rate, audio_frames)
#             sf.write(user_input_filename, audio_frames, sample_rate)
#
#             print("Audio saved as output.wav")
#             return False  # Return False to stop the listener
#
#     # Set up the listener for keyboard events
#     with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
#         print("Press 'Enter' to start recording...")
#         listener.join()

def transcribe_audio():
    '''
    Transcribe the audio file using OpenAI's Whisper model
    '''
    audio_file = open(user_input_filename, "rb")
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        response_format="text",
        file=audio_file
    )
    # model =whisper-1
    # response = requests.post('https://api.openai.com/v1/audio/transcriptions', files=files, headers={'Authorization': f'Bearer {openai.api_key}'})
    # transcription = response.json()['text']
    print("Transcription:", transcription.text)
    return transcription.text

def generate_response(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": text}]
    )
    return response.choices[0].message['content']

def text_to_speech(text):
    # response = requests.post('https://api.openai.com/v1/audio/speech', headers={'Authorization': f'Bearer {openai.api_key}'}, json={'model': 'tts-1', 'text': text})
    # audio_content = response.content
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text,
    )

    response.stream_to_file(curigpt_output_filename)
    # with open('response.mp3', 'wb') as audio:
    #     audio.write(audio_content)
    sound = AudioSegment.from_mp3(curigpt_output_filename)
    play(sound)

def main():
    record_audio()
    transcription = transcribe_audio()
    response_text = generate_response(transcription)
    print("Assistant Response:", response_text)
    text_to_speech(response_text)

if __name__ == '__main__':
    # main()
    # record_audio()
    record_audio_test()