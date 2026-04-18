#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from lib.common import build_unimarc_xml, load_json, write_json_stdout


def main() -> int:
    parser = argparse.ArgumentParser(description="Génération locale d'UNIMARC XML.")
    parser.add_argument("--json-file", required=True, help="Chemin du JSON de métadonnées.")
    parser.add_argument("--persons-file", help="Chemin optionnel du JSON enrichi IdRef.")
    args = parser.parse_args()

    payload = load_json(args.json_file)
    metadata = payload.get("metadata", payload)
    persons = None
    if args.persons_file:
        persons_payload = load_json(args.persons_file)
        persons = persons_payload.get("persons", [])
    xml = build_unimarc_xml(metadata, persons)
    write_json_stdout({
        "xml": xml,
        "fields_written": sorted(set(["101", "200", "210", "328", "330", "686", "700", "701", "702", "712"])),
        "error": None,
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
