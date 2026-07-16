---
name: motorcycle_history_writer
description: Research a motorcycle's history and create a rich, long-form Jekyll history page for the WhichBike project. Includes eligibility screening — declines to write if the motorcycle is too new, niche, or lacks a compelling story.
---

# Motorcycle History Writer Skill 🏍️📖

This skill researches a motorcycle's full history and generates a polished, long-form Jekyll Markdown page suitable for the WhichBike website. It is modeled on the existing Kawasaki Eliminator history page at `/home/danilo/Projects/eliminator/website/_moto/historia.md`.

---

## Step 0 — Eligibility Screening (REQUIRED FIRST)

Before writing anything, evaluate if this motorcycle **deserves** a history page. A great history page requires at least 3 of the following:

| Criterion | Examples |
|---|---|
| ✅ Has at least one generation shift or major redesign | CBR 600F → CBR 600RR |
| ✅ Has cultural significance or iconic status | Honda CG, Yamaha RD, Harley Sportster |
| ✅ Is sold in Brazil for 5+ years | Widespread local context |
| ✅ Has an interesting origin story or industry impact | First of its kind, disrupted a segment |
| ✅ Has a rich competitive history or community | Racing heritage, active clubs |
| ✅ Has interesting Brazilian market chapters | Locally assembled, price history, import era |

**Decline and explain if:**
- The motorcycle was launched less than 2 years ago AND has no historical predecessors with the same name
- It is an extremely niche model with no road-going history
- It is a generic commuter rebadge with no meaningful differentiation or story
- The model name has only one generation with fewer than 5 years of production

---

## Step 0.5 — Family-Level Scope (CRITICAL)

Do **NOT** write separate history pages for individual engine variations or sub-models (e.g., do not write one page for Eliminator 900, one for Eliminator 450, and one for Eliminator 125). 
Instead, write a **single, comprehensive history page for the entire model family/lineage** (e.g., "Kawasaki Eliminator" or "Honda Shadow"). The page should structure the narrative chronologically, covering all engine displacements, generations, and regional variations in separate sections under that single cohesive story.

When declining, write a short explanation: *"Este modelo não possui história suficiente para uma página completa porque..."*

---

## Step 1 — Research

Use `search_web` to gather information across these dimensions:

1. **Origin & first generation**: When created? What problem did it solve? Market context?
2. **Technical evolution**: How did engine, chassis, and electronics change across generations?
3. **Brazilian market history**: When did it arrive in Brazil? Imported, locally assembled, or CKD? Pricing milestones.
4. **Cultural significance**: Racing history, famous owners, pop culture moments, community.
5. **Current generation**: Latest version, what changed vs predecessors?
6. **Competitors**: Main rivals at each era.

Perform **at least 4 web searches** using queries like:
- `"[model name] history generations"`
- `"[model name] Brasil mercado lançamento história"`
- `"[model name] [year] specs ficha técnica"`
- `"[model name] cultural history racing heritage"`

---

## Step 2 — Evaluate & Structure

Organize research into sections (omit any section where you have insufficient solid information):

1. **Introduction** — 2–3 paragraphs setting the scene: what this motorcycle means, its place in history
2. **Origin & First Generation** — founding story, first year, original specs table
3. **Evolution** — one H2 per major generation/era
4. **Brazilian Market Chapter** — arrival, assembly, pricing, local reception
5. **Cultural Significance** (if applicable) — racing, media, community
6. **Current Generation** (if applicable) — specs table, what's new
7. **Perspectives / Legacy** — closing analysis

Each H2 section should have 3–6 paragraphs. Include **at least 2 Markdown tables** with specs or comparisons.

---

## Step 3 — Write the Page

### Jekyll Front Matter

```yaml
---
layout: single
title: "História da [BRAND] [MODEL]"
permalink: /historia/[slug]/
excerpt: "[One sentence about the motorcycle's legacy and significance in PT-BR.]"
header:
  overlay_color: "#000"
  overlay_filter: "0.6"
toc: true
toc_label: "Nesta página"
toc_icon: "motorcycle"
last_modified_at: YYYY-MM-DD
---
```

Where `[slug]` is lowercase, hyphenated: `honda-cg-160`, `kawasaki-eliminator`, etc.

### Writing Style & Tone

- **Language**: Brazilian Portuguese (PT-BR) — fully, not mixed
- **Tone**: Authoritative yet engaging — a knowledgeable enthusiast writing for fellow riders, not a press release
- **Depth**: Long-form. Each section reads like a chapter, not a bullet list
- **Brazilian context**: Always frame specs and events within the Brazilian market when relevant
- **Technical units**: cv (not hp), kgf.m (not Nm), mm (not inches in body text)
- **Tables**: Use Markdown tables for spec comparisons across generations
- **Separators**: Use `---` horizontal rules between major H2 sections
- **Avoid**: Superlatives without evidence, vague marketing language, unsupported claims

### Gold Standard Reference

Read and study `/home/danilo/Projects/eliminator/website/_moto/historia.md` before writing.
Note specifically:
- How spec tables are woven into narrative paragraphs
- How each era is given its own cultural and market context
- The analytical (not promotional) closing perspective

---

## Step 4 — Save the Page

Save to:
```
/home/danilo/Projects/whichbike/website/historia/[slug].md
```

Create the `website/historia/` directory if it does not exist yet.

---

## Step 5 — Report to User

After saving, tell the user:
- ✅ File path created
- Sections written and approximate word count
- Any gaps where sources were thin (suggest manual research topics)
- Whether the page needs image assets to be complete
- Suggested navigation entry if applicable

---

## Quality Bar
 
A completed history page MUST be:
- **Minimum 800 words** of body text (excluding front matter and tables)
- **At least 3 H2 sections**
- **At least 2 spec or comparison tables**
- Written entirely in **Brazilian Portuguese**
- Factually grounded in web research
- **Mandatory References and Sources (ADR format)**: Must include a "Referências e Fontes (ADR)" section at the end of the file containing valid, clickable links to the sources used, structured as Architecture Decision Records (ADRs) explaining how they substantiate the presented facts.

Format for references section:
```markdown
## Referências e Fontes (ADR)

* ### [REF-001] [Nome da Fonte / Título da Matéria](https://exemplo.com)
  - **Decisão / Contexto:** Este documento fundamenta [especificar os dados e decisões suportadas, como potência, anos de fabricação, etc.].
```

If you cannot meet this bar due to insufficient sources, decline and explain what is missing.
