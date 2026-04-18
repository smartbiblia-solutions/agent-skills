#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from lib.common import load_knowledge_summary, parse_cover_text, read_text, write_json_stdout


def main() -> int:
    parser = argparse.ArgumentParser(description="Extraction de métadonnées de thèse vers JSON.")
    parser.add_argument("--input-file", required=True, help="Fichier texte OCR ou transcription de couverture.")
    args = parser.parse_args()

    text = read_text(args.input_file)
    payload = parse_cover_text(text)
    write_json_stdout({
        "metadata": payload,
        "knowledge_summary": load_knowledge_summary(),
        "error": None,
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
