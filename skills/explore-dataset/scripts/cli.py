#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pandas>=2.0",
#   "openpyxl",
#   "plotly>=5.0",
#   "pyarrow",
# ]
# ///
"""
explore-dataset CLI

Produces:
  <stem>.metrics.json     — structured EDA metrics (pipeline-ready)
  <stem>.dashboard.html   — standalone interactive HTML dashboard (Plotly, no server)
  <stem>.summary.md       — narrative EDA summary (human-readable)

Usage:
  uv run skills/explore-dataset/scripts/cli.py --input data.csv --output-dir /tmp/out/
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# ──────────────────────────────────────────────────────────────────────────────
# Config
# ──────────────────────────────────────────────────────────────────────────────

MAX_ROWS    = int(os.environ.get("EXPLORE_MAX_ROWS", "100000"))
SAMPLE_SEED = int(os.environ.get("EXPLORE_SAMPLE_SEED", "42"))
PLOTLY_CDN  = os.environ.get(
    "EXPLORE_PLOTLY_CDN",
    "https://cdn.plot.ly/plotly-2.35.2.min.js",
)

HUB_MARKER_FIELDS = {"source", "doi", "year", "authors", "title"}


# ──────────────────────────────────────────────────────────────────────────────
# Loading
# ──────────────────────────────────────────────────────────────────────────────

def load(path: Path, sheet: str | None, trace: bool) -> pd.DataFrame:
    ext = path.suffix.lower()
    if trace:
        print(f"[trace] Loading {path} (ext={ext})", file=sys.stderr)

    if ext == ".csv":
        return pd.read_csv(path, low_memory=False)
    if ext == ".tsv":
        return pd.read_csv(path, sep="\t", low_memory=False)
    if ext in (".xlsx", ".xls"):
        kw: dict[str, Any] = {}
        if sheet:
            kw["sheet_name"] = sheet
        return pd.read_excel(path, **kw)
    if ext in (".parquet",):
        return pd.read_parquet(path)
    if ext in (".arrow", ".feather"):
        return pd.read_feather(path)
    if ext == ".json":
        raw = json.loads(path.read_text(encoding="utf-8"))
        # hub output shape: {"results": [...], ...}
        if isinstance(raw, dict) and "results" in raw:
            raw = raw["results"]
        if not isinstance(raw, list):
            raise ValueError("JSON must be an array or an object with a 'results' key.")
        return pd.json_normalize(raw, max_level=1)

    raise ValueError(
        f"Unsupported format: {ext!r}. "
        "Accepted: .csv .tsv .json .xlsx .xls .parquet .arrow .feather"
    )


def maybe_sample(df: pd.DataFrame, trace: bool) -> tuple[pd.DataFrame, float]:
    if len(df) <= MAX_ROWS:
        return df, 1.0
    rate = MAX_ROWS / len(df)
    if trace:
        print(
            f"[trace] Sampling {MAX_ROWS:,}/{len(df):,} rows (rate={rate:.2%})",
            file=sys.stderr,
        )
    return df.sample(MAX_ROWS, random_state=SAMPLE_SEED), rate


# ──────────────────────────────────────────────────────────────────────────────
# Profile detection
# ──────────────────────────────────────────────────────────────────────────────

def detect_profile(df: pd.DataFrame) -> str:
    if HUB_MARKER_FIELDS.issubset(set(df.columns)):
        return "hub-records"
    return "tabular-generic"


# ──────────────────────────────────────────────────────────────────────────────
# Metrics helpers
# ──────────────────────────────────────────────────────────────────────────────

def _safe_nunique(series: pd.Series) -> int:
    try:
        return int(series.nunique())
    except TypeError:
        return int(series.astype(str).nunique())


def _safe_value_counts(series: pd.Series, n: int) -> dict[str, int]:
    try:
        counts = series.value_counts().head(n)
    except TypeError:
        counts = series.astype(str).value_counts().head(n)
    return {str(k): int(v) for k, v in counts.items()}


def column_inventory(df: pd.DataFrame) -> list[dict]:
    return [
        {
            "name": col,
            "dtype": str(df[col].dtype),
            "missing": int(df[col].isna().sum()),
            "unique": _safe_nunique(df[col]),
        }
        for col in df.columns
    ]


def numeric_stats(df: pd.DataFrame) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for col in df.select_dtypes(include="number").columns:
        s = df[col].dropna()
        if s.empty:
            continue
        out[col] = {
            "min": round(float(s.min()), 4),
            "max": round(float(s.max()), 4),
            "mean": round(float(s.mean()), 4),
            "median": round(float(s.median()), 4),
            "std": round(float(s.std()), 4),
        }
    return out


def categorical_stats(df: pd.DataFrame, max_cat: int) -> dict[str, dict]:
    out: dict[str, dict] = {}
    # include str/object/category but skip list/dict columns
    candidates = df.select_dtypes(include=["object", "category", "string"]).columns
    for col in candidates:
        # skip if first non-null value is a collection
        sample = df[col].dropna()
        if not sample.empty and isinstance(sample.iloc[0], (list, dict)):
            continue
        out[col] = _safe_value_counts(df[col], max_cat)
    return out


def hub_specific_metrics(df: pd.DataFrame, max_cat: int) -> dict:
    m: dict[str, Any] = {}

    # Open-access rate
    if "is_open_access" in df.columns:
        m["open_access_rate"] = round(
            float(df["is_open_access"].fillna(False).mean()), 3
        )

    # Publications by year
    if "year" in df.columns:
        by_year = (
            df["year"].dropna().astype(int).value_counts().sort_index()
        )
        m["publications_by_year"] = {str(k): int(v) for k, v in by_year.items()}

    # Top authors — flatten list columns
    if "authors" in df.columns:
        all_authors: list[str] = []
        for val in df["authors"].dropna():
            if isinstance(val, list):
                all_authors.extend(str(a) for a in val)
            else:
                all_authors.append(str(val))
        top = Counter(all_authors).most_common(max_cat)
        m["top_authors"] = [{"name": a, "count": c} for a, c in top]

    # Top journals
    if "journal" in df.columns:
        top_j = df["journal"].dropna().value_counts().head(max_cat)
        m["top_journals"] = [{"name": str(k), "count": int(v)} for k, v in top_j.items()]

    # Top topics — flatten list columns
    if "topics" in df.columns:
        all_topics: list[str] = []
        for val in df["topics"].dropna():
            if isinstance(val, list):
                all_topics.extend(str(t) for t in val)
            else:
                all_topics.append(str(val))
        top_t = Counter(all_topics).most_common(max_cat)
        m["top_topics"] = [{"topic": t, "count": c} for t, c in top_t]

    return m


def compute_metrics(
    df: pd.DataFrame,
    profile: str,
    input_file: str,
    sample_rate: float,
    max_cat: int,
) -> dict:
    total_missing = int(df.isna().sum().sum())
    cols_with_missing = [c for c in df.columns if df[c].isna().any()]

    m: dict[str, Any] = {
        "profile": profile,
        "input_file": input_file,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "shape": {"rows": len(df), "columns": len(df.columns)},
        "sample_rate": sample_rate,
        "columns": column_inventory(df),
        "missing_summary": {
            "total_missing_cells": total_missing,
            "columns_with_missing": cols_with_missing,
            "missing_rate_pct": round(
                total_missing / max(len(df) * len(df.columns), 1) * 100, 2
            ),
        },
        "numeric_stats": numeric_stats(df),
        "categorical_stats": categorical_stats(df, max_cat),
    }
    if profile == "hub-records":
        m["hub_metrics"] = hub_specific_metrics(df, max_cat)
    return m


# ──────────────────────────────────────────────────────────────────────────────
# Markdown summary
# ──────────────────────────────────────────────────────────────────────────────

def make_summary(metrics: dict, title: str) -> str:
    m = metrics
    shape = m["shape"]
    missing = m["missing_summary"]
    profile = m["profile"]
    ts = m["generated_at"][:10]

    lines = [
        f"# EDA summary — {title}",
        f"\n> Generated {ts} · {profile} profile · {shape['rows']:,} rows × {shape['columns']} columns",
        "\n## Dataset overview\n",
        f"- **Rows**: {shape['rows']:,}"
        + (f" (sampled from {int(shape['rows'] / m['sample_rate']):,})" if m["sample_rate"] < 1.0 else ""),
        f"- **Columns**: {shape['columns']}",
        f"- **Missing data**: {missing['missing_rate_pct']}% of all cells"
        + (f" ({', '.join(missing['columns_with_missing'][:5])})" if missing["columns_with_missing"] else " — none"),
    ]

    # Numeric highlights
    num = m.get("numeric_stats", {})
    if num:
        lines.append("\n## Numeric columns\n")
        for col, stats in num.items():
            lines.append(
                f"- **{col}**: min {stats['min']}, max {stats['max']}, "
                f"mean {stats['mean']}, median {stats['median']}"
            )

    # Categorical highlights (top 3 values per column, max 5 columns)
    cat = m.get("categorical_stats", {})
    if cat:
        lines.append("\n## Categorical columns\n")
        for col, counts in list(cat.items())[:5]:
            top3 = list(counts.items())[:3]
            top3_str = ", ".join(f"{k} ({v})" for k, v in top3)
            lines.append(f"- **{col}**: {top3_str}…")

    # Hub-specific section
    hm = m.get("hub_metrics", {})
    if hm:
        lines.append("\n## Bibliometric overview\n")

        if "open_access_rate" in hm:
            oa_pct = round(hm["open_access_rate"] * 100, 1)
            lines.append(f"- **Open access rate**: {oa_pct}%")

        if "publications_by_year" in hm:
            by_year = hm["publications_by_year"]
            year_range = f"{min(by_year.keys())}–{max(by_year.keys())}"
            peak_year = max(by_year, key=lambda y: by_year[y])
            lines.append(
                f"- **Publication span**: {year_range} "
                f"(peak: {peak_year} with {by_year[peak_year]} publications)"
            )

        if "top_authors" in hm and hm["top_authors"]:
            top3 = hm["top_authors"][:3]
            lines.append(
                "- **Top authors**: "
                + ", ".join(f"{a['name']} ({a['count']})" for a in top3)
            )

        if "top_journals" in hm and hm["top_journals"]:
            top3 = hm["top_journals"][:3]
            lines.append(
                "- **Top journals**: "
                + ", ".join(f"{j['name']} ({j['count']})" for j in top3)
            )

        if "top_topics" in hm and hm["top_topics"]:
            top5 = hm["top_topics"][:5]
            lines.append(
                "- **Top topics**: "
                + ", ".join(f"{t['topic']} ({t['count']})" for t in top5)
            )

    lines.append(
        f"\n---\n*Full metrics: `{m['input_file'].replace('.', '_')}.metrics.json` "
        f"· Dashboard: `{m['input_file'].replace('.', '_')}.dashboard.html`*"
    )
    return "\n".join(lines) + "\n"


# ──────────────────────────────────────────────────────────────────────────────
# HTML dashboard
# ──────────────────────────────────────────────────────────────────────────────

def _fig_html(fig: go.Figure) -> str:
    return fig.to_html(full_html=False, include_plotlyjs=False)


def make_dashboard(df: pd.DataFrame, metrics: dict, title: str, max_cat: int) -> str:
    profile = metrics["profile"]
    shape   = metrics["shape"]
    missing = metrics["missing_summary"]
    sample_rate = metrics["sample_rate"]

    charts: list[tuple[str, str]] = []  # (section title, html)

    # ── Hub-records charts ────────────────────────────────────────────────────
    if profile == "hub-records":
        hm = metrics.get("hub_metrics", {})

        if "publications_by_year" in hm:
            by_year = hm["publications_by_year"]
            fig = px.line(
                x=list(by_year.keys()),
                y=list(by_year.values()),
                labels={"x": "Year", "y": "Publications"},
                markers=True,
            )
            fig.update_layout(margin=dict(t=20, b=40))
            charts.append(("Publications by year", _fig_html(fig)))

        if hm.get("top_authors"):
            items = hm["top_authors"][:20]
            fig = px.bar(
                x=[a["count"] for a in items],
                y=[a["name"]  for a in items],
                orientation="h",
                labels={"x": "Count", "y": "Author"},
            )
            fig.update_layout(yaxis={"autorange": "reversed"}, margin=dict(t=20))
            charts.append(("Top authors", _fig_html(fig)))

        if hm.get("top_journals"):
            items = hm["top_journals"][:15]
            fig = px.bar(
                x=[j["count"] for j in items],
                y=[j["name"]  for j in items],
                orientation="h",
                labels={"x": "Count", "y": "Journal"},
            )
            fig.update_layout(yaxis={"autorange": "reversed"}, margin=dict(t=20))
            charts.append(("Top journals", _fig_html(fig)))

        if hm.get("top_topics"):
            items = hm["top_topics"][:20]
            fig = px.bar(
                x=[t["count"] for t in items],
                y=[t["topic"] for t in items],
                orientation="h",
                labels={"x": "Count", "y": "Topic"},
            )
            fig.update_layout(yaxis={"autorange": "reversed"}, margin=dict(t=20))
            charts.append(("Top topics", _fig_html(fig)))

        if "doc_type" in df.columns:
            counts = df["doc_type"].dropna().value_counts().head(max_cat)
            fig = px.pie(values=counts.values, names=counts.index)
            fig.update_layout(margin=dict(t=20))
            charts.append(("Document types", _fig_html(fig)))

        if "open_access_rate" in hm:
            oa = hm["open_access_rate"]
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=round(oa * 100, 1),
                number={"suffix": "%"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "#2ecc71"},
                    "steps": [
                        {"range": [0,  40], "color": "#fadbd8"},
                        {"range": [40, 70], "color": "#fdebd0"},
                        {"range": [70, 100], "color": "#d5f5e3"},
                    ],
                },
            ))
            fig.update_layout(height=250, margin=dict(t=20, b=10))
            charts.append(("Open access rate", _fig_html(fig)))

    # ── Generic charts ────────────────────────────────────────────────────────
    else:
        num_cols = df.select_dtypes(include="number").columns.tolist()
        for col in num_cols[:6]:
            fig = px.histogram(df, x=col, labels={"x": col, "y": "Count"})
            fig.update_layout(margin=dict(t=20))
            charts.append((f"Distribution — {col}", _fig_html(fig)))

        cat = metrics.get("categorical_stats", {})
        for col, counts in list(cat.items())[:6]:
            keys = list(counts.keys())
            vals = list(counts.values())
            fig = px.bar(x=keys, y=vals, labels={"x": col, "y": "Count"})
            fig.update_layout(margin=dict(t=20))
            charts.append((f"Frequencies — {col}", _fig_html(fig)))

        if len(num_cols) >= 2:
            corr = df[num_cols].corr().round(2)
            fig = px.imshow(
                corr, text_auto=True,
                color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
            )
            fig.update_layout(margin=dict(t=20))
            charts.append(("Correlation heatmap", _fig_html(fig)))

        missing_cols = metrics["missing_summary"]["columns_with_missing"]
        if missing_cols:
            pct = {c: round(df[c].isna().mean() * 100, 1) for c in missing_cols}
            pct = dict(sorted(pct.items(), key=lambda x: -x[1]))
            fig = px.bar(
                x=list(pct.keys()), y=list(pct.values()),
                labels={"x": "Column", "y": "Missing (%)"},
            )
            fig.update_layout(margin=dict(t=20))
            charts.append(("Missing values (%)", _fig_html(fig)))

    # ── Summary card ──────────────────────────────────────────────────────────
    sampled_note = (
        f"<span class='note'>(sampled {shape['rows']:,} "
        f"/ {int(shape['rows'] / sample_rate):,})</span>"
        if sample_rate < 1.0 else ""
    )
    summary_html = f"""
