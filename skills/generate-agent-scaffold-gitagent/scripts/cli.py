#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMPT_PATH = ROOT / "prompts" / "prompt.md"
SCHEMA_PATH = ROOT / "schemas" / "output.schema.json"


def load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def validate_payload(payload: dict) -> list[str]:
    errors: list[str] = []

    required_top = {
        "agent_name",
        "template",
        "gitagent_spec_version",
        "summary",
        "directories",
        "files",
        "assumptions",
        "next_steps",
    }
    missing = sorted(required_top - payload.keys())
    if missing:
        errors.append(f"missing top-level fields: {', '.join(missing)}")

    if not isinstance(payload.get("agent_name"), str) or not payload.get("agent_name"):
        errors.append("agent_name must be a non-empty string")
    elif payload["agent_name"].startswith("/") or "_" in payload["agent_name"]:
        errors.append("agent_name must be relative and use kebab-case, not snake_case")

    if payload.get("template") not in {"minimal", "standard", "full"}:
        errors.append("template must be one of: minimal, standard, full")

    if not isinstance(payload.get("gitagent_spec_version"), str):
        errors.append("gitagent_spec_version must be a string")

    if not isinstance(payload.get("summary"), str) or not payload.get("summary"):
        errors.append("summary must be a non-empty string")

    directories = payload.get("directories")
    if not isinstance(directories, list):
        errors.append("directories must be an array")
    else:
        for index, entry in enumerate(directories):
            if not isinstance(entry, dict):
                errors.append(f"directories[{index}] must be an object")
                continue
            for field in ("path", "purpose", "required"):
                if field not in entry:
                    errors.append(f"directories[{index}] missing field: {field}")
            if isinstance(entry.get("path"), str) and entry["path"].startswith("/"):
                errors.append(f"directories[{index}].path must be relative")

    files = payload.get("files")
    if not isinstance(files, list) or len(files) < 2:
        errors.append("files must be an array with at least 2 entries")
    else:
        paths = set()
        has_agent_yaml = False
        has_soul = False
        for index, entry in enumerate(files):
            if not isinstance(entry, dict):
                errors.append(f"files[{index}] must be an object")
                continue
            for field in ("path", "purpose", "required", "content"):
                if field not in entry:
                    errors.append(f"files[{index}] missing field: {field}")
            path = entry.get("path")
            if isinstance(path, str):
                if path.startswith("/"):
                    errors.append(f"files[{index}].path must be relative")
                if path in paths:
                    errors.append(f"files[{index}].path duplicates another file path: {path}")
                paths.add(path)
                if path == "agent.yaml":
                    has_agent_yaml = True
                if path == "SOUL.md":
                    has_soul = True
        if not has_agent_yaml:
            errors.append("files must include agent.yaml")
        if not has_soul:
            errors.append("files must include SOUL.md")

    for field in ("assumptions", "next_steps"):
        value = payload.get(field)
        if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
            errors.append(f"{field} must be an array of strings")

    return errors


def cmd_prompt(_: argparse.Namespace) -> int:
    sys.stdout.write(load_prompt())
    return 0


def cmd_schema(_: argparse.Namespace) -> int:
    json.dump(load_schema(), sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    try:
        payload = json.loads(Path(args.json_file).read_text(encoding="utf-8"))
    except FileNotFoundError:
        result = {"ok": False, "errors": [f"file not found: {args.json_file}"]}
        json.dump(result, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0
    except json.JSONDecodeError as exc:
        result = {"ok": False, "errors": [f"invalid JSON: {exc.msg} at line {exc.lineno} column {exc.colno}"]}
        json.dump(result, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    errors = validate_payload(payload)
    result = {"ok": not errors, "errors": errors}
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Expose the prompt and schema for generate-agent-scaffold-gitagent."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    prompt_parser = subparsers.add_parser("prompt", help="Print the prompt contract.")
    prompt_parser.set_defaults(func=cmd_prompt)

    schema_parser = subparsers.add_parser("schema", help="Print the JSON schema.")
    schema_parser.set_defaults(func=cmd_schema)

    validate_parser = subparsers.add_parser("validate", help="Validate a JSON output file.")
    validate_parser.add_argument("--json-file", required=True, help="Path to the JSON output to validate.")
    validate_parser.set_defaults(func=cmd_validate)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
