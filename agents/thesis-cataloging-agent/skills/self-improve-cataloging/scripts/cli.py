#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from lib.common import MEMORY_DIR, load_json, write_json_stdout


def main() -> int:
    parser = argparse.ArgumentParser(description="Mise en mémoire d'un retour de catalogage.")
    parser.add_argument("--feedback-file", required=True, help="JSON du retour utilisateur ou de l'écart observé.")
    args = parser.parse_args()

    payload = load_json(args.feedback_file)
    memory_file = MEMORY_DIR / "cases.jsonl"
    memory_file.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": dt.datetime.utcnow().isoformat() + "Z",
        "payload": payload,
    }
    with memory_file.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    write_json_stdout({
        "memory_updated": True,
        "entries_written": 1,
        "wiki_candidate": bool(payload.get("generalizable_rule")),
        "error": None,
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
