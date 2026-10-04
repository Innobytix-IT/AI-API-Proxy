# AI-API-Proxy

Lokaler **OpenAI-kompatibler Proxy** für die offizielle Google-Gemini-API — mit automatischer Modell-Rotation bei Quota-Erschöpfung, echtem SSE-Streaming und Token-Pruning für Agenten.

Ideal um bestehende Clients (Open-WebUI, Librechat, Continue.dev, Ilija, eigene Agenten, …) über ein einziges `http://.../v1/chat/completions`-Endpoint an Gemini zu hängen — ohne pro Client die Rate-Limits einzeln managen zu müssen.

---

## Features

- **OpenAI-kompatibel**: `/v1/chat/completions`, `/v1/models`, `/health`
- **Auto-Modell-Discovery**: ruft beim Start `models.list()` auf, filtert alle agent-tauglichen Gemini-Modelle und sortiert nach Qualität
- **Automatischer Fallback bei 429/503**: wenn ein Modell rate-limited oder überlastet ist, rotiert der Router sofort zum nächsten — effektiv endloses Tageskontingent für Personal-Use
- **Echtes SSE-Streaming**: Chunks kommen einzeln an, nicht erst am Ende; First-Chunk-Peeking stellt sicher dass bei 429 noch sauber auf nächstes Modell gefallback'd wird
- **Native Gemini-Content-Objekte**: Multi-Turn-Dialoge mit korrektem Role-Alternation, Tool-/Function-Role-Formatierung und Erstmessage-Enforcement
- **Agent-History-Pruning**: in langen Agent-Loops werden mittlere Tool-Outputs komprimiert; Hauptziel + letzte N Turns bleiben voll erhalten → spart massiv Prompt-Tokens
- **Token-Usage-Metriken**: `prompt_tokens`, `completion_tokens`, `total_tokens` werden aus Googles Metadaten weitergereicht
- **Tkinter-Launcher**: Dark-Theme-GUI mit API-Key-Prüfung, Port-Einstellung, Start/Stop-Button und Endpunkt-URL zum Kopieren

---

## Setup

### Voraussetzungen

- Python ≥ 3.10
- Ein kostenloser Gemini-API-Key aus [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

### Installation

```bash
git clone https://github.com/Innobytix-IT/AI-API-Proxy.git
cd AI-API-Proxy
pip install -r requirements.txt
```

### Konfiguration

```bash
cp .env.example .env
# .env öffnen und GEMINI_API_KEY eintragen
```

Alternativ: einfach den **Launcher** starten — er pflegt die `.env` automatisch:

```bash
python app.py
```

---

## Nutzung

### Variante A — Launcher (empfohlen)

```bash
python app.py
```

1. API-Key ins Feld eintragen → **„Prüfen"** klickt `models.list()` und zeigt die Modellanzahl
2. Port + API-Secret anpassen (oder Default lassen)
3. **„▶ Server starten"** → grüner Punkt zeigt Status
4. „Netzwerk-URL kopieren" → in deinen Client als Endpunkt eintragen, API-Secret als API-Key

### Variante B — Nur CLI

```bash
python main.py
# oder: uvicorn main:app --host 0.0.0.0 --port 8642
```

---

## Nutzung aus Clients

Jeder OpenAI-kompatible Client funktioniert. Beispiel mit `curl`:

```bash
curl http://localhost:8642/v1/chat/completions \
  -H "Authorization: Bearer DEIN_API_SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "auto",
    "messages": [{"role": "user", "content": "Erkläre Rate-Limiting in einem Satz."}]
  }'
```

Beispiel mit `openai`-Python-Client:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8642/v1",
    api_key="DEIN_API_SECRET",
)

resp = client.chat.completions.create(
    model="auto",     # Router wählt bestes verfügbares Modell
    messages=[{"role": "user", "content": "Hallo"}],
    stream=True,
)
for chunk in resp:
    print(chunk.choices[0].delta.content or "", end="")
```

### Modell-Auswahl

- `"auto"` — Router rotiert bei 429/503 automatisch
- `"gemini-2.5-flash"`, `"gemini-pro-latest"`, … — explizites Modell; bei 429 weiter zum nächsten in der Rangliste

---

## Endpunkte

| Methode | Pfad | Beschreibung |
|---|---|---|
| `GET` | `/health` | Status + geladene Modelle |
| `GET` | `/v1/models` | Modell-Katalog (OpenAI-Format) |
| `POST` | `/v1/chat/completions` | Chat (Non-Streaming + SSE-Streaming) |

---

## Konfiguration (`.env`)

| Variable | Default | Zweck |
|---|---|---|
| `GEMINI_API_KEY` | — | Google-AI-Studio-API-Key (**erforderlich**) |
| `API_SECRET` | `change-me-…` | Shared-Secret für Clients. Leer / „change-me" = ungeschützt |
| `HOST` | `0.0.0.0` | Server-Bind — `0.0.0.0` für LAN, `127.0.0.1` für nur lokal |
| `PORT` | `8642` | TCP-Port |
| `MODEL_EXCLUDE` | *(siehe .env.example)* | Kommagetrennte Substrings — Modelle, deren Name einen enthält, werden aussortiert |
| `DEFAULT_MODEL` | `auto` | Fallback wenn Client nichts angibt |
| `ENABLE_AGENT_PRUNING` | `true` | History-Pruning für Agent-Loops aktivieren |
| `PRUNE_KEEP_RECENT` | `4` | Anzahl jüngster Nachrichten die voll erhalten bleiben |
| `PRUNE_MAX_MIDDLE_CHARS` | `350` | Ältere Tool-Outputs auf diese Länge kürzen |

---

## Projektstruktur

```
AI-API-Proxy/
├── app.py              Tkinter-Launcher
├── main.py             FastAPI-App (Endpunkte, SSE)
├── router.py           Modell-Fallback-Logik (429/503)
├── config.py           .env-Loader (pydantic-settings)
├── models.py           OpenAI-Request-Schemas
├── providers/
│   └── api.py          Gemini-SDK-Wrapper (async + streaming + usage)
├── test_routes.py      End-to-End-Test (Health, Standard, Streaming, Pruning)
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## Lizenz

[GPL-3.0](LICENSE) — frei nutzbar, abgeleitete Werke müssen ebenfalls GPL-3.0 sein.
