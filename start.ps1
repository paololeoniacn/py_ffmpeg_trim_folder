# Controllo se FFmpeg è installato
$ffmpegPath = (Get-Command ffmpeg -ErrorAction SilentlyContinue).Source
if (-not $ffmpegPath) {
    Write-Output "FFmpeg non è installato o non è nel PATH."

    # Controlla se Chocolatey è installato
    $chocoPath = (Get-Command choco -ErrorAction SilentlyContinue).Source
    if ($chocoPath) {
        Write-Output "Chocolatey trovato. Installo FFmpeg..."
        choco install ffmpeg -y
        Write-Output "FFmpeg installato con Chocolatey. Riavvia il terminale e riesegui questo script."
        exit
    } else {
        Write-Output "Chocolatey non è installato. Segui questi passi per installare FFmpeg manualmente:"
        Write-Output "1. Scarica FFmpeg da https://www.gyan.dev/ffmpeg/builds/"
        Write-Output "2. Scegli la versione 'ffmpeg-release-essentials.zip'."
        Write-Output "3. Estrai il contenuto in C:\ffmpeg."
        Write-Output "4. Aggiungi C:\ffmpeg\bin al PATH di Windows."
        Write-Output "5. Riavvia il terminale e riesegui questo script."
        exit
    }
}

Write-Output "FFmpeg trovato in: $ffmpegPath"

# Crea l'ambiente virtuale se non esiste
if (!(Test-Path "venv")) {
    python -m venv venv
    Write-Output "Ambiente virtuale creato."
}

# Attiva l'ambiente virtuale
Write-Output "Attivazione dell'ambiente virtuale..."
& ".\venv\Scripts\Activate.ps1"

# Installa le dipendenze
Write-Output "Installazione delle dipendenze..."
pip install -r requirements.txt

# Avvia il programma di registrazione
Write-Output "Avvio della registrazione dello schermo..."
python .\main.py
