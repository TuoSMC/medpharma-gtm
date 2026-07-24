# App — v2 playbook UI

Status: **built.** `index.html` — single self-contained file, zero external deps.

## Build / refresh
```
python3 tools/build_app.py     # reads /data/*.yaml -> writes app/index.html
open app/index.html            # file:// works; data is embedded
```
Data is the single source of truth. To change a vendor, category, trigger, or
account: edit the yaml in `/data`, re-run the build. **Never edit `index.html`
by hand** — it is generated (CLAUDE.md §8 rule 1). App code lives in
`tools/build_app.py` and holds zero domain content.

## Tabs
- **Taxonomy** — 53 categories; filter by **infra bucket (on-prem / cloud)** · segment · play · deployment · hw_pull · **spans-boundary** toggle + text search. Each card shows a derived infra-control bucket badge (green = on-prem = hardware opportunity; `⇄` = spans customer↔vendor boundary). Top rollup line summarises the split.
- **Plays** — 3 solution plays (workloads, targets, hardware anchor, regulatory)
- **Triggers** — 14 triggers, colour-coded by urgency
- **Scoring** — the 100-pt model + interactive scorer (mirrors `tools/score.py`)
- **Accounts** — every `data/accounts/*.yaml`, live-scored, ranked, with evidence-confidence flag

Rendering uses DOM text nodes only (no `innerHTML` with data) — embedded content
cannot execute as markup. Theme follows OS light/dark.
