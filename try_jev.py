#!/usr/bin/env python3
"""Send one request file to Jev and print the answers.

    python try_jev.py                                  # the desk note
    python try_jev.py demos/02a-cocoa-clean.json
    python try_jev.py <file> --raw                     # also print the full reply

The key is read from a .env file in this folder:

    TYPESAFE_API_KEY=your_key

Each reply is saved to live/<name>.result.json.
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ENDPOINT = "https://api.typesafe.ai/v1/systemone"
KEY_NAME = "TYPESAFE_API_KEY"
HERE = Path(__file__).resolve().parent
DEFAULT_DEMO = HERE / "demos" / "01-desk-note.json"
BAR = 24


def load_key() -> str:
    """The key comes from a .env file, so it never shows on screen or in the repo.

    Looks in this folder, then its parent, then the current folder. Falls back
    to an exported TYPESAFE_API_KEY. No packages needed.
    """
    for folder in (HERE, HERE.parent, Path.cwd()):
        path = folder / ".env"
        if not path.is_file():
            continue
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[len("export "):]
            name, _, value = line.partition("=")
            if name.strip() != KEY_NAME:
                continue
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            else:
                value = value.split(" #")[0].strip()
            if value:
                return value
    return os.environ.get(KEY_NAME, "").strip()


def bar(p: float) -> str:
    filled = max(0, min(BAR, round(p * BAR)))
    return "█" * filled + "░" * (BAR - filled)


def show(answers: dict) -> None:
    width = max((len(name) for name in answers), default=0)
    for name, a in answers.items():
        kind = a.get("type")
        if kind == "noul":  # TypeSafe's API name for the yes-or-no question
            p = a.get("noul", 0.0)
            print(f"  {name:<{width}}   yes  {p:4.2f}  {bar(p)}")
        elif kind == "score":
            p = a.get("score", 0.0)
            print(f"  {name:<{width}}   score {p:4.2f}  {bar(p)}  confidence {a.get('confidence', 0):.2f}")
        elif kind == "choice":
            print(f"  {name:<{width}}   {a.get('choice')}   confidence {a.get('confidence', 0):.2f}")
            options = a.get("probabilities") or {}
            for option, p in sorted(options.items(), key=lambda kv: -kv[1]):
                print(f"  {'':<{width}}     {option:<18} {p:4.2f}  {bar(p)}")
        else:
            print(f"  {name:<{width}}   {a}")
        print()


def main() -> int:
    args = sys.argv[1:]
    raw = "--raw" in args
    args = [a for a in args if a != "--raw"]
    out_path = None
    if "--out" in args:
        i = args.index("--out")
        out_path = Path(args[i + 1])
        del args[i : i + 2]

    demo = Path(args[0]) if args else DEFAULT_DEMO
    body = json.loads(demo.read_text())
    if out_path is None:
        out_path = HERE / "live" / f"{demo.stem}.result.json"

    key = load_key()
    if not key:
        print(f"No API key found. Add this line to a file named .env:\n\n    {KEY_NAME}=your_key")
        return 1

    request = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    print(f"\n  {body.get('model', 'jev')}  ·  {demo.name}\n")
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode())
    except urllib.error.HTTPError as error:
        print(f"  Request failed: HTTP {error.code}")
        print(error.read().decode(errors="replace"))
        return 1
    except urllib.error.URLError as error:
        print(f"  Could not reach the API: {error.reason}")
        return 1
    elapsed_ms = round((time.perf_counter() - started) * 1000)

    payload["_client_ms"] = elapsed_ms  # round trip from this machine, saved with the result
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2))

    if raw:
        print(json.dumps(payload, indent=2))
        print()
    show(payload.get("answers") or {})

    usage = payload.get("usage") or {}
    tokens = f"  ·  {usage.get('input_tokens')} tokens in, {usage.get('output_tokens')} out" if usage else ""
    print(f"  {elapsed_ms} ms round trip{tokens}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
