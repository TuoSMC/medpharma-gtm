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
- **Taxonomy** — 53 categories; filter by **hardware_buyer (customer / operator / oem / hyperscaler)** · substrate (on-prem/cloud) · segment · play · deployment · hw_pull · spans-boundary toggle + search. **Group by** any axis (primary_buyer / hardware_buyer / hw_pull / play / segment / data_modality / role / bucket). Each card shows a primary-buyer badge (green customer = direct / purple operator = ISV co-sell / orange OEM = design-win), other buyers as chips, `⇄` when deployment spans the customer↔vendor boundary. Top rollup line: HOT_customer / HOT_operator / OEM counts.
- **Plays** — 3 solution plays (workloads, targets, hardware anchor, regulatory)
- **Triggers** — 14 triggers, colour-coded by urgency
- **Scoring** — the 100-pt model + interactive scorer (mirrors `tools/score.py`)
- **Accounts** — every `data/accounts/*.yaml`, live-scored, ranked, with evidence-confidence flag

Rendering uses DOM text nodes only (no `innerHTML` with data) — embedded content
cannot execute as markup. Theme follows OS light/dark.
