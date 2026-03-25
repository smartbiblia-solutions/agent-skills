---
name: explore_dataset
description: >
  Perform exploratory data analysis (EDA) on any tabular dataset and produce
  interactive HTML dashboards. Accepts CSV, TSV, JSON, and Excel files —
  including outputs from hub retrieval skills (search-works-openalex,
  search-records-hal, search-records-sudoc). Produces two outputs: a JSON
  metrics report for downstream pipeline use, and a standalone interactive
  HTML dashboard (no server required, opens directly in a browser). Use this
  skill whenever the task involves understanding the shape, distribution,
  quality, or trends in a dataset — before synthesis, before modelling, or
  as a standalone deliverable. Trigger on phrases like "explore this dataset",
  "analyse these records", "show me the distribution of", "build a dashboard
  for", "what are the trends in", "data quality report", "EDA on".
metadata: {"version": "0.1.0", "author": "smartbiblia", "maturity": "experimental", "preferred_output": "html", "openclaw": {"emoji": "📊", "requires": {"bins": ["uv"]}}}

selection:
  use_when:
    - The task is to understand the shape, quality, or distribution of a dataset.
    - The user wants an interactive visualization of tabular data.
    - The input is an output from a hub retrieval skill and needs to be explored before synthesis.
    - A publication trend, author distribution, or topic breakdown is requested.
  avoid_when:
    - The task is to synthesize the content of papers — use synthesize-literature instead.
    - The task is to compute bibliometrics on a pre-defined corpus schema — use analyze-corpus instead (if available).
  combine_with:
    - search-works-openalex
    - search-records-hal
    - search-records-sudoc
    - synthesize-literature

tags:
  - eda
  - dataviz
  - dashboard
  - analytics
  - tabular
---

# explore-dataset

## Purpose

A two-output analytical skill: given any tabular dataset, it produces a **JSON
metrics report** (structured, pipeline-ready) and a **standalone interactive
HTML dashboard** (self-contained, opens in any browser, no server needed).

The skill is generalist — it works on any tabular data. It has built-in
awareness of hub record schemas (OpenAlex, HAL, Sudoc outputs) and applies
domain-relevant analyses automatically when it detects those schemas. For
all other datasets it falls back to universal EDA patterns.

The CLI (`scripts/cli.py`) handles data loading, schema detection, metrics
computation, and HTML generation. The agent drives the analysis by reading
the prompt contract and selecting the appropriate analysis profile.

---

## When to use / When not to use

Use this skill at any point where understanding the data matters: before
deciding which papers to synthesize, after a retrieval to assess corpus
quality, or as a standalone deliverable for a stakeholder who wants a
visual overview.

Do not use it when the task is to read and synthesize paper content — that
is `synthesize-literature`. This skill operates on the metadata and structure
of the dataset, not on the intellectual content of documents.

---

## Input formats

| Format | Extension | Notes |
|---|---|---|
| CSV | `.csv` | Auto-detected delimiter (`,` or `;`) |
| TSV | `.tsv` | Tab-separated |
| JSON | `.json` | Array of objects or newline-delimited JSON |
| Excel | `.xlsx`, `.xls` | First sheet by default; `--sheet` to override |
| Parquet | `.parquet` | |
| Arrow / Feather | `.arrow`, `.feather` | |

JSON arrays from hub retrieval skills are accepted directly — the CLI detects
the `results[]` array automatically and flattens it.

---

## Analysis profiles

The CLI detects the dataset schema and applies the appropriate profile.
Override with `--profile` if auto-detection is wrong.

| Profile | Auto-detected when | Key analyses |
|---|---|---|
| `hub-records` | Fields `source`, `doi`, `year`, `authors` are present | Publications by year, top authors, top journals, OA rate, doc type distribution, topic breakdown |
| `tabular-generic` | Any other tabular structure | Shape, dtypes, missing values, numeric distributions, categorical frequencies, correlations |

Both profiles always produce: row count, column inventory, missing value
report, and at least one time-series chart if a date/year column is found.

---

## CLI usage

```bash
# Basic usage — produces .metrics.json + .summary.md + .dashboard.html
uv run skills/explore-dataset/scripts/cli.py \
  --input $WORKSPACE/openalex_results.json \
  --output-dir $WORKSPACE/explore-output/

# Explicit profile and sheet selection
uv run skills/explore-dataset/scripts/cli.py \
  --input data.xlsx \
  --sheet "Sheet2" \
  --profile tabular-generic \
  --output-dir $WORKSPACE/explore-output/

# JSON metrics only (no HTML)
uv run skills/explore-dataset/scripts/cli.py \
  --input records.csv \
  --output-dir $WORKSPACE/explore-output/ \
  --no-html

# HTML only (skip JSON metrics file)
uv run skills/explore-dataset/scripts/cli.py \
  --input records.csv \
  --output-dir $WORKSPACE/explore-output/ \
  --no-json
```

