import cv2
import numpy as np
import mss
import sounddevice as sd
import queue
import threading
import wave
import time
import ffmpeg
import keyboard  # Aggiunto per la gestione dei tasti

# Imposta i parametri
SCREEN_SIZE = (1920, 1080)
VIDEO_FILENAME = "output.mp4"
AUDIO_FILENAME = "output.wav"
FINAL_OUTPUT = "final_video.mp4"
FPS = 30

# Coda per l'audio
audio_queue = queue.Queue()

# Imposta il formato dell'audio
SAMPLE_RATE = 44100
CHANNELS = 2

recording = True  # Variabile di controllo

def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    audio_queue.put(indata.copy())

def record_audio():
    with wave.open(AUDIO_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)

        with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, callback=audio_callback):
            while recording:
                data = audio_queue.get()
                wf.writeframes(data.astype(np.int16).tobytes())

def record_screen():
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  
    out = cv2.VideoWriter(VIDEO_FILENAME, fourcc, FPS, SCREEN_SIZE)

    with mss.mss() as sct:
        monitor = sct.monitors[1]  # Monitor principale

        while recording:
            img = sct.grab(monitor)
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            out.write(frame)

    out.release()

def merge_audio_video():
    input_video = ffmpeg.input(VIDEO_FILENAME)
    input_audio = ffmpeg.input(AUDIO_FILENAME)
    ffmpeg.output(input_video, input_audio, FINAL_OUTPUT, vcodec='libx264', acodec='aac').run()

# Avvio delle registrazioni
audio_thread = threading.Thread(target=record_audio)
video_thread = threading.Thread(target=record_screen)

print("Inizio registrazione... (Premi 'q' per terminare)")
audio_thread.start()
video_thread.start()

# Attendi che l'utente prema 'q' per terminare
while True:
    if keyboard.is_pressed('q'):
        print("Interruzione della registrazione...")
        recording = False
        break
    time.sleep(0.1)

# Aspetta la fine delle registrazioni
audio_thread.join()
video_thread.join()

# Unisce audio e video
print("Unione di audio e video...")
merge_audio_video()
print(f"Video finale salvato come {FINAL_OUTPUT}")
