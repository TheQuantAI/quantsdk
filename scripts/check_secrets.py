#!/usr/bin/env python3
"""Scan source code for potential hardcoded secrets."""

import pathlib
import re
import sys

PATTERN = re.compile(
    r"(password|secret|api_key|token)\s*=\s*[\x22\x27].{8,}[\x22\x27]",
    re.IGNORECASE,
)

# Allowlist: lines that are false positives (e.g., test assertions, docs)
ALLOWLIST = {
    "# nosec",
    "test_",
    "mock",
    "example",
    "dummy",
    "placeholder",
    "your_",
    "your-",
    "****",
    "masked",
    '"""',
    "'''",
}


def main() -> int:
    found = False
    for f in pathlib.Path("src").rglob("*.py"):
        for i, line in enumerate(f.read_text().splitlines(), 1):
            if PATTERN.search(line):
                # Skip allowlisted lines
                if any(kw in line.lower() for kw in ALLOWLIST):
                    continue
                print(f"  {f}:{i}: {line.strip()}")
                found = True

    if found:
        print("\n::warning::Potential hardcoded secrets detected")
        return 1

    print("No hardcoded secrets found ✅")
    return 0


if __name__ == "__main__":
    sys.exit(main())
