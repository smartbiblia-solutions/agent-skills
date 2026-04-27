---
name: ingest
description: "Process source material (PDFs, markdown files, web URLs) into a structured, interlinked wiki knowledge base using a four-stage pipeline: chunk, extract, plan, write. Creates one wiki page per concept with dense [[cross-links]], maintains an index, tracks what has been processed, and writes source summaries for traceability. MUST use this skill whenever the user wants to: add documents or files to a wiki or knowledge base; ingest, import, or process PDFs, papers, articles, notes, or lecture materials; turn a URL or web article into wiki pages; update a knowledge base with new source material; extract concepts, findings, or structured data from documents into organized pages. This skill applies even when the user doesn't say 'ingest' explicitly — any request to read source material and organize it into wiki-style pages should use this skill. Do NOT use for: searching/querying existing wiki content, editing or reorganizing existing pages, or general file creation unrelated to knowledge extraction."
source: https://github.com/akshayballal95/wiki-ingest
---

# Ingest

You are an ingestion agent that reads raw source material and maintains a structured wiki knowledge base. You follow a four-stage pipeline: **Chunk -> Extract -> Plan -> Write**. Each stage has a clear job — do them in order, don't skip stages.

## Configuration

On first run, check for `ingest.config.json` in the project root. If it doesn't exist, ask the user:

1. **Where are your raw source files?** (default: `raw/`)
2. **Where should the wiki be created?** (default: `wiki/`)

Save their answers to `ingest.config.json`:

```json
{
  "raw_dir": "raw/",
  "wiki_dir": "wiki/",
  "processed_file": "processed.json"
}
```

On subsequent runs, read the config and use those paths. All paths below that reference `raw/` or `wiki/` should use the configured values instead.

If the config file already exists, skip the questions and proceed.

## Folder structure

```
<raw_dir>/              — source files to ingest (PDFs, markdown, text)
<wiki_dir>/             — concept pages (one per concept)
<wiki_dir>/index.md     — master index: every concept page listed with a one-line description
<wiki_dir>/sources/     — source summary pages (one per ingested source or chunk)
processed.json          — tracks which files have been ingested (filename -> content hash)
```

If `<wiki_dir>/`, `<wiki_dir>/sources/`, or `<wiki_dir>/index.md` don't exist yet, create them. If `processed.json` doesn't exist, create it as an empty JSON object `{}`.

## Supported input types

- **PDF files** in `<raw_dir>/` — read using the Read tool (which supports PDFs). For large PDFs, read in page ranges (20-40 pages at a time).
- **Markdown / text files** in `<raw_dir>/` — read directly.
- **Web links** — if the user pastes a URL, fetch its content using WebFetch and process it as a source. Use the URL as the source identifier.

## Before you start

1. Read `ingest.config.json` — if missing, run the configuration flow above.
2. Read `processed.json` to see what's already been ingested.
3. List files in `<raw_dir>/` and identify unprocessed files (not in `processed.json`, or hash has changed).
4. Read `<wiki_dir>/index.md` to understand the current state of the wiki.
5. If there are no new files and the user hasn't provided a URL, tell them there's nothing to ingest.

## The pipeline

Run this pipeline for each unprocessed source. If there are multiple files, process them one at a time — each file should see the wiki updates from all previous files.

### Stage 1: Chunk

Split the source into manageable pieces.

- **Short sources** (articles, single papers, < ~40 pages): treat as one chunk.
- **Large sources** (books, long reports, > ~40 pages): split by natural boundaries. For PDFs, read the table of contents or scan headings to find chapter/section breaks. Target 20-40 pages per chunk. Process chunks in order — the wiki should reflect chunk 1 before you start chunk 2.

For each chunk, note:
- Source name (filename or URL)
- Chunk label (e.g., "full document", "Chapter 3", "pages 45-80")
- Position in sequence (1 of 1, 2 of 7, etc.)

### Stage 2: Extract

Read the chunk and extract structured information. This is pure analysis — don't write any wiki files yet.

Pull out everything worth capturing:

- **Concepts and ideas** — the core topics discussed. What is this chunk *about*?
- **Structured data** — tables, benchmarks, comparison matrices, metrics, numerical results. Preserve these in their original tabular form.
- **Processes and methods** — algorithms, workflows, step-by-step procedures, architectures.
- **Named entities** — people, organizations, models, tools, datasets, frameworks.
- **Claims and findings** — key conclusions, experimental results, open questions.
- **Relationships** — how concepts connect to each other (e.g., "LoRA is a type of parameter-efficient fine-tuning", "ALMA extends continual learning").

Write out the extraction as a structured list before proceeding. This is your working material for the next stages.

### Stage 3: Plan

Decide what changes to make to the wiki. Read the current `wiki/index.md` and any existing wiki pages that are relevant to the extracted content.

For each extracted item, decide:

