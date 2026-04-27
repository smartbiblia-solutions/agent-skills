---
name: search-authorities-idref
description: >
  Search and retrieve authority records from IdRef (ABES) using the Solr API,
  and fetch linked bibliographic references through IdRef micro web services.
  Use this skill whenever the user asks to find an IdRef authority, search French
  authority data for persons, organizations, subjects, conferences, or places,
  retrieve an authority by PPN, or inspect bibliographic references linked to an
  authority. Prefer this skill over generic web search when the target is IdRef
  or French academic authority control.
metadata:
  {
    "version": "0.1.0",
    "author": "smartbiblia",
    "maturity": "stable",
    "preferred_output": "json",
    "openclaw": { "requires": { "bins": ["uv"] } }
  }

selection:
  use_when:
    - The task is to search IdRef authority records by name, title, subject, affiliation, or expert Solr query.
    - The user provides an IdRef PPN and wants the authority record or linked references.
    - The task concerns French academic authority data maintained by ABES.
  avoid_when:
    - The task is broad scholarly article discovery rather than authority control.
    - The task requires library holdings or bibliographic catalog search rather than authority search.
  prefer_over:
    - generic-web-search
  combine_with:
    - search-records-sudoc
    - search-records-hal

tags:
  - idref
  - authorities
  - abes
  - france
  - library
  - scholarly
---

# IdRef authorities

## Purpose

`skills/search-authorities-idref/scripts/cli.py` is a self-contained CLI (runs with `uv run`) that wraps two parts of the IdRef developer surface:

- the **Solr authority search endpoint** at `https://www.idref.fr/Sru/Solr`
- the **micro web service** `references` endpoint at `https://www.idref.fr/services/references/<PPN>.json`

It emits **strict JSON on stdout** and is designed for agent use.

This skill exposes three logical operations through CLI subcommands. These are not separate skills; they are entry points of the single skill `search-authorities-idref`:

| Logical operation | CLI subcommand | Purpose |
|---|---|---|
| authority search | `search` | Search IdRef authorities with a simple or expert Solr query |
| authority lookup by PPN | `get` | Retrieve a single authority by PPN using a precise Solr lookup |
| linked bibliographic references | `references` | Fetch linked bibliographic references grouped by role |

## When to use / When not to use

Use this skill when the user wants IdRef authority records for people, organizations, conferences, places, titles, Rameau subjects, or related French authority data.

Do not use it when:
- The task is to search bibliographic records themselves rather than authority records.
- The task targets general scholarly literature discovery across many sources.
- The user only needs a public webpage snippet and not structured IdRef data.

## Subcommands

### `search` — authority search via Solr

```bash
uv run skills/search-authorities-idref/scripts/cli.py search \
  --query 'persname_t:(Bourdieu AND Pierre)' \
  --max-results 5
```

Or build a simple search without writing raw Solr:

```bash
uv run skills/search-authorities-idref/scripts/cli.py search \
  --index persname_t \
  --text 'Victor Hugo' \
  --max-results 5
```

| Flag | Type | Default | Notes |
|---|---|---|---|
| `--query` | string | — | Raw Solr query. Mutually exclusive with `--index` + `--text`. |
| `--index` | string | `all` | Solr index, e.g. `persname_t`, `corpname_t`, `all`, `ppn_z`. |
| `--text` | string | — | Plain text to search in the chosen index. |
| `--max-results` | int | `10` | Max rows returned. |
| `--start` | int | `0` | Offset for pagination. |
| `--sort` | string | `score desc` | Example: `affcourt_z asc`. |
| `--fields` | comma list | `id,ppn_z,recordtype_z,affcourt_z` | Solr `fl` parameter. |

### `get` — fetch one authority by PPN

```bash
uv run skills/search-authorities-idref/scripts/cli.py get --ppn 027715078
```

This performs a Solr lookup with `q=ppn_z:<PPN>` and returns the first matching authority plus the public IdRef page URL.

### `references` — bibliographic references linked to an authority

```bash
uv run skills/search-authorities-idref/scripts/cli.py references --ppn 02686018X
```

Returns grouped reference data from `services/references/<PPN>.json`.

| Flag | Type | Default | Notes |
|---|---|---|---|
| `--ppn` | string | — | Required IdRef PPN |
| `--max-roles` | int | unlimited | Limit number of role groups returned |
| `--max-docs-per-role` | int | `10` | Limit documents included in each role group |

## Output

### Search / get

```jsonc
{
  "source": "idref",
  "query": "persname_t:(Bourdieu AND Pierre)",
  "total_found": 1,
  "returned": 1,
  "start": 0,
  "results": [
    {
      "source": "idref",
      "id": "027715078",
      "ppn": "027715078",
      "title": "Bourdieu, Pierre (1930-2002)",
      "authors": null,
      "abstract": null,
      "doi": null,
      "pdf_url": null,
      "url": "https://www.idref.fr/027715078",
      "year": null,
      "date": null,
      "doc_type": "a",
      "journal": null,
      "recordtype": "a",
      "solr_id": "91588"
    }
  ],
  "error": null
}
```

### References

```jsonc
{
  "source": "idref",
  "ppn": "02686018X",
  "roles": [
    {
      "role_name": "Auteur",
      "marc21_code": "aut",
      "unimarc_code": "070",
      "count": 146,
      "docs": [
        {
          "citation": "Commanditaire, auteur, artiste dans les inscriptions médiévales / Robert Favreau",
          "referentiel": "sudoc",
          "id": "189894652",
          "ppn": "189894652",
          "url": "https://www.sudoc.fr/189894652",
          "uri": "https://www.sudoc.fr/189894652/id"
        }
      ]
    }
  ],
  "error": null
}
```

Always check the `error` field.

## Composition hints

```text
search-authorities-idref        ← this skill
  → subcommand `search`
  → subcommand `get`
  → subcommand `references`
  → search-records-sudoc
```

Useful pattern:

```text
search-authorities-idref (subcommand `search`)      ← identify a person or organization in IdRef
  → search-authorities-idref (subcommand `references`) ← inspect linked bibliography
  → search-records-sudoc                              ← expand to catalog records if needed
```

## Environment variables

Set in `skills/search-authorities-idref/.env` or export in the shell.

| Variable | Default | Purpose |
|---|---|---|
| `IDREF_HTTP_TIMEOUT` | `20.0` | Seconds before timeout |
| `IDREF_MAX_RETRIES` | `2` | Total attempts per request |
| `IDREF_BACKOFF_BASE` | `1.0` | Base seconds for retry backoff |
| `IDREF_BACKOFF_FACTOR` | `2.0` | Backoff multiplier |
| `IDREF_JITTER_MAX` | `0.25` | Max random jitter in seconds |
| `IDREF_TRACE` | `0` | Set to `1` for HTTP trace logging |

Retried status codes: 429, 500, 502, 503, 504.

## Failure modes

- **Exit code always 0 on handled API failures**: inspect the `error` field.
- **No authority found**: returns zero results with `error: null` for search, or `result: null` for `get`.
- **Invalid or missing PPN**: the references service may return non-JSON or a 404-like response; the CLI surfaces this in `error`.
- **Solr query mistakes**: malformed expert queries are returned as an error payload.
- **Field variability**: IdRef Solr fields can be sparse; many normalized fields are `null`.

## Files

- `scripts/cli.py` — self-contained CLI wrapper
- `references/llm.md` — condensed IdRef API reference for maintenance
