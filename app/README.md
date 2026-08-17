# App — GTM hunt map (shell + on-demand archive)

Status: **built.** A **shell** (`index.html`, ~2.2 MB) + an **on-demand archive**
(`taxonomy_tree.js`, ~1.7 MB) that ship together — no remote deps (plan-v6.1 C3).
The shell embeds the 59-category spine + L1 sub-markets + the retrieval index; the archived
L2+ sub-tree loads lazily from `taxonomy_tree.js` on "Show deeper". Both files are byte-identical
in `app/` and `docs/` (GitHub Pages deploys `docs/`).

## Build / refresh
```
python3 tools/build_index.py   # data/*.yaml -> data/taxonomy_index.yaml (+ tree index)  [run first]
python3 tools/build_app.py     # -> app/index.html + app/taxonomy_tree.js  (+ docs/ copies)
open app/index.html            # file:// works; the archive loads via a <script> element, not fetch
```
Data is the single source of truth. To change a vendor, category, trigger, or account:
edit the yaml in `/data`, rebuild the index (if taxonomy changed), re-run the app build.
**Never edit `index.html` or `taxonomy_tree.js` by hand** — both are generated. App code lives
in `tools/build_app.py` and holds zero domain content.

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
