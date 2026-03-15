# llm.md guide — documenting a data source API for skill creation

A `llm.md` is a condensed, LLM-optimized reference document for a data source
API. It captures everything an agent needs to use the API correctly, without
the noise of a full developer documentation site.

Store it at: `skills/<skill-name>/references/llm.md`
It is **not packaged** in the `.skill` file — it stays in the repo for maintenance.

---

## When to produce a llm.md

Produce one when:
- The API has non-obvious behavior (encoding quirks, case-sensitive paths, etc.)
- The API has a rich query language that needs to be documented for reliable use
- The data model differs from the hub's common record schema and normalization rules are needed
- Official documentation is scattered across multiple pages

Skip it when:
- The API is a simple REST endpoint with self-evident parameters
- The skill wraps a well-known service already covered by the agent's training data

---

## How to produce a llm.md

### Step 1 — Fetch the documentation

```bash
# Official docs page
# OpenAPI/Swagger spec if available
# Any LLM-optimized page (e.g. https://developers.openalex.org/guides/llm-quick-reference)
```

Prioritize:
1. An official LLM-optimized page (like OpenAlex's `/llm.txt`) — use it directly as the base
2. An OpenAPI spec — extract endpoints, parameters, and response schemas
3. The main documentation site — read the key pages and synthesize

### Step 2 — Extract the essential information

For each API, capture:

- **Base URL and endpoint structure**
- **Authentication** (required / optional / none)
- **Key parameters** with types, defaults, and valid values
- **Non-obvious behavior** — encoding rules, case sensitivity, pagination, rate limits
- **Response structure** — the raw response schema before normalization
- **Field mapping** — how raw response fields map to the hub common record schema
- **Error behavior** — how errors are signaled (status codes, error fields, always-200 APIs)
- **Rate limits and retry guidance**

---

## llm.md template

```markdown
# <Source name> — LLM reference

> Condensed API reference for skill creation and maintenance.
> Generated: <date>
> Source docs: <URL>

---

## API overview

- **Base URL**: `https://...`
- **Protocol**: REST / SRU / Solr / GraphQL
- **Authentication**: none required | API key (optional/required) | OAuth
- **Rate limits**: <N> requests/second, or none published
- **Response format**: JSON | XML | UNIMARC/XML
- **Encoding notes**: <any non-standard encoding behavior>

---

## Endpoints

### <Endpoint name>

**URL pattern**: `GET <base>/<path>?<params>`

**Key parameters**:

| Parameter | Type | Default | Notes |
|---|---|---|---|
| `param1` | string | **required** | Description |
| `param2` | int | `15` | Max value: 200 |

**Non-obvious behavior**:
- <encoding quirk, case sensitivity, etc.>
- <pagination logic>

**Response structure**:
```json
{
  "field1": "...",
  "nested": {
    "items": []
  }
}
```

---

## Field mapping to hub common record schema

| Hub field | Source field | Notes |
|---|---|---|
| `id` | `<source_id_field>` | |
| `title` | `<title_field>` | May be an array — take first element |
| `authors` | `<authors_field>` | May need flattening |
| `abstract` | `<abstract_field>` | Null if not present |
| `doi` | `<doi_field>` | Strip `https://doi.org/` prefix if present |
| `pdf_url` | `<pdf_field>` | Null if not open access |
| `url` | `<url_field>` | |
| `year` | `<year_field>` | Cast to int |
| `date` | `<date_field>` | ISO 8601 string or null |
| `doc_type` | `<type_field>` | |
| `journal` | `<journal_field>` | Null if not applicable |

Source-specific fields to preserve alongside the common schema:
- `<source>_id`: `<native_id_field>`
- `<other_field>`: `<source_field>`

---

## Error handling

- **HTTP errors**: retried on <status codes>
- **Application errors**: <how errors are returned — error field, always-200, etc.>
- **Not found**: <behavior when a record doesn't exist>

---

## Known quirks and gotchas

- <Quirk 1>
- <Quirk 2>

---

## Useful query examples

```bash
# <Description>
curl "<URL>"

# <Description>
curl "<URL>"
```
```

---

## Real examples from the hub

### HAL llm.md — key sections

The HAL skill's llm.md would capture:

```markdown
## Non-obvious behavior

- HAL Search API uses Apache Solr. The query language is Solr's (`q`, `fq`, `fl`, `facet.*`).
- Path routing is case-sensitive:
  - `/search/tel/` → portal instance (lowercase)
  - `/search/FRANCE-GRILLES/` → collection (typically uppercase)
- Collection-first design: most real usage targets `/search/{COLLECTION}/` not the global endpoint.
- `--wt bibtex` is valid but returns non-JSON — the CLI surfaces the Solr URL
  in an error payload so the caller can fetch it directly.

## Field mapping

| Hub field | HAL field | Notes |
|---|---|---|
| `id` | `halId_s` | |
| `title` | `title_s` or `title_t` | `title_s` preferred |
| `authors` | `authFullName_s` | May be string or array — normalize to array |
| `abstract` | `abstract_s` or `abstract_t` | Often null |
| `doi` | `doiId_s` | |
| `pdf_url` | `fileMain_s` or `openAccessFile_s` | Best-effort OA URL |
| `year` | `publicationDateY_i` | Cast to int |
| `date` | `publicationDate_s` or `producedDate_s` | |
| `doc_type` | `docType_s` | e.g. ART, THESE, COMM |
| `journal` | `journalTitle_s` | |
```

### Sudoc llm.md — key sections

```markdown
## Non-obvious behavior

- SRU 1.1 protocol (not REST). Queries use CQL-like syntax but with Sudoc-specific indexes.
- CRITICAL encoding rule: `=` must be encoded as `%3D` inside every index=term pair.
  Other characters: `|` → `%7C`, `"` → `%22`, `,` → `%2C`, `/` → `%2F`, space → `+`.
  The CLI handles this automatically.
- Two separate limitation sets for language and country (major vs. full ISO lists).
  `--lang-major` uses the LAN limitation (10 major languages).
  `--language` uses the LAI limitation (all ISO 639-2/3 codes).
  Do not mix them for the same language.
- Response format: UNIMARC encapsulated in XML (UTF-8). Requires XML parsing of UNIMARC fields.
- Exit code is always 0 — errors returned in the `error` field.
- The `scan` operation browses an index alphabetically — useful for debugging zero-result queries.
```