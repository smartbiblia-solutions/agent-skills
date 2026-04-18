#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from lib.common import load_json, person_to_access_point, write_json_stdout


def stable_ppn(name: str) -> str:
    digest = hashlib.sha1(name.encode("utf-8")).hexdigest()
    return str(int(digest[:9], 16))[:9]


def add_person(role: str, name: str, persons: list[dict], ambiguous: bool = False) -> None:
    if not name:
        return
    persons.append({
        "role": role,
        "name": name,
        "normalized_form": person_to_access_point(name),
        "ppn": None if ambiguous else stable_ppn(name),
        "match_confidence": "ambiguous" if ambiguous else "strong",
        "explanation": "aucune autorité IdRef pertinente trouvée" if ambiguous else "Alignement heuristique local en attente d'un branchement IdRef réel.",
    })


def main() -> int:
    parser = argparse.ArgumentParser(description="Enrichissement local des personnes avec structure IdRef simulée.")
    parser.add_argument("--json-file", required=True, help="Chemin du JSON de métadonnées.")
    parser.add_argument("--ambiguous-names", nargs="*", default=[], help="Liste de noms à marquer comme ambigus.")
    args = parser.parse_args()

    payload = load_json(args.json_file)
    metadata = payload.get("metadata", payload)
    ambiguous = set(args.ambiguous_names)
    persons: list[dict] = []
    add_person("author", metadata.get("author", ""), persons, metadata.get("author", "") in ambiguous)
    for name in metadata.get("advisor", []):
        add_person("advisor", name, persons, name in ambiguous)
    for name in metadata.get("jury_president", []):
        add_person("jury_president", name, persons, name in ambiguous)
    for name in metadata.get("reviewers", []):
        add_person("reviewer", name, persons, name in ambiguous)
    already_named = {p["name"] for p in persons}
    for name in metadata.get("committee_members", []):
        if name not in already_named:
            add_person("committee_member", name, persons, name in ambiguous)
    write_json_stdout({"persons": persons, "error": None})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
