# CHANGELOG

## 2026-07-24 — Cloud/hybrid/on-prem rollup lens (derived, schema unchanged)
**Decision (Tuo-approved):** collapse the 8-value `deployment` enum into the §3 infra-control gate as **two mutually-exclusive buckets + one hybrid flag**, NOT three buckets. Mapping: on-prem side ← on-prem/edge/private/OEM; cloud side ← public/SaaS/managed; `hybrid` is the boundary marker only. Primary bucket = first-listed deployment; `spans_infra_boundary` = deployment set touches both sides (or literal hybrid).

**Changed (derived only — `taxonomy.yaml` untouched, stays approved v2):**
- `tools/rollup.py` — CLI over taxonomy.yaml. Result: **37 on-prem · 16 cloud · 0 hybrid-primary**, 44/53 span the boundary, **26 HOT** (on-prem & hw_pull≥3, incl. all 9 hw4 flagship categories).
- `tools/build_app.py` / `app/index.html` — Taxonomy tab gains an infra-bucket filter, spans-boundary toggle, per-card bucket badge (green on-prem / muted cloud, `⇄` when spanning), and a top rollup summary.
- **Live-verified**: CLI and app agree (both single-source from taxonomy.yaml, independent code paths). In-browser filter on-prem + hw_pull≥3 → "26 / 53 shown" = rollup.py HOT count.

**Note:** cloud bucket = 0 categories at hw_pull≥3 → SMCI direct-sell skips it; enter only via ISV/operator. The hardware list IS the 26 HOT on-prem categories.

**Open (for Tuo):** run `codex` (+ optional Grok) as a second-opinion reviewer over this deployment mapping? Next drill-down axis after infra bucket: hw_pull → play → segment.

## 2026-07-24 — App built + taxonomy boundaries sharpened
**Changed:**
- `tools/build_app.py` + `app/index.html` — single-file playbook UI (67 KB, zero external deps, file:// works). Generated from `/data`; app code holds no domain content. 5 tabs: Taxonomy (filter by segment/play/deployment/hw_pull + search), Plays, Triggers (urgency-coloured), Scoring (interactive scorer mirroring score.py), Accounts (live-scored + ranked + evidence flag).
- **Live-verified in a real browser** (http server, JS executed): all 5 tabs render; scorer all-3 → 60.0 Nurture; Riverbend account → 77 breakdown matches score.py; evidence-D flag shows.
- Rendering via DOM text nodes only (no innerHTML with data).
- Taxonomy boundary fixes (no merge — granularity kept): `smart-room-ambient-ai` dropped "OR video routing" (→ `or-surgical-video`); `bioinformatics-secondary`↔`clinical-genomics-reporting` handoff (compute→SaaS) defined on both.

**Open questions (for Tuo):**
1. Drop v1 `.jsx` into `/source/` → vendor extraction (vendors.yaml still empty) + cross-check vs the 53 categories.
2. Remaining overlap pairs — merge or keep? `medical-device-integration`↔`icu-central-monitoring` · `ngs-lab-lims`↔`rd-lab-informatics` (both left separate for now).
3. Start filling real target accounts (30 max) via the lite-card workflow?

## 2026-07-24 — Taxonomy filled (schema approved)
**Changed:**
- `data/taxonomy.yaml` → `status: approved`, `version: 2`. **53 categories** (3 pre-approved examples + 50 new), 0 enum violations, no vendor-name leakage.
- Built via multi-agent workflow: 7 domain clusters drafted in parallel → adversarial verify per cluster (enum compliance, deployment/hw_pull honesty, Taiwan繁中 terminology) → completeness critic.
- Verifier corrections applied (highlights): EHR `SaaS`→`managed` (vendor-hosted single-tenant, not multi-tenant); `ngs-lab-lims` hw_pull 3→2 (LIMS ≠ the sequencer/analysis storage anchor); many name_zh fixes to Taiwan usage (量能 not 容量, 建築 not 樓宇, 視訊 not 視頻, 數位分身 not 數位孿生, 醫療器材軟體 for SaMD, 紀錄簿 orthography).
- Coverage critic added 4 hardware-relevant categories: `radiation-oncology-tps-ois` (GPU dose calc, play-a), `advanced-visualization-3d` (GPU render farm, play-a), `automated-visual-inspection` (edge-GPU line QC, play-c), `ai-hpc-orchestration` (GPU/HPC scheduler + MLOps — strongest ISV co-sell anchor, play-b).
- Distribution: hw_pull {1:9, 2:18, 3:17, 4:9} · plays a8/b9/c8 + 28 cross-cutting · 29 hospital-matrix / 24 non-hospital · all 8 segments covered.

**Open questions (for Tuo):**
1. Overlap pairs flagged by critic — keep separate (current) or merge? `medical-device-integration`↔`icu-central-monitoring` · `or-surgical-video`↔`smart-room-ambient-ai` (OR video double-count) · `ngs-lab-lims`↔`rd-lab-informatics` · `clinical-genomics-reporting`↔`bioinformatics-secondary` (tertiary handoff).
2. 53 categories vs "lean" — trim any before building the app?
3. Drop v1 `.jsx` into `/source/` → vendor extraction + cross-check against these 53.
4. Build `/app` (renders taxonomy + plays + triggers + scoring + accounts from `/data`)?

## 2026-07-24 — First Task executed
**Changed:**
- Repo scaffolded per §7 (`git init` done, no commit yet): `/data` `/templates` `/tools` `/app` `/docs` `/source`
- `CLAUDE.md` saved at root
- Seeded `data/scoring.yaml` (8 items, 100 pts, 4 tiers), `data/plays.yaml` (Play A/B/C), `data/triggers.yaml` (10 v1 + 4 framework = 14 triggers), `data/vendors.yaml` (empty registry, extraction TODO)
- `templates/account-card-lite.md` (10 fields) + `account-card-full.md`
- `tools/score.py` built + verified end-to-end: fictional Riverbend digital-pathology account → 77.0 / Active pursuit; gap detection works (flags all-D evidence, missing fields)
- `data/accounts/example-riverbend-pathology.yaml` — FICTIONAL demo, all confidence D
- `docs/workflow.md` (lean 10-phase with kill rules) + `docs/glossary.md` (EN/ZH seed, 17 terms)
- `data/taxonomy.yaml` — SCHEMA PROPOSAL with 3 examples (pacs-vna, bioinformatics-secondary, mes-ebr). `status: PROPOSAL`.

**Open questions (for Tuo):**
1. Taxonomy schema approval — approve / modify before full fill (§9.4 gate)
2. Confirm or swap default Play A/B/C trio (§5.1)
3. Drop v1 `.jsx` files into `/source/` → vendor + category extraction
4. First git commit — say the word
