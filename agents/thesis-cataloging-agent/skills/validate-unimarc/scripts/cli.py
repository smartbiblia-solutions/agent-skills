#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from lib.common import load_json, validate_unimarc_xml, write_json_stdout


def main() -> int:
    parser = argparse.ArgumentParser(description="Validation locale d'UNIMARC XML.")
    parser.add_argument("--json-file", help="JSON contenant une clé xml.")
    parser.add_argument("--xml-file", help="Fichier XML direct.")
    args = parser.parse_args()

    if args.xml_file:
        xml_text = Path(args.xml_file).read_text(encoding="utf-8")
    else:
        payload = load_json(args.json_file)
        xml_text = payload["xml"]
    errors, warnings, checked_fields = validate_unimarc_xml(xml_text)
    write_json_stdout({
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "checked_fields": checked_fields,
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
