# SMCI Medical / Pharma GTM Playbook

A reusable **classification asset** for Supermicro (SMCI) medical/pharma go-to-market: it maps the medical & pharma **software universe** to the **hardware infrastructure** behind it (GPU servers, HPC, NVMe/archive storage, industrial edge, HA/DR), so a hardware seller can find and work the deal underneath the software.

**▶ Live tool: https://tuosmc.github.io/medpharma-gtm/**

Single self-contained HTML page (zero dependencies, works offline, bilingual EN / 繁中).

## What's inside

- **59 software categories** classified by lifecycle, role, data modality, deployment, the **hardware buyer** (customer / operator / OEM), and the SMCI hardware profile each pulls.
- **4 solution plays** — A Medical Imaging + Digital Pathology · B Genomics / Research AI · C GMP Manufacturing Edge · D Clinical Core Resilience & Ransomware DR.
- **14 purchase triggers** — each a signal → affected markets → the prescribed outreach move.
- **309 vendors** with leaderboard ranks, cited **market-share** figures, and **partnerships** (hardware/cloud partners flagged as co-sell / displacement angles).
- An **Explore** hunt launcher: search · product line · trigger · play, every door landing on a category **battle card** (your motion · reference architecture · trigger-to-watch · vendor market-share bars · partner landscape).

## Build

Data lives in `/data` (YAML); the app renders from it — updating a vendor or category never touches code.

```bash
python3 tools/build_app.py      # regenerates app/index.html + docs/index.html
python3 -m pytest tools/tests/  # integrity checks
```

The published site is served from `docs/` (GitHub Pages). Every factual claim in the data carries an evidence-confidence tag and, where researched, a source. Market-share / partnership data is point-in-time (2025–26 sources) — refresh periodically.
