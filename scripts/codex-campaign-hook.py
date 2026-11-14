#!/usr/bin/env python3
"""Run this project's campaign guard with Codex's native Stop payload."""
import json
from pathlib import Path
import sys


def main():
    import campaign_guard
    root = str(Path(__file__).resolve().parents[1])
    raw = sys.stdin.read(2_000_001)
    try:
        if len(raw) > 2_000_000:
            raise ValueError("Codex hook payload too large")
        event = json.loads(raw)
        if not isinstance(event, dict):
            raise ValueError("Codex hook payload must be an object")
        event.pop("conversationId", None)
        _, output = campaign_guard.stop_hook(json.dumps(event), root)
        print(output or "{}")
    except Exception as error:
        print(f"codex-campaign-hook: {error}", file=sys.stderr)
        print("{}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