1. **Does a relevant page already exist?** Check `index.md` for matching or closely related concepts. If yes, read that page.
2. **Update or create?**
   - If the concept is already covered: plan what new information to add. Don't duplicate what's there. If the new information contradicts existing content, note the contradiction.
   - If the concept is new: plan a new page with a clear title and scope.
3. **Cross-links** — for every page you're updating or creating, identify which other wiki pages it should link to. Be generous with links — they're what make the wiki useful. Use Obsidian link syntax:
   - `[[Page Name]]` — link to a whole page
   - `[[Page Name#Section]]` — link to a specific header within a page (use this when the target page has a relevant subsection)
   - `[[Page Name#Section|display text]]` — link with custom display text so the prose reads naturally (e.g., `[[Vacuum Pumps#Ultrasonic Leak Detectors|handheld ultrasonic leak detector]]`)
   Prefer header-anchored links when a specific subsection is the real target — they're more precise than linking the whole page.
4. **Deduplication** — if the source is reinforcing something already well-covered in the wiki, skip it rather than bloating pages with repetition.

Write out the plan as a concrete list:
- Pages to update: which page, what to add/change
- Pages to create: title, scope, key content
- Cross-links to add
- Contradictions to flag

### Stage 4: Write

Execute the plan. This stage is mechanical — the thinking was done in Stage 3.

**Updating existing pages:**
- Read the current page content
- Merge new information into the appropriate sections
- Preserve existing structure, tables, and formatting
- Add new cross-links using `[[Page Name]]`, `[[Page Name#Section]]`, or `[[Page Name#Section|display text]]` as appropriate
- Don't rewrite content that doesn't need changing

**Creating new pages:**
- Use the concept title as the filename with spaces (e.g., `Gradient Descent.md`). This matches Obsidian's `[[link]]` resolution.
- Start with a `# Title` heading
- Write substantial content — a reader should get a complete picture of the concept from this page alone
- Include `[[links]]` to related concepts throughout the text, not just in a "See also" section
- Include any tables, benchmarks, or structured data extracted from the source

**Updating index.md:**
- Add entries for any new pages: `- [[Page Name]] — one-line description`
- Update descriptions for existing pages if their scope has meaningfully expanded
- Keep the index sorted alphabetically

**Writing source summary:**
- Create a page in `wiki/sources/` named after the source (e.g., `wiki/sources/understanding-lora.md`)
- For chunked sources, one summary per chunk (e.g., `wiki/sources/book-title-ch03.md`)
- Include: source filename/URL, date processed, list of concepts extracted, which wiki pages were created or updated

**Updating processed.json:**
- After successfully processing a file, add its filename and content hash to `processed.json`
- For chunked sources, update after each chunk completes (so ingestion can resume if interrupted)

## Page writing guidelines

Wiki pages should be:

- **Substantial.** A page on "Gradient Descent" should explain what it is, how it works, key variants, and where it's used — not just a one-line definition. Think encyclopedia article, not glossary entry.
- **Self-contained.** A reader should be able to understand the page without reading other pages. Cross-links provide depth, not prerequisites.
- **Densely linked.** Mention a concept that has its own page? Link it. Use `[[Concept Name]]` for whole-page links, `[[Concept Name#Section]]` to target a specific header, and `[[Concept Name#Section|display text]]` when you need custom display text so the sentence reads naturally — e.g., "use a [[Vacuum Pumps#Ultrasonic Leak Detectors|handheld ultrasonic leak detector]] to find leaks". Prefer header-anchored links when a subsection is the real target. Link on first mention in each major section. Use `## Headers` within your own pages so other pages can link to them.
- **Preserving of structured data.** Tables, benchmarks, and metrics should appear as markdown tables, not flattened into prose. These are often the most valuable part of a source.
- **Honest about uncertainty.** If two sources disagree, say so. Use a "Contradictions" or "Open Questions" section when needed rather than silently picking one version.
- **Jargon-aware.** Define technical terms and acronyms on first use. Don't assume the reader knows what "FFN" or "oracle routing" means — briefly explain inline (e.g., "FFN (Feed-Forward Network) layers — the dense transformation blocks within each transformer layer").
- **No inline citations.** This is a wiki, not an academic paper. Don't scatter "(Author et al., 2025)" throughout the text. If a page draws from a specific source, mention it naturally (e.g., "Back et al. found that...") or note it in a "References" section at the bottom. Keep the prose clean.

## When the user provides a URL

If the user pastes a URL (instead of or in addition to processing `raw/`):

1. Fetch the URL content using WebFetch
2. Treat the fetched content as a source and run it through the same pipeline
3. Use the URL as the source identifier in `processed.json` and source summaries
4. Save the source summary to `wiki/sources/` using a slugified version of the page title or domain

## Progress reporting

As you work through sources, give brief status updates:
- "Processing: [filename] (1 of 5)"
- "Extracted 8 concepts, 2 tables, 3 key findings"
- "Updating 3 existing pages, creating 2 new pages"
- "Done. Wiki now has X concept pages."

Don't be verbose — just enough for the user to follow along.
