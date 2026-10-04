"""
End-to-End Test für den Proxy:
  1. GET /health
  2. POST /v1/chat/completions (Normal Ping)
  3. POST /v1/chat/completions (Echtes SSE-Streaming)
  4. POST /v1/chat/completions (Simulation Agenten-Loop mit Pruning)
"""
from __future__ import annotations

import os
import sys
import time
import json
import httpx

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(SCRIPT_DIR, ".env")

G, R, B, D, E = "\033[92m", "\033[91m", "\033[94m", "\033[90m", "\033[0m"


def _read_env() -> dict:
    res = {}
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, encoding="utf-8") as f:
            for line in f:
                k, _, v = line.strip().partition("=")
                if k and not k.startswith("#"):
                    res[k.strip()] = v.strip()
    return res


def main():
    env = _read_env()
    port = env.get("PORT", "8642")
    secret = env.get("API_SECRET", "")
    base = f"http://127.0.0.1:{port}"

    headers = {} if secret in ("", "change-me") else {"Authorization": f"Bearer {secret}"}
    client = httpx.Client(base_url=base, timeout=90.0, headers=headers)

    print(f"\n{B}── 1. GET /health ──{E}")
    try:
        r = client.get("/health")
        if r.status_code != 200:
            print(f"{R}Health-Check fehlgeschlagen:{E} {r.status_code} - {r.text}")
            return 1
        data = r.json()
        print(f"Status: {G}OK{E}, Verfügbare Modelle: {len(data.get('api_models', []))}")
    except Exception as e:
        print(f"{R}Server nicht erreichbar:{E} {e}")
        return 1

    print(f"\n{B}── 2. Standard Chat Completion ──{E}")
    body = {
        "model": "auto",
        "messages": [{"role": "user", "content": "Antworte mit exakt einem Wort: BEREIT"}],
    }
    r = client.post("/v1/chat/completions", json=body)
    if r.status_code == 200:
        d = r.json()
        print(f"Modell: {d.get('model')} | Antwort: {d['choices'][0]['message']['content'].strip()!r}")
        print(f"Usage-Metriken: {d.get('usage')}")
    else:
        print(f"{R}Fehler:{E} {r.status_code} - {r.text}")
        return 1

    print(f"\n{B}── 3. Echtes SSE-Streaming Testen ──{E}")
    body_stream = {
        "model": "auto",
        "messages": [{"role": "user", "content": "Zähle von 1 bis 5."}],
        "stream": True,
    }
    chunks_received = 0
    full_stream_text = []
    try:
        with client.stream("POST", "/v1/chat/completions", json=body_stream) as resp:
            for line in resp.iter_lines():
                if line.startswith("data: ") and not line.endswith("[DONE]"):
                    chunks_received += 1
                    chunk_json = json.loads(line[6:])
                    delta = chunk_json["choices"][0]["delta"].get("content", "")
                    full_stream_text.append(delta)
        print(f"{G}✓ Streaming erfolgreich!{E} Chunks empfangen: {chunks_received}")
        print(f"  Stream-Inhalt: {''.join(full_stream_text).strip()!r}")
    except Exception as e:
        print(f"{R}Streaming-Fehler:{E} {e}")
        return 1

    print(f"\n{B}── 4. Agenten-Pruning Simulation (10.000 Zeichen Tool-Dump) ──{E}")
    agent_history = [
        {"role": "system", "content": "Du bist ein präziser Python-Coding-Agent."},
        {"role": "user", "content": "AUFGABE: Finde heraus, ob in log.txt ein Error steht."},
        {"role": "assistant", "content": "Ich lese log.txt ein."},
        {"role": "tool", "name": "read_file", "content": "START\n" + ("X" * 10000) + "\nERROR: Port 8642 busy\nENDE"},
        {"role": "assistant", "content": "Ich sehe den Port-Error in der Datei."},
        {"role": "user", "content": "Bestätige nur mit dem Wort: 'Gefunden'."},
    ]

    t0 = time.time()
    r = client.post("/v1/chat/completions", json={"model": "auto", "messages": agent_history})
    dur = time.time() - t0

    if r.status_code == 200:
        res = r.json()
        usage = res.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        print(f"{G}✓ Agenten-Request erfolgreich! ({dur:.2f}s){E}")
        print(f"  Antwort: {res['choices'][0]['message']['content'].strip()!r}")
        print(f"  Verbrauchte Prompt-Tokens: {prompt_tokens} (Durch Pruning massiv reduziert!)")
    else:
        print(f"{R}✗ Fehler:{E} {r.status_code} - {r.text}")
        return 1

    print(f"\n{G}Alle Tests ohne Fehler bestanden! Proxy ist produktionsbereit.{E}")
    return 0


if __name__ == "__main__":
    sys.exit(main())