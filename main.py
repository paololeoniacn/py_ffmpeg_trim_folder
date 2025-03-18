import subprocess
import sys
import os
from datetime import datetime
import win32gui
import re
from screeninfo import get_monitors
import msvcrt
import subprocess

def sanitize_filename(filename):
    """
    Sostituisce gli spazi con underscore e rimuove i caratteri non consentiti
    nei nomi dei file per Windows.
    """
    sanitized = filename.replace(" ", "_")
    sanitized = re.sub(r'[<>:"/\\|?*]', '', sanitized)
    sanitized = re.sub(r'_+', '_', sanitized).strip('_')
    return sanitized

def get_open_windows():
    """
    Restituisce una lista di tuple (hwnd, titolo) per le finestre visibili con un titolo non vuoto.
    """
    windows = []
    def enumHandler(hwnd, lParam):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd).strip()
            if title:
                windows.append((hwnd, title))
    win32gui.EnumWindows(enumHandler, None)
    return windows

def choose_window():
    """
    Elenca le finestre aperte e permette di sceglierne una tramite numero.
    Se l'utente lascia vuoto l'input o fornisce un numero non valido, restituisce None
    (registrazione dell'intero desktop).
    """
    windows = get_open_windows()
    if not windows:
        print("Nessuna finestra aperta trovata!")
        return None
    print("Finestre aperte:")
    for i, (hwnd, title) in enumerate(windows):
        print(f"{i}) {title}")
    scelta = input("🔎 Scegli il numero della finestra da registrare (lascia vuoto per intero desktop): ").strip()
    if scelta == "":
        return None
    try:
        scelta_num = int(scelta)
        if 0 <= scelta_num < len(windows):
            return windows[scelta_num]  # Restituisce (hwnd, titolo)
        else:
            print("Numero non valido, verrà registrato l'intero desktop.")
            return None
    except ValueError:
        print("Input non valido, verrà registrato l'intero desktop.")
        return None

def choose_monitor():
    """
    Elenca i monitor disponibili e permette di sceglierne uno.
    Se l'input è vuoto o non valido, restituisce il monitor primario.
    """
    monitors = get_monitors()
    if not monitors:
        print("Nessun monitor trovato!")
        return None
    print("Monitor disponibili:")
    for i, m in enumerate(monitors):
        # Se disponibile, mostra il nome del monitor, altrimenti un'etichetta generica
        name = getattr(m, 'name', f"Monitor {i}")
        print(f"{i}) {name}: {m.width}x{m.height} @ ({m.x}, {m.y})")
    scelta = input("Scegli il numero del monitor da registrare (lascia vuoto per il monitor primario): ").strip()
    if scelta == "":
        return monitors[0]
    try:
        scelta_num = int(scelta)
        if 0 <= scelta_num < len(monitors):
            return monitors[scelta_num]
        else:
            print("Numero non valido, verrà usato il monitor primario.")
            return monitors[0]
    except ValueError:
        print("Input non valido, verrà usato il monitor primario.")
        return monitors[0]

def record_application(window_title, window_rect, system_audio_device, mic_audio_device, output_file):
    command = ["ffmpeg", "-y"]
    
    # Validate the system audio device if provided
    if system_audio_device:
        validate_dshow_device(system_audio_device)

    # Se sono disponibili le coordinate (window_rect), le usiamo per ritagliare la porzione di desktop
    if window_rect:
        left, top, right, bottom = window_rect
        width = right - left
        height = bottom - top
        command.extend([
            "-f", "gdigrab",
            "-framerate", "30",
            "-offset_x", str(left),
            "-offset_y", str(top),
            "-video_size", f"{width}x{height}",
            "-i", "desktop"
        ])
    else:
        # Altrimenti, cattura l'intero desktop
        command.extend(["-f", "gdigrab", "-framerate", "30", "-i", "desktop"])
    
    # Gestione degli input audio.
    if system_audio_device and mic_audio_device:
        command.extend([
            "-f", "dshow", "-i", f"audio={system_audio_device}",
            "-f", "dshow", "-i", f"audio={mic_audio_device}",
            "-filter_complex", "[1:a][2:a]amix=inputs=2:duration=first:dropout_transition=2[aout]",
            "-map", "0:v", "-map", "[aout]"
        ])
    elif system_audio_device:
        command.extend([
            "-f", "dshow", "-i", f"audio={system_audio_device}",
            "-map", "0:v", "-map", "1:a"
        ])
    elif mic_audio_device:
        command.extend([
            "-f", "dshow", "-i", f"audio={mic_audio_device}",
            "-map", "0:v", "-map", "1:a"
        ])
    
    # Parametri per una codifica compatibile: H.264 per il video e AAC per l'audio.
    command.extend([
        "-c:v", "h264_qsv",
        "-preset", "fast",
        "-pix_fmt", "yuv420p",
        "-r", "30",
        "-vsync", "1",
        "-c:a", "aac",
        "-fflags", "+genpts",
        "-avoid_negative_ts", "make_zero",
        output_file
    ])


    print("\nEsecuzione del comando:")
    print(" ".join(command))
    print("\n🎥 La registrazione è in corso... premi 'q' per terminare.\n")

    try:
        proc = subprocess.Popen(command, stdin=subprocess.PIPE)
        return proc
    except FileNotFoundError:
        print("Errore: ffmpeg non è stato trovato. Assicurati che sia installato e presente nel PATH.")
        sys.exit(1)

