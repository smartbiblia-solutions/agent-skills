#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = ['python-dotenv']
# ///

from __future__ import annotations

# ══════════════════════════════════════════════════════════════════════════════
# SECTION : core
# ══════════════════════════════════════════════════════════════════════════════

import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()


def get_agent_name() -> str:
    """Return the configured orchestrator name used by CLI and MCP wrappers."""
    return os.getenv("LITERATURE_REVIEW_AGENT_NAME", "literature-review-agent")


def list_pipeline_steps() -> list[dict[str, str]]:
    """Return the canonical high-level workflow steps for literature review orchestration."""
    return [
        {"id": "search_references", "summary": "Build queries, retrieve papers, and deduplicate records."},
        {"id": "analyze_papers", "summary": "Screen papers and summarize included studies."},
        {"id": "synthesize_corpus", "summary": "Build thematic, chronological, methodological, or PRISMA synthesis."},
        {"id": "save_to_zotero", "summary": "Optionally export included records to Zotero."},
    ]


def get_step(step_id: str) -> dict[str, Any]:
    """Return a step definition by id, or an error payload if the step is unknown."""
    for step in list_pipeline_steps():
        if step["id"] == step_id:
            return step
    return {"error": f"Unknown step: {step_id}", "available_steps": [s["id"] for s in list_pipeline_steps()]}

# ══════════════════════════════════════════════════════════════════════════════
# SECTION : facade
# ══════════════════════════════════════════════════════════════════════════════

import argparse
import json


def main() -> int:
    ap = argparse.ArgumentParser(prog="literature-review-agent")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("name", help="Print agent name")
    sub.add_parser("steps", help="List canonical pipeline steps")
    p_step = sub.add_parser("step", help="Get one step by id")
    p_step.add_argument("--id", required=True)

    args = ap.parse_args()

    if args.cmd == "name":
        print(json.dumps({"name": get_agent_name()}, ensure_ascii=False, indent=2))
        return 0
    if args.cmd == "steps":
        print(json.dumps({"steps": list_pipeline_steps()}, ensure_ascii=False, indent=2))
        return 0
    if args.cmd == "step":
        print(json.dumps(get_step(args.id), ensure_ascii=False, indent=2))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
