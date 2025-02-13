# Crea l'ambiente virtuale se non esiste
if (!(Test-Path "venv")) {
    python -m venv venv
    Write-Output "✅ Ambiente virtuale creato."
}

# Attiva l'ambiente virtuale
Write-Output "🔹 Attivazione dell'ambiente virtuale..."
& ".\venv\Scripts\Activate.ps1"

# Installa sounddevice se non è già installato
Write-Output "🔹 Controllo e installazione delle dipendenze..."
pip install sounddevice --quiet

# Esegui lo script Python per mostrare i dispositivi audio
Write-Output "🎧 test audio:"
python test_audio.py

# Mantiene la finestra aperta per visualizzare il risultato
Write-Output "🔹 Premi INVIO per chiudere."
Pause
