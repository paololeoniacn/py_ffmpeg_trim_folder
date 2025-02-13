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

# Definizione della versione di Python richiesta
$PYTHON_VERSION = "3.12.3"

# 🔍 Controllo della versione di Python attuale
Write-Host "🔍 Verifica della versione di Python..."
$pythonVersionOutput = python --version 2>&1
if ($pythonVersionOutput -match "No global/local python version has been set yet") {
    Write-Host "❌ Nessuna versione di Python è stata impostata. Controllo Pyenv..."
    $pythonVersion = $null
} else {
    $pythonVersion = $pythonVersionOutput -replace "Python ", ""
}

# ⚠️ Se la versione di Python NON è quella richiesta, tenta di usare Pyenv
if ($pythonVersion -ne $PYTHON_VERSION) {
    Write-Host "⚠️ Versione Python errata. Richiesta: $PYTHON_VERSION, Trovata: $pythonVersion"
    
    # Controllo se Pyenv è installato
    $pyenvCheck = Get-Command pyenv -ErrorAction SilentlyContinue
    if (-not $pyenvCheck) {
        Write-Host "❌ Pyenv non è installato. Installa Pyenv e riprova."
        Exit 1
    }

    Write-Host "✅ Pyenv trovato. Provo a installare e impostare Python $PYTHON_VERSION..."

    # Controllo se la versione di Python richiesta è già installata su Pyenv
    $installedVersions = pyenv versions --bare
    if ($installedVersions -notcontains $PYTHON_VERSION) {
        Write-Host "🔄 Installazione di Python $PYTHON_VERSION tramite Pyenv..."
        pyenv install $PYTHON_VERSION
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Errore nell'installazione di Python con Pyenv. Esco..."
            Exit 1
        }
    }

    # Risincronizza Pyenv
    Write-Host "🔄 Aggiornamento Pyenv..."
    pyenv rehash

    # Impostare la versione di Python a livello locale per questa cartella
    Write-Host "🔄 Impostazione della versione di Python a livello locale..."
    pyenv local $PYTHON_VERSION
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Errore nell'impostare la versione locale di Python. Esco..."
        Exit 1
    }

    # Riprova a verificare la versione di Python
    $pythonVersion = python --version 2>&1
    $pythonVersion = $pythonVersion -replace "Python ", ""

    # Se la versione è ancora errata, esci con errore
    if ($pythonVersion -ne $PYTHON_VERSION) {
        Write-Host "❌ Errore critico: Python $PYTHON_VERSION non è stato impostato correttamente. Esco..."
        Exit 1
    }
}

Write-Host "✅ Versione di Python corretta ($PYTHON_VERSION). Procedo con il setup..."

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
# python main.py 60 output.mp4