<div class="summary-card">
  <div class="stat"><span class="label">Rows</span>
    <span class="value">{shape['rows']:,} {sampled_note}</span></div>
  <div class="stat"><span class="label">Columns</span>
    <span class="value">{shape['columns']}</span></div>
  <div class="stat"><span class="label">Profile</span>
    <span class="value">{profile}</span></div>
  <div class="stat"><span class="label">Missing</span>
    <span class="value">{missing['missing_rate_pct']}%</span></div>
</div>"""

    charts_html = "\n".join(
        f'<section class="chart-block"><h2>{name}</h2>{html}</section>'
        for name, html in charts
    )

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<script src="{PLOTLY_CDN}"></script>
<style>
  *,*::before,*::after{{box-sizing:border-box}}
  body{{font-family:system-ui,sans-serif;margin:0;padding:1.5rem 2rem;
        background:#f8f9fa;color:#212529;max-width:1200px}}
  h1{{font-size:1.6rem;margin:0 0 .2rem}}
  .meta{{color:#6c757d;font-size:.875rem;margin-bottom:1.5rem}}
  .summary-card{{display:flex;flex-wrap:wrap;gap:2rem;background:#fff;
    border:1px solid #dee2e6;border-radius:8px;padding:1rem 1.5rem;margin-bottom:2rem}}
  .stat{{display:flex;flex-direction:column;gap:.15rem}}
  .label{{font-size:.7rem;text-transform:uppercase;letter-spacing:.06em;color:#6c757d}}
  .value{{font-size:1.25rem;font-weight:600}}
  .note{{font-size:.8rem;font-weight:400;color:#6c757d}}
  .chart-block{{background:#fff;border:1px solid #dee2e6;border-radius:8px;
    padding:1rem 1.5rem;margin-bottom:1.25rem}}
  h2{{font-size:.95rem;font-weight:600;color:#495057;margin:0 0 .5rem}}
</style>
</head>
<body>
<h1>{title}</h1>
<p class="meta">Generated {ts} &middot; {profile} profile</p>
{summary_html}
{charts_html}
</body>
</html>"""


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(prog="explore-dataset")
    ap.add_argument("--input",      required=True, help="Input file (CSV/TSV/JSON/Excel/Parquet/Arrow)")
    ap.add_argument("--output-dir", required=True, dest="output_dir")
    ap.add_argument("--profile",    default=None,
                    choices=["hub-records", "tabular-generic"])
    ap.add_argument("--sheet",      default=None,  help="Excel sheet name or index")
    ap.add_argument("--title",      default=None,  help="Dashboard/report title")
    ap.add_argument("--max-categories", type=int, default=20, dest="max_cat")
    ap.add_argument("--no-html",    action="store_true")
    ap.add_argument("--no-json",    action="store_true")
    ap.add_argument("--no-md",      action="store_true")
    ap.add_argument("--trace",      action="store_true")
    args = ap.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        df = load(input_path, args.sheet, args.trace)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        return 1

    df, sample_rate = maybe_sample(df, args.trace)
    profile = args.profile or detect_profile(df)
    title   = args.title   or input_path.stem
    stem    = input_path.stem

    if args.trace:
        print(
            f"[trace] Profile: {profile} | Rows: {len(df):,} | "
            f"Cols: {len(df.columns)} | Sample rate: {sample_rate:.2f}",
            file=sys.stderr,
        )

    metrics = compute_metrics(df, profile, input_path.name, sample_rate, args.max_cat)

    if not args.no_json:
        p = output_dir / f"{stem}.metrics.json"
        p.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[metrics]   {p}")

    if not args.no_md:
        p = output_dir / f"{stem}.summary.md"
        p.write_text(make_summary(metrics, title), encoding="utf-8")
        print(f"[summary]   {p}")

    if not args.no_html:
        p = output_dir / f"{stem}.dashboard.html"
        p.write_text(make_dashboard(df, metrics, title, args.max_cat), encoding="utf-8")
        print(f"[dashboard] {p}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())