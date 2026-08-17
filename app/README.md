# App — single-file GTM hunt map

Status: **built.** `index.html` — one self-contained file, zero external deps.
`app/index.html` == `docs/index.html` byte-identical (GitHub Pages deploys `docs/`).

## Build / refresh
```
python3 tools/build_app.py     # reads /data/*.yaml -> writes app/index.html + docs/index.html
open app/index.html            # file:// works; data is embedded
```
Data is the single source of truth. To change a vendor, category, trigger, or account:
edit the yaml in `/data`, re-run the build. **Never edit `index.html` by hand** — it is
generated (CLAUDE.md rule). App code lives in `tools/build_app.py` and holds zero domain content.

## Tabs (live)
- **Explore** — the Play spine. Play A/B/C/D → AI / No-AI → **category**. **59 locked categories**
  are the default tree; the 999-subcategory drill-down is an archive behind an explicit control,
  not the default view (plan-v6). Each category opens a battle card (motion · architecture · trigger ·
  vendor slugs). Primary-buyer badge: green customer = direct · purple operator = ISV co-sell · orange OEM = design-win.
- **Method** — the gate, the 4 plays, the 100-pt scoring model, and the research workflow.
- **Vendors** — vendor two-pane with `#v/` deep-links; per-vendor intel drawer
  (ISV type · what they make · products · deployment preference cloud/on-prem/hybrid · end-user base · source).

Rendering uses DOM text nodes only (no `innerHTML` with data) — embedded content cannot execute
as markup. Theme follows OS light/dark.

> **Numbers (2026-08-17):** 59 categories · 999 subcategories (archive) · 4 plays · 14 triggers ·
> 309 vendors · 408 intel records · HOT = 35 categories with `hardware_opportunity >= 3`.
