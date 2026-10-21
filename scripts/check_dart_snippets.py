#!/usr/bin/env python3
"""Analyze selected Dart APIs and test the SSE snippet extracted from its reference."""
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/dart"


def main():
    reference = ROOT / "mobile-stack-toolkit/references/flutter/ai-integration.md"
    blocks = re.findall(r"^```dart\n(.*?)^```", reference.read_text(), re.M | re.S)
    candidates = [block for block in blocks if "Stream<String> streamAI(" in block]
    if len(candidates) != 1:
        raise ValueError("Expected one complete streamAI Dart snippet")
    generated = FIXTURE / "lib/stream.dart"
    generated.write_text(candidates[0])
    try:
        for command in (
            ["dart", "pub", "get", "--enforce-lockfile"],
            ["dart", "analyze"],
            ["dart", "test"],
        ):
            subprocess.run(command, cwd=FIXTURE, check=True, timeout=180)
    finally:
        generated.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