| Flag | Type | Default | Notes |
|---|---|---|---|
| `--input` | path | **required** | Input file — CSV, TSV, JSON, or Excel |
| `--output-dir` | path | **required** | Directory for output files |
| `--profile` | string | auto | `hub-records` or `tabular-generic` |
| `--sheet` | string | first sheet | Excel sheet name or index |
| `--title` | string | filename | Dashboard title shown in the HTML |
| `--max-categories` | int | `20` | Max categories shown in bar charts |
| `--no-html` | flag | off | Skip HTML generation |
| `--no-json` | flag | off | Skip JSON metrics file |
| `--no-md` | flag | off | Skip Markdown summary |
| `--trace` | flag | off | Print debug info to stderr |

---

## Output

All three files are written to `--output-dir`.

### Markdown summary — `<input-stem>.summary.md`

A concise narrative report (5–15 lines) covering: row/column count, missing
data rate, numeric column highlights, top categorical values, and — for
hub-records — open access rate, publication span, top authors, journals, and
topics. Readable without tooling, commitable as documentation.

---

### JSON metrics report — `<input-stem>.metrics.json`

```jsonc
{
  "profile": "hub-records",
  "input_file": "openalex_results.json",
  "generated_at": "2025-03-15T14:32:00Z",
  "shape": {"rows": 142, "columns": 14},
  "columns": [
    {"name": "year", "dtype": "int", "missing": 0, "unique": 7},
    {"name": "doi",  "dtype": "str", "missing": 12, "unique": 130}
  ],
  "missing_summary": {"total_missing_cells": 34, "columns_with_missing": ["doi", "abstract"]},
  "numeric_stats": {
    "year": {"min": 2018, "max": 2024, "mean": 2022.3, "median": 2023}
  },
  "categorical_stats": {
    "doc_type": {"article": 98, "preprint": 31, "review": 13},
    "source":   {"openalex": 142}
  },
  "hub_metrics": {
    "open_access_rate": 0.73,
    "top_authors": [{"name": "…", "count": 7}],
    "top_journals": [{"name": "…", "count": 14}],
    "top_topics": [{"topic": "…", "count": 23}],
    "publications_by_year": {"2018": 8, "2019": 14, "2020": 18, "2021": 22, "2022": 31, "2023": 49}
  }
}
```

`hub_metrics` is only present for the `hub-records` profile.

### HTML dashboard — `<input-stem>.dashboard.html`

A single self-contained HTML file with embedded CSS and JS (Plotly via CDN).
No server, no build step — open directly in any browser.

Contains:
- Dataset summary card (rows, columns, profile, missing rate)
- For `hub-records`: publications by year (line), top authors (bar), top
  journals (bar), doc type distribution (pie), OA rate gauge, topic cloud
- For `tabular-generic`: column overview table, numeric distributions
  (histograms), categorical frequencies (bar), correlation heatmap (if ≥2
  numeric columns), missing values heatmap

All charts are interactive (hover, zoom, filter via Plotly).

---

## Prompt contract

Before running the CLI, read the analysis intent from the user and determine:

1. **What question is being asked?** Distribution, trend, quality, comparison,
   outlier detection — each implies different charts to highlight.
2. **What is the audience?** Technical (show all metrics) vs non-technical
   (narrative summary + key charts only).
3. **Is there a domain context?** If the dataset is hub records, activate
   domain-specific metrics (OA rate, RAMEAU subjects, etc.).

Then run the CLI and, after it completes:
- Read the JSON metrics file.
- Produce a short narrative summary (3–5 sentences) of the key findings
  to accompany the HTML dashboard.
- Point the user to the HTML file path.

---

## Composition hints

As a standalone EDA step before synthesis:

```
search-works-openalex
  → explore-dataset          ← this skill — understand the corpus before reading it
  → screen-studies-prisma
  → synthesize-literature
```

As a deliverable on its own:

```
[any CSV / JSON / Excel input]
  → explore-dataset          ← EDA + interactive dashboard
```

Piping JSON metrics into a downstream analytical skill:

```
explore-dataset (--no-html)
  → analyze-corpus           ← if available, for deeper bibliometric analysis
```

---

## Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `EXPLORE_MAX_ROWS` | `100000` | Row limit before sampling is applied |
| `EXPLORE_SAMPLE_SEED` | `42` | Random seed for reproducible sampling |
| `EXPLORE_PLOTLY_CDN` | `https://cdn.plot.ly/plotly-2.35.2.min.js` | Plotly CDN URL for the HTML output |

---

## Failure modes

- **Unsupported format**: the CLI exits with a clear error message listing
  accepted formats. It does not attempt to parse unknown extensions.
- **Empty dataset**: returns a metrics JSON with `shape.rows: 0` and a
  warning in the HTML — does not crash.
- **Very large files** (> `EXPLORE_MAX_ROWS`): the CLI samples the data,
  notes the sampling rate in the JSON and in the dashboard header.
- **Excel with multiple sheets**: uses the first sheet unless `--sheet` is
  specified. Lists available sheet names in the trace output.
- **JSON with nested structures**: flattens one level deep. Deeply nested
  fields are reported as `object` dtype and excluded from numeric analysis.
- **No numeric columns**: skips correlation heatmap and numeric distributions,
  produces categorical charts only.