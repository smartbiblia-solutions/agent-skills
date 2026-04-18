#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from lib.common import KNOWLEDGE_DIR, load_json, write_json_stdout


def slugify(text: str) -> str:
    return "-".join("".join(ch.lower() if ch.isalnum() else " " for ch in text).split())[:80] or "rule"


def main() -> int:
    parser = argparse.ArgumentParser(description="Mise à jour simple du wiki de catalogage.")
    parser.add_argument("--rule-file", required=True, help="JSON contenant au minimum title et rule_markdown.")
    args = parser.parse_args()

    payload = load_json(args.rule_file)
    title = payload.get("title", "Règle")
    body = payload.get("rule_markdown", "")
    target = KNOWLEDGE_DIR / f"user-rule-{slugify(title)}.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    content = f"# {title}\n\n{body.strip()}\n"
    target.write_text(content, encoding="utf-8")
    write_json_stdout({
        "updated_files": [str(target.relative_to(ROOT))],
        "rules_added": 1,
        "rules_updated": 0,
        "error": None,
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
