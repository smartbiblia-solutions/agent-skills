#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

SOLR_URL = "https://www.idref.fr/Sru/Solr"
REFERENCES_URL = "https://www.idref.fr/services/references/{ppn}.json"
DEFAULT_FIELDS = ["id", "ppn_z", "recordtype_z", "affcourt_z"]
RETRYABLE = {429, 500, 502, 503, 504}


def env_float(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, default))
    except Exception:
        return default


def env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except Exception:
        return default


TIMEOUT = env_float("IDREF_HTTP_TIMEOUT", 20.0)
MAX_RETRIES = env_int("IDREF_MAX_RETRIES", 2)
BACKOFF_BASE = env_float("IDREF_BACKOFF_BASE", 1.0)
BACKOFF_FACTOR = env_float("IDREF_BACKOFF_FACTOR", 2.0)
JITTER_MAX = env_float("IDREF_JITTER_MAX", 0.25)
TRACE = os.environ.get("IDREF_TRACE", "0") == "1"


def trace(msg: str) -> None:
    if TRACE:
        print(f"[idref] {msg}", file=sys.stderr)


def json_out(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def sleep_backoff(attempt: int) -> None:
    delay = BACKOFF_BASE * (BACKOFF_FACTOR ** max(0, attempt - 1)) + random.uniform(0, JITTER_MAX)
    time.sleep(delay)


def http_get_json(url: str, headers: dict[str, str] | None = None) -> tuple[Any | None, str | None, int | None]:
    hdrs = {"User-Agent": "nanobot-idref-skill/0.1"}
    if headers:
        hdrs.update(headers)
    last_error = None
    for attempt in range(1, MAX_RETRIES + 2):
        try:
            trace(f"GET {url}")
            req = urllib.request.Request(url, headers=hdrs, method="GET")
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                status = getattr(resp, "status", 200)
                body = resp.read().decode("utf-8", "replace")
                return json.loads(body), None, status
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace") if hasattr(e, "read") else ""
            last_error = f"HTTP {e.code}: {body[:400]}".strip()
            if e.code in RETRYABLE and attempt <= MAX_RETRIES + 1:
                sleep_backoff(attempt)
                continue
            return None, last_error, e.code
        except urllib.error.URLError as e:
            last_error = f"Network error: {e.reason}"
            if attempt <= MAX_RETRIES + 1:
                sleep_backoff(attempt)
                continue
            return None, last_error, None
        except json.JSONDecodeError as e:
            return None, f"Invalid JSON response: {e}", None
        except Exception as e:
            return None, f"Unexpected error: {e}", None
    return None, last_error or "Unknown error", None


def normalize_doc(doc: dict[str, Any]) -> dict[str, Any]:
    ppn = doc.get("ppn_z") or doc.get("ppn") or doc.get("id")
    title = doc.get("affcourt_z") or doc.get("affcourt_r") or doc.get("title")
    recordtype = doc.get("recordtype_z")
    return {
        "source": "idref",
        "id": ppn,
        "ppn": ppn,
        "title": title,
        "authors": None,
        "abstract": None,
        "doi": None,
        "pdf_url": None,
        "url": f"https://www.idref.fr/{ppn}" if ppn else None,
        "year": None,
        "date": None,
        "doc_type": recordtype,
        "journal": None,
        "recordtype": recordtype,
        "solr_id": doc.get("id"),
        "raw": doc,
    }


def build_query(index: str | None, text: str | None, query: str | None) -> str:
    if query:
        return query
    if not text:
        raise ValueError("Either --query or --text must be provided")
    idx = index or "all"
    if " " in text:
        return f'{idx}:({" AND ".join(text.split())})'
    return f"{idx}:{text}"


def cmd_search(args: argparse.Namespace) -> int:
    try:
        q = build_query(args.index, args.text, args.query)
    except Exception as e:
        json_out({"source": "idref", "query": None, "total_found": 0, "returned": 0, "start": 0, "results": [], "error": str(e)})
        return 0

    params = {
        "q": q,
        "wt": "json",
        "sort": args.sort,
        "version": "2.2",
        "start": str(args.start),
        "rows": str(args.max_results),
        "indent": "on",
        "fl": ",".join(args.fields),
    }
    url = SOLR_URL + "?" + urllib.parse.urlencode(params, safe=",:() ").replace(" ", "%20")
    data, error, _status = http_get_json(url)
    if error:
        json_out({"source": "idref", "query": q, "total_found": 0, "returned": 0, "start": args.start, "results": [], "error": error})
        return 0

    response = (data or {}).get("response", {})
    docs = response.get("docs", []) or []
    results = [normalize_doc(d) for d in docs if isinstance(d, dict)]
    json_out({
        "source": "idref",
        "query": q,
        "total_found": int(response.get("numFound", 0) or 0),
        "returned": len(results),
        "start": int(response.get("start", args.start) or 0),
        "results": results,
        "error": None,
    })
    return 0


def cmd_get(args: argparse.Namespace) -> int:
    ppn = args.ppn.strip()
    params = {
        "q": f"ppn_z:{ppn}",
        "wt": "json",
        "sort": "score desc",
        "version": "2.2",
        "start": "0",
        "rows": "1",
        "indent": "on",
        "fl": ",".join(args.fields),
    }
    url = SOLR_URL + "?" + urllib.parse.urlencode(params, safe=",:() ").replace(" ", "%20")
    data, error, _status = http_get_json(url)
    if error:
        json_out({"source": "idref", "ppn": ppn, "result": None, "error": error})
        return 0

    docs = (((data or {}).get("response") or {}).get("docs") or [])
    result = normalize_doc(docs[0]) if docs else None
    json_out({"source": "idref", "ppn": ppn, "result": result, "error": None})
    return 0


def ensure_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def cmd_references(args: argparse.Namespace) -> int:
    ppn = args.ppn.strip()
    url = REFERENCES_URL.format(ppn=urllib.parse.quote(ppn))
    data, error, _status = http_get_json(url, headers={"Accept": "application/json, text/json;q=0.9"})
    if error:
        json_out({"source": "idref", "ppn": ppn, "roles": [], "error": error})
        return 0

    envelope = None
    if isinstance(data, dict):
        envelope = data.get("sudoc") or next(iter(data.values()), None)
    result = (envelope or {}).get("result", {}) if isinstance(envelope, dict) else {}
    roles_raw = ensure_list(result.get("role"))
    if args.max_roles is not None:
        roles_raw = roles_raw[: args.max_roles]
    roles = []
    for role in roles_raw:
        if not isinstance(role, dict):
            continue
        docs = []
        role_docs = ensure_list(role.get("doc"))
        if args.max_docs_per_role is not None:
            role_docs = role_docs[: args.max_docs_per_role]
        for d in role_docs:
            if isinstance(d, dict):
                docs.append({
                    "citation": d.get("citation"),
                    "referentiel": d.get("referentiel"),
                    "id": d.get("id"),
                    "ppn": d.get("ppn"),
                    "url": d.get("URL"),
                    "uri": d.get("URI"),
                    "raw": d,
                })
        roles.append({
            "role_name": role.get("roleName"),
            "marc21_code": role.get("marc21Code"),
            "unimarc_code": role.get("unimarcCode"),
            "count": int(role.get("count", 0) or 0),
            "docs": docs,
        })
    json_out({"source": "idref", "ppn": ppn, "roles": roles, "error": None})
    return 0




def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="IdRef authority search and references CLI")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("search", help="Search IdRef authorities via Solr")
    s.add_argument("--query", help="Raw Solr query")
    s.add_argument("--index", default="all", help="Solr index for simple search")
    s.add_argument("--text", help="Simple text for index search")
    s.add_argument("--max-results", type=int, default=10)
    s.add_argument("--start", type=int, default=0)
    s.add_argument("--sort", default="score desc")
    s.add_argument("--fields", nargs="+", default=DEFAULT_FIELDS)
    s.set_defaults(func=cmd_search)

    g = sub.add_parser("get", help="Fetch one authority by PPN")
    g.add_argument("--ppn", required=True)
    g.add_argument("--fields", nargs="+", default=DEFAULT_FIELDS)
    g.set_defaults(func=cmd_get)

    r = sub.add_parser("references", help="Fetch linked bibliographic references by PPN")
    r.add_argument("--ppn", required=True)
    r.add_argument("--max-roles", type=int, default=None)
    r.add_argument("--max-docs-per-role", type=int, default=10)
    r.set_defaults(func=cmd_references)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
