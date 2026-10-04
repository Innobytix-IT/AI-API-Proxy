"""
Testet dass der Proxy sowohl mit als auch ohne /v1-Präfix funktioniert.
Simuliert alle 4 häufigen Client-Kombinationen:

  1. Base = http://host:port       + Client hängt /v1/...  an
  2. Base = http://host:port/v1    + Client hängt /...     an
  3. Base = http://host:port       + Client hängt /...     an  (fehlendes /v1)
  4. Base = http://host:port/v1    + Client hängt /v1/...  an  (doppeltes /v1)
"""
from __future__ import annotations

import os
import sys
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


def _test(label: str, url: str, headers: dict) -> bool:
    body = {
        "model": "auto",
        "messages": [{"role": "user", "content": "Antworte nur: OK"}],
    }
    try:
        r = httpx.post(url, json=body, headers=headers, timeout=60)
        if r.status_code != 200:
            print(f"  {R}✗{E}  {label}  → HTTP {r.status_code}  {D}{r.text[:120]}{E}")
            return False
        data = r.json()
        used = data.get("model", "?")
        txt = (data["choices"][0]["message"]["content"] or "").strip()
        print(f"  {G}✓{E}  {label}  → {used}  answer={txt!r}")
        return True
    except Exception as e:
        print(f"  {R}✗{E}  {label}  → {e}")
        return False


def main() -> int:
    env = _read_env()
    port = env.get("PORT", "8642")
    secret = env.get("API_SECRET", "")
    headers = {} if secret in ("", "change-me") else {"Authorization": f"Bearer {secret}"}
    host = f"http://127.0.0.1:{port}"

    print(f"\n{B}── URL-Format-Tests  @ {host} ──{E}\n")

    cases = [
        ("Standard         /v1/chat/completions",  f"{host}/v1/chat/completions"),
        ("Ohne /v1-Präfix  /chat/completions",     f"{host}/chat/completions"),
        ("Doppeltes /v1    /v1/v1/chat/completions", f"{host}/v1/v1/chat/completions"),
        ("Dreifach /v1     /v1/v1/v1/chat/completions", f"{host}/v1/v1/v1/chat/completions"),
    ]

    oks = 0
    for label, url in cases:
        if _test(label, url, headers):
            oks += 1

    print(f"\n{B}── /v1/models vs /models ──{E}\n")
    for label, url in [
        ("Standard  /v1/models",  f"{host}/v1/models"),
        ("Ohne /v1  /models",     f"{host}/models"),
        ("Doppelt   /v1/v1/models", f"{host}/v1/v1/models"),
    ]:
        try:
            r = httpx.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                n = len(r.json().get("data", []))
                print(f"  {G}✓{E}  {label}  → {n} Modelle")
                oks += 1
            else:
                print(f"  {R}✗{E}  {label}  → HTTP {r.status_code}")
        except Exception as e:
            print(f"  {R}✗{E}  {label}  → {e}")

    total = len(cases) + 3
    print(f"\n{B}Ergebnis:{E} {oks}/{total} erfolgreich")
    return 0 if oks == total else 1


if __name__ == "__main__":
    sys.exit(main())
