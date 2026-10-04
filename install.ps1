# AI-API-Proxy — Windows Quickstart
# ─────────────────────────────────────
# Lädt das Repo, installiert alle Dependencies und startet den Launcher.
#
# Nutzung:
#     iwr -useb https://raw.githubusercontent.com/Innobytix-IT/AI-API-Proxy/main/install.ps1 | iex

$ErrorActionPreference = "Stop"

function Say($msg, $color = "White") { Write-Host $msg -ForegroundColor $color }

Say "`n== AI-API-Proxy · Quickstart ==`n" Cyan

# ── Python finden ────────────────────────────────────────────────────────
$pythonCmd = $null
foreach ($cmd in @("py", "python", "python3")) {
    if (Get-Command $cmd -ErrorAction SilentlyContinue) {
        $pythonCmd = $cmd
        break
    }
}
if (-not $pythonCmd) {
    Say "Python >= 3.10 nicht gefunden. Bitte zuerst installieren: https://python.org" Red
    exit 1
}
Say "Python gefunden: $pythonCmd" DarkGray

# ── Git finden ───────────────────────────────────────────────────────────
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Say "Git nicht gefunden. Bitte zuerst installieren: https://git-scm.com" Red
    exit 1
}
Say "Git gefunden." DarkGray

# ── Clone oder Update ────────────────────────────────────────────────────
$installDir = Join-Path $PWD "AI-API-Proxy"
if (Test-Path $installDir) {
    Say "`nVerzeichnis existiert bereits — Pull laufender Version..." Yellow
    Push-Location $installDir
    git pull --ff-only
    Pop-Location
} else {
    Say "`nKlone Repo nach $installDir..." Yellow
    git clone https://github.com/Innobytix-IT/AI-API-Proxy.git $installDir
}

Push-Location $installDir

# ── Dependencies ─────────────────────────────────────────────────────────
Say "`nInstalliere Dependencies..." Yellow
& $pythonCmd -m pip install --upgrade pip --quiet
& $pythonCmd -m pip install -r requirements.txt --quiet

# ── Launcher starten ─────────────────────────────────────────────────────
Say "`nStarte Launcher — API-Key eintragen und 'Server starten' klicken.`n" Green
& $pythonCmd app.py

Pop-Location
