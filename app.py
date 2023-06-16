import io

import speech_recognition as sr
import whisper
import torch

from datetime import datetime, timedelta
from tempfile import NamedTemporaryFile
from time import sleep

from queue import Queue
import multiprocessing as mp

from utils.utils import clear_queue
from ui import lang_net_ui

import os
# Add bin/ffmpeg/ to the path.
os.environ['PATH'] += os.pathsep + os.path.dirname(os.path.realpath(__file__)) + '/bin/ffmpeg/'

def main(model_queue, load_event, language_queue, translation_queue, clear_event, text_queue):
    # Create a recognizer instance.
    recorder = sr.Recognizer()
    recorder.energy_threshold = 1000
    recorder.dynamic_energy_threshold = False

    record_timeout = 2
    phrase_timeout = 3
    
    # Create a microphone instance.
    source = sr.Microphone(sample_rate=16000)

    # Wait for the model load button to be pressed.
    while not load_event.is_set():
        #print("Waiting for load event...")
        sleep(0.5)
    load_event.clear()    

    # Clear the text queue and add a loading message.
    clear_queue(text_queue)
    text_queue.put(["Loading, please wait..."])

    # Load/Download the model
    model = model_queue.get()
    print("Loading model: " + model)
    audio_model = whisper.load_model(model)

    #temp_file = NamedTemporaryFile().name
    temp_file = "temp/temp"
    transcription = ['']

    with source:
        recorder.adjust_for_ambient_noise(source)

    data_queue = Queue() # Thread safe Queue for passing data from the threaded recording callback.
    def record_callback(_, audio:sr.AudioData) -> None:
        data = audio.get_raw_data()
        data_queue.put(data)

    # Start listening in the background.
    recorder.listen_in_background(source, record_callback, phrase_time_limit=record_timeout)

    # Clear the text queue and add a loading message.
    clear_queue(text_queue)
    text_queue.put(["Loading complete."]) 

    language = language_queue.get() # Get the current language from the queue.
    translator = translation_queue.get() # Get the current translator from the queue.

    phrase_time = None
    last_sample = bytes()

    while True:
        try:
            now = datetime.utcnow()
            if not data_queue.empty():
                phrase_complete = False
                if phrase_time and now - phrase_time > timedelta(seconds=phrase_timeout):
                    last_sample = bytes()
                    phrase_complete = True
                phrase_time = now

                # Concatenate our current audio data with the latest audio data.
                while not data_queue.empty():
                    data = data_queue.get()
                    last_sample += data

                # Use AudioData to convert the raw data to wav data.
                audio_data = sr.AudioData(last_sample, source.SAMPLE_RATE, source.SAMPLE_WIDTH)
                wav_data = io.BytesIO(audio_data.get_wav_data())

                # Write wav data to the temporary file as bytes.
                with open(temp_file, 'w+b') as f:
                    f.write(wav_data.read())

                if translator == "None" or translator == "DeepL":
                    if language == "Auto":
                        result = audio_model.transcribe(temp_file, fp16=torch.cuda.is_available())
                    else:
                        # print("Using non auto with language: " + language)
                        result = audio_model.transcribe(temp_file, fp16=torch.cuda.is_available(), language=language)
                elif translator == "Whisper":
                    if language == "Auto":
                        result = audio_model.transcribe(temp_file, fp16=torch.cuda.is_available(), task="translate")
                    else:
                        result = audio_model.transcribe(temp_file, fp16=torch.cuda.is_available(), language=language, task="translate")

                text = result['text'].strip()

                if phrase_complete:
                    transcription.append(text)
                else:
                    transcription[-1] = text

                if clear_event.is_set():
                    transcription = ['']
                    clear_event.clear()
                    clear_queue(text_queue)

                clear_queue(text_queue)
                transcription_copy = transcription.copy()
                text_queue.put(transcription_copy)

                sleep(0.01)
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    print("CUDA available: " + str(torch.cuda.is_available()))

    with mp.Manager() as manager:
        model_queue = manager.Queue()
        load_event = manager.Event()
        language_queue = manager.Queue()
        translation_queue = manager.Queue()
        clear_event = manager.Event()
        text_queue = manager.Queue()

        # UI process
        lang_net_ui_process = mp.Process(target=lang_net_ui.run, args=(model_queue, load_event, language_queue, translation_queue, clear_event, text_queue))
        lang_net_ui_process.start()
        
        # Main process
        main(model_queue, load_event, language_queue, translation_queue, clear_event, text_queue)