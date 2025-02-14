# Crea l'ambiente virtuale se non esiste
if (!(Test-Path "venv")) {
    python -m venv venv
    Write-Output "Ambiente virtuale creato."
}

# Attiva l'ambiente virtuale
Write-Output "Attivazione ambiente virtuale..."
& ".\venv\Scripts\Activate.ps1"

# Avvia il programma di registrazione
Write-Output "Avvio della registrazione dello schermo..."
python .\main.py
# python main.py 60 output.mp4

deactivate
