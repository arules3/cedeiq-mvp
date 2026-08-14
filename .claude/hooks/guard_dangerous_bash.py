#!/usr/bin/env python3
"""
PreToolUse hook: guards against destructive bash commands before Claude Code
executes them. Claude Code passes tool-call details as JSON on stdin; this
script reads the proposed command and exits non-zero (blocking) if it
matches a deny-listed pattern, or 0 (allow) otherwise.

This is a real, runnable safety hook — not a placeholder — though it hasn't
been exercised inside a live Claude Code session for this capstone (see
docs/daily-log.md, CLI budget constraint).
"""

import json
import sys

DANGEROUS_PATTERNS = [
    "rm -rf /",
    "rm -rf ~",
    "rm -rf .git",
    "git push --force",
    "git push -f",
    "DROP TABLE",
    "DROP DATABASE",
    "> backend/cedeiq.db",  # overwriting the DB file directly instead of via the app
]


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        # If we can't parse the hook payload, fail open (allow) rather than
        # block legitimate work on a parsing issue — but log it.
        print("guard_dangerous_bash: could not parse hook input, allowing.", file=sys.stderr)
        sys.exit(0)

    command = payload.get("tool_input", {}).get("command", "")

    for pattern in DANGEROUS_PATTERNS:
        if pattern.lower() in command.lower():
            print(
                f"BLOCKED by guard_dangerous_bash: command contains '{pattern}'. "
                f"If this is intentional, run it manually outside Claude Code.",
                file=sys.stderr,
            )
            sys.exit(2)  # non-zero exit signals Claude Code to block the tool call

    sys.exit(0)


if __name__ == "__main__":
    main()
