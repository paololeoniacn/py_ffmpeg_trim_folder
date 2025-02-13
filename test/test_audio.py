import sounddevice as sd
import numpy as np
import wave

# Imposta il dispositivo corretto
SAMPLE_RATE = 44100
CHANNELS = 2
DEVICE = 23  # Usa "Stereo Mix (Realtek HD Audio Stereo input)"

print(f"🎧 Registrazione test con il dispositivo {DEVICE}...")
recording = sd.rec(int(5 * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='int16', device=DEVICE)
sd.wait()
print("✅ Registrazione completata!")

# Salva il file audio
with wave.open("test_audio.wav", 'wb') as wf:
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(2)
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(recording.tobytes())

print("🎧 Prova il file test_audio.wav")
