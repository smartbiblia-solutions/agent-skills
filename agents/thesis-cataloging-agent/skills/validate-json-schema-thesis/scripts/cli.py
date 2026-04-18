#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from lib.common import load_json, validate_metadata, write_json_stdout


def main() -> int:
    parser = argparse.ArgumentParser(description="Validation du JSON de thèse.")
    parser.add_argument("--json-file", required=True, help="Chemin du JSON à valider.")
    args = parser.parse_args()

    payload = load_json(args.json_file)
    metadata = payload.get("metadata", payload)
    issues, warnings = validate_metadata(metadata)
    write_json_stdout({
        "valid": len([i for i in issues if i.level == "error"]) == 0,
        "errors": [{"path": i.path, "message": i.message} for i in issues],
        "warnings": warnings,
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