def validate_dshow_device(device_name: str) -> None:
    """
    Verifies that ffmpeg’s DirectShow list_devices output contains device_name.
    If not found, prints a user‑friendly English error and exits.
    """
    try:
        output = subprocess.check_output(
            ["ffmpeg", "-list_devices", "true", "-f", "dshow", "-i", "dummy"],
            stderr=subprocess.STDOUT,
            text=True
        )
        
    except FileNotFoundError:
        print("Error: ffmpeg executable not found. Make sure ffmpeg is installed and on your PATH.")
        sys.exit(1)

    if device_name not in output:
        print(f"\nERROR: The audio device “{device_name}” was not found by ffmpeg.\n")
        print(f"\n ----- ACTUAL LIST ----- \n")
        print(output)
        print(f"\n ----- ACTUAL LIST ----- \n")
        print("Possible fixes:")
        print(" • Make sure “Stereo Mix” is enabled in Windows ► Control Panel → Sound → Recording → Right‑click → Show Disabled Devices → Enable Stereo Mix.")
        print(" • If you don’t see Stereo Mix, install a virtual audio capture driver (e.g. VB‑Audio Virtual Cable) and restart your PC.")
        print(" • Alternatively you can switch to WASAPI loopback capture (use “-f wasapi -i \"Speakers (Your Output Device):loopback\"” instead).")
        input("Press ENTER to exit...")
        sys.exit(1)

if __name__ == "__main__":
    output_file_input = input(f"Inserisci il nome del file di output (es. Test.mp4): ").strip()
    
    # Chiedi all'utente se registrare una finestra o uno schermo.
    mode = input("Vuoi registrare (1) una finestra o (2) uno schermo? [default: 2]: ").strip()
    if mode == "" or mode == "2":
        monitor = choose_monitor()
        # Per il monitor, usiamo le sue coordinate
        window_title = f"Monitor_{monitor.width}x{monitor.height}"
        window_rect = (monitor.x, monitor.y, monitor.x + monitor.width, monitor.y + monitor.height)
    else:
        window_choice = choose_window()
        if window_choice:
            hwnd, window_title = window_choice
            window_rect = win32gui.GetWindowRect(hwnd)
        else:
            window_title = None
            window_rect = None

    # Audio di sistema: default S (Si)
    audio_sys_input = input("Vuoi registrare l'audio di sistema? (S/n) [default: S]: ").strip().lower()
    if audio_sys_input == "" or audio_sys_input == "s":
        # system_audio_device = "Stereo Mix (Realtek(R) Audio)"
        system_audio_device = "Stereo Mix (2- Realtek(R) Audio)"
    else:
        system_audio_device = None

    # Microfono: default n (No)
    mic_input = input("Vuoi registrare il microfono? (S/n) [default: n]: ").strip().lower()
    if mic_input == "" or mic_input == "n":
        mic_audio_device = None
    else:
        mic_audio_device = input("Inserisci il nome esatto del dispositivo microfono: ").strip()
        if mic_audio_device == "":
            mic_audio_device = None

    # Creazione della cartella di output con timestamp
    start_time = datetime.now()
    timestamp_folder = start_time.strftime("%Y%m%d_%H%M%S")
    # output_folder = f"recordings/{timestamp_folder}" #LOCAL
    CAPTURE_FOLDER = "C:\\Users\\paolo.leoni\\Videos\\Captures\\"
    output_folder = os.path.join(str(CAPTURE_FOLDER),"myFFMPEG")
    os.makedirs(output_folder, exist_ok=True)

    # Imposta il nome di default del file: se si registra una finestra, usa il titolo (sanitizzato);
    # altrimenti usa l'orario di inizio.
    appendix = start_time.strftime("%H_%M_%S")
    default_file_base_tmp = sanitize_filename(window_title) if window_title else "default"
    default_file_base = F"{default_file_base_tmp}_{appendix}"
    
    if output_file_input == "":
        output_file = f"{output_folder}/{default_file_base}.mp4"
    else:
        output_file = f"{output_folder}/{output_file_input}_{appendix}.mp4"

    proc = record_application(window_title, window_rect, system_audio_device, mic_audio_device, output_file)

    print("Premi 'q' per fermare la registrazione...")
    while True:
        if msvcrt.kbhit() and msvcrt.getch().lower() == b'q':
            break
    try:
        proc.communicate(input=b"q\n")
    except Exception as e:
        print("Si è verificato un errore durante la terminazione della registrazione:", e)

    # input("Premi INVIO per fermare la registrazione...\n")
    # try:
    #     proc.communicate(input=b"q\n")
    # except Exception as e:
    #     print("Si è verificato un errore durante la terminazione della registrazione:", e)

    print(f"✅ Video salvato in {output_file}({os.path.getsize(output_file)/1024/1024:.2f} MB)")
 
