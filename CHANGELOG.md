# CHANGELOG

## 2026-07-24 — per-buyer hw_pull (taxonomy v4) + icu flip + spec note
Actioned all three open items from the hardware_buyer round ("三個都要"):
1. **icu-central-monitoring** primary_buyer customer→**oem** — device-maker channel (Philips/GE/Draeger supply the FDA-cleared central-station servers) is the larger motion; hospital surveillance analytics is the smaller customer pull. (primary_buyer dist now 43 customer / 9 operator / 1 oem.)
2. **Per-buyer `hw_pull_by_buyer`** (taxonomy → **v4**): each buyer scored independently (customer/operator/oem; hyperscaler never scored). Assigned by a 17-agent workflow (score → adversarial verify → consistency critic). Verify caught lazy customer→operator copies (or-surgical-video oem 3→2, workforce-management operator 2→1, etc.). Consistency critic → 1 fix applied: patient-portal-engagement operator 2→1 (commodity multi-tenant portal SaaS = hyperscaler-diluted; GxP-validated hosting is what earns operator 2 — principle now stated).
3. **CLAUDE.md §3** documents the hardware_buyer axis + per-buyer pull + HOT lists.
- Refined HOT lists (per-buyer, not blended): **HOT_customer 25** (customer pull≥3) · **HOT_operator 16** (operator pull≥3) · **OEM design-wins 8**. Now surfaces cases where operator > customer (e.g. cdss-clinical-ai customer 2 / operator 3; him-coding, rcm-billing-claims, payer-um-fraud-analytics, rwd-rwe-analytics all operator-3 / customer-2 — invisible under a blended score).
- `tools/rollup.py` + `tools/drilldown.py` use per-buyer pull; `app` cards show per-buyer pull on each buyer badge (e.g. `CUSTOMER·4  operator·3`). Live-verified in browser.

## 2026-07-24 — hardware_buyer axis (taxonomy v3) + codex review actioned
**Why:** codex (independent review) showed the deployment-only on-prem/cloud split conflated substrate, hardware buyer, service model and deal motion — and buried the operator (ISV/managed) hardware deals the playbook §3 explicitly wants. Decision (Tuo: "我都要 + 把 buyer 更明確排出"): make **who buys the iron** an explicit field.

**Changed:**
- `data/taxonomy.yaml` → **v3**. New enum + per-category `hardware_buyer` (array of customer/operator/hyperscaler/oem), `primary_buyer`, `smc_reachable`. Assigned by a 17-agent workflow (per-cluster assign → adversarial verify → cross-cluster consistency critic). 5 consistency fixes applied (healthcare-cmms→operator primary; +oem smart-room; +operator or-surgical-video & radiation-oncology; icu-central-monitoring oem→customer primary for tie-break consistency — **the one debatable call, easy to flip**).
- Distribution: primary_buyer 44 customer / 9 operator. **26 HOT_customer (SMCI direct), 18 HOT_operator (ISV co-sell — previously invisible), 8 OEM design-wins.** 53/53 reachable.
- `tools/rollup.py` + `tools/drilldown.py` rewritten around hardware_buyer (buyer is now the authoritative "who controls hw" axis; deployment demoted to a guarded substrate descriptor — fixes codex's unknown→cloud and `['hybrid']` bugs).
- `app`: Taxonomy tab gains a hardware_buyer filter, primary_buyer/hardware_buyer group-by, per-card primary-buyer badge + other-buyer chips; rollup summary is buyer-centric. Live-verified in browser (group-by primary_buyer → 44/9; counts match rollup.py).

**Codex verdict was HOLD; actioned as:** applied the sharp/cheap fixes (OEM≠on-prem, explicit buyer replaces first-listed-deployment heuristic, substrate guards, operator co-sell surfaced). Did NOT accept codex's cloud-first reordering of ai-drug-discovery / clinical-data-lakehouse (fights Play B's on-prem + cloud-repatriation thesis).

**Open (for Tuo):**
1. `icu-central-monitoring` primary_buyer = customer (was oem) — flip back if the device-maker channel is really the bigger deal.
2. Per-actor hw_pull (codex wanted HOT_customer vs HOT_operator scored separately) — worth splitting, or leave single hw_pull?
3. Note hardware_buyer in CLAUDE.md §3 spec, or keep it as an evolved-in-repo field?

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
