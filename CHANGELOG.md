# CHANGELOG

## 2026-07-28 — backfill 78 leaderboard leaders into registry (FK 46%→96%) + Explore overhaul + v2.0
Two asks: complete the leaderboard↔registry fusion, and fix the confusing Explore filter panel.
- **Registry 231 → 309 (v8).** Backfilled **78 of the 84** market-leaders that were on a leaderboard but absent from the registry (Qure.ai, Lunit, HeartFlow, Cleerly, DeepScribe, Iambic, Bayesian Health, Greenway, SCC Soft, Tecsys, …). Each researched full §8 (HQ, founded, current-and-verified leadership, history, deployment) by the `backfill-vendors` workflow (9 chunks + 9 adversarial verifiers = 18 agents); the verify pass caught real tenure changes (DeepScribe's founder-CEO departed 2025 → current CEO Matthew Ko). Each is filed under its sub-segment's taxonomy category (imaging-ai-deployment, digital-pathology, ai-drug-discovery, ehr-emr-core, lis, …), so those 15 categories now carry a far fuller vendor list. **Leaderboard→registry FK: 71/155 → 150/155 (96%)** — nearly every ranked leader now click-throughs to a vendor card (verified: Qure.ai row → its card with 🏆 badge + Mumbai HQ). The 5 residual are the leaders the enrich pass couldn't confirm (ScriptPro, Datavant ×2, Health Gorilla, Foundation Medicine) — honest null.
- **Explore wayfinding overhaul** (committed in the same arc): the dense "Hardware-buyer rollup §3 gate…" text and raw 8-dropdown Refine panel replaced with a plain intro, clickable HOT shortcut chips (🎯 sell direct / 🤝 ISV co-sell / 🔩 OEM / 📋 show all — hyperlink guidance straight to each target list), one-click quick-view chips (by care area / who buys / play / hardware / data type / flat) replacing the cryptic group-by dropdown, a colour legend for the buyer badge, and labeled advanced filters under "More filters". Fully bilingual.
- **84 tests GREEN**; app deterministic; browser clean both languages.
- **Tagged `v2.0`** — the software-universe map is now fully fused: 59 categories · 309 vendors · 2 ranked leaderboards, cross-linked Home↔Explore↔Vendors↔Leaderboards.

## 2026-07-28 — relationship fusion across Home · Explore · Vendors · Leaderboards + v1.9
Wove the four browsing tabs into one connected graph instead of four separate lists, per Tuo ("關係統整以及融合").
- **Foreign key: leaderboard → registry.** `data/leaderboards.yaml` v2 adds `vendor_id` to every entry — **71 / 155** entries resolve to a registry vendor (name/alias/parenthetical matching); the other 84 are leaders not (yet) in the 231-vendor registry (mostly pure-AI startups — Qure.ai, Lunit, HeartFlow…) and stay honest `null`. This FK is what fuses Leaderboards ↔ Vendors ↔ Explore.
- **Bidirectional cross-navigation** (JS helpers `goVendor` / `goCategory` + the `LB_BY_VID` rank map): Explore vendor pills are now click-through to the vendor card (and carry a 🏆 badge when that vendor is a market leader); Vendors category chips show the real category name and click through to Explore; Vendors cards show a 🏆 `AI #n` / `No-AI #n` rank badge (63 cards) linking to the board; linked leaderboard rows (↩, 71 of them) click through to the vendor card; Home gains a 🏆 link to the leaderboards. Every link works both directions and in both languages.
- Tests: `test_vendor_id_foreign_key` (every entry has vendor_id; non-null ⇒ real registry id; ≥1 linked) + `test_cross_tab_fusion_wired` (goVendor/goCategory/lbBadge/LB_BY_VID present). **84 tests GREEN**; app deterministic; browser clean, cross-nav verified (Explore→vendor, leaderboard→vendor, vendor→category all jump correctly).
- **Tagged `v1.9`.**

## 2026-07-28 — market vendor leaderboards (AI + No-AI, ranked, sourced) + v1.8
Two market-wide leaderboards of the leading medical/pharma software vendors, ranked by market share / installed base, per Tuo (asked for ~100 each; "fewer is fine — don't pad").
- **`data/leaderboards.yaml`**: **AI board 66 · No-AI board 89** (155 total), every entry §8-sourced — a real cited figure or a sourced market position, no fabrication. Built by the `market-leaderboards` workflow (16 sub-segment researchers + 16 adversarial verifiers = 32 agents); the verify pass caught and fixed real errors (e.g. Qure.ai's "105 countries" was a TIME100 artifact → corrected to 100+). Grouped by sub-market and ranked by installed base / share within each: AI led by Aidoc (31 FDA clearances, ~2,000 hospitals), Qure.ai (4,800+ sites), Lunit (KOSDAQ-audited revenue); No-AI led by Epic, Oracle Health, MEDITECH (KLAS acute-care EHR share). Dual-play vendors (GE, Philips) appear on both boards.
- **New "Leaderboards / 榜單" app tab** (9th): two ranked columns, grouped by sub-segment, each row rank · vendor · market_basis · clickable source (155 source links). Fully bilingual.
- Ranking basis is market share / installed base first, sourced market-leader position where no number is public (§8) — never a bare number. `market-leaderboards.yaml` version 1.
- Tests: `TestLeaderboards` (both boards present, dense 1..N ranks, every entry has a market_basis, ≥80% sourced). **82 tests GREEN**; app deterministic; browser clean both languages.
- **Tagged `v1.8`.**

## 2026-07-28 — Home re-organised by point-of-care stakeholder × AI/No-AI + v1.7
Replaced the Home page's hunting-funnel (plays / HOT stats / trigger panel — those live on in Explore·Hunt·Triggers) with a stakeholder-first map of the whole 59-category universe, per Tuo's scheme.
- **New data axis `home_stakeholder`** (facility / doctor / nurse / patient / other) on every category + an enum. The taxonomy's `clinician` tag doesn't split doctor vs nurse, so this is an explicit editable-in-data judgment: 8 doctor (PACS, CDSS, RIS/CVIS, radiation-oncology, surgical video, 3D viz, digital pathology, EHR), 4 nurse (ICU monitoring, pharmacy automation, smart-room ambient, clinical-communication), 3 patient (portal, access/scheduling, telehealth), 14 facility (ERP, RCM, HIM, workforce, device-integration, RTLS, CMMS, IoT-sec, BMS, capacity-command, imaging-AI, data-lakehouse, HIE, LLM-serving), 30 other (all non-hospital-point-of-care: pharma, manufacturing, lab back-end, payer, medtech).
- **Home = 5 stakeholder blocks, each split AI-driven vs No-AI.** AI-ness is derived (role analytics-AI OR modality AI-models OR gpu-server in profile) — a JS helper, not stored. Counts render live (e.g. Facility 14 = AI 8 · No-AI 6; Patient 3 = AI 0 · No-AI 3). Clicking a category deep-links into Explore pre-searched to it. Fully bilingual via the existing toggle (設施/醫生/護理/病人/其他 · AI 驅動/非 AI).
- Tests: `home_stakeholder` added to REQUIRED_CATEGORY_FIELDS + enum-membership test; the two obsolete Home invariants (play-tile deep-link, trigger-panel label) replaced by `test_home_groups_by_stakeholder_and_ai` and a slimmed honesty check (still bars a false "trigger fired" CRM label). **79 tests GREEN**; app deterministic; browser clean both languages.
- **Tagged `v1.7`.** The doctor/nurse assignments are a first defensible pass — correct any in `data/taxonomy.yaml` (one line per category), no code change.

## 2026-07-28 — category #59 clinical-communication + full EN⇄中文 app toggle + v1.6
Two asks: close the on-shift-clinician-communication gap in the map, and make the whole universe map viewable in Chinese.
- **+1 category → 59: `clinical-communication-collaboration`** (nurse call, secure messaging, on-call scheduling, shift handoff) under `hospital-device-facility-operations`. Full six layers + workload_envelope (derived from tags via the helper: gpu none, capacity none, availability high-availability, latency real-time; judgment low/random-transactional/high). Deliberately modest (opportunity 2) — pure comms is SaaS-light under the §3 hardware gate — but real for a complete software-universe map. **7 vendors**: added the category to ascom/connexall/spok/qgenda + researched 3 new (Vocera/Stryker, TigerConnect, PerfectServe) §8-verified — Vocera leadership honest-null (now a Stryker unit, no independent current exec), TigerConnect → Sean O'Neal CEO, PerfectServe → Guillaume Castel CEO. Registry → 231.
- **EN ⇄ 中文 toggle across the whole app.** A header button flips a global `LANG`; all 8 tab renders refactored from run-once IIFEs into named functions + a `renderAll()` so a toggle re-renders live. Category display names switch to `name_zh` (with the English as the sub-line); nav labels, tab chrome, section titles, field labels (HQ→總部, Leadership→負責人, Market share→市佔, …), and the key hero/rollup strings switch via a `T(en, zh)` helper. Vendor company names stay English (proper nouns). Browser-verified both directions, category #59 renders in both languages, zero console errors.
- **78 tests GREEN** (59 categories, 231 vendors); app + hunting guide rebuilt (deterministic).
- **Tagged `v1.6`.**

## 2026-07-28 — vendor leadership backfill + market_share layer (registry v7) + v1.5
Closed the two vendor-page gaps: the 28 vendors missing a named leader, and a new **market_share** field across all 228. Filled by the `vendor-enrich2` workflow (10 chunks × research + adversarial verify, 20 agents) under the §8 no-fabrication rule.
- **leadership +22** (of 28 missing) — each a current, sourced named exec with tenure verified (e.g. Intelerad → Jordan Bazinsky CEO; ETQ → Vick Vaishnavi; Varian → Arthur Kaindl; Nonlinear Dynamics → Udit Batra via parent Waters). **6 stay honest null** (eq2, gatan, matrix-science, open-systems-pharmacology, systech, terarecon — no public exec found). Leadership coverage 200 → 222 / 228.
- **market_share +33** — a cited figure for a *defined* market, or null (bare percentages are §8-meaningless). Real ones landed: Epic 42.3% US hospitals / 54.9% beds, Oracle Health 22.9%, Meditech 14.8% (KLAS); NVIDIA ~90-94% GPU (Jon Peddie); Illumina >90% clinical NGS; Veeva ~80% pharma CRM; Olympus >70% GI endoscope; Varian >60% radiotherapy; ABB #1 DCS ~19%; Thermo Fisher ~24.5% mass-spec; SAP ~6.6% ERP; Databricks ~11% lakehouse; IQVIA largest CRO; Roche #1 IVD; plus Best-in-KLAS ranks (Sectra, Abridge, Dolbey). The other 195 are honest null — most vendors publish no share figure.
- **§8 held:** every filled value carries a real source folded into the vendor's `sources`; HTML entities from scraped text decoded; the adversarial verify pass nulled anything weak or tenure-stale. `market_share` is a descriptive **string** (figure + market + source), never a bare number — enforced by `test_market_share_shape`.
- Registry **v6 → v7**; vendor card + search now render market_share; RED `d23e271` → GREEN. **78 tests**; app rebuilt (deterministic), browser clean — 33 cards show market share, 222 show leadership.
- **Tagged `v1.5`.**

## 2026-07-28 — workload axis + codex/grok dual review actioned + v1.4
Shipped `drilldown.py --axis workload` (queryable envelope slices by gpu_role / capacity_band / concurrency / availability_class, reading STORED values — no second derivation), then ran the **codex + grok dual review** of the whole workload layer and actioned every real finding. codex = **RED** (§8 + correctness), grok = **YELLOW** (market, "ship for internal GTM; fix H1/H2"). They **converged** on the two load-bearing issues.
- **§8 (both reviewers): two per_unit numbers whose citations didn't support them → nulled.** `pacs-vna` 0.1–1.5 GB (Purview article gives no such general range) and `digital-pathology` 1–4 GB (DPA FAQ only says "may exceed 1 GB"; the 4 GB upper + CLIA/CAP WSI extension is practice/inference, not a cited interval). Both `per_unit_data_size → null`, sources trimmed to their real retention citations. `per_unit` now 2/58 (bioinformatics WGS, cryo-EM — both grok order-of-magnitude-OK); dropped the URL-less CAP source line. §8 held: a number is nulled unless its own citation carries it.
- **Correctness (both): the derived-band heuristics over-claimed.** `gpu_role` used `images && !AI → visualization`, which mislabelled GPU **dose-calculation** (radiation-oncology) and **video-AI** (surgical) as visualisation → helper now maps `simulation → mixed` and **never auto-emits `visualization`** (reserved for a tag-driven override). `latency_class` mapped `edge-industrial + time-series → deterministic-real-time`, over-claiming hard-real-time for soft edge telemetry (asset tracking, cold-chain) → helper now emits `real-time` and **never auto-emits `deterministic-real-time`** (reserved for genuine control-loop categories via tags). Re-derived: 0 spurious `visualization`, 0 spurious `deterministic-real-time`; `radiation-oncology`/`pat-twin`/`samd` correctly `mixed`.
- **Test hardening (codex):** INV-4 now checks the exact 5-key set + finite non-bool numeric bounds + `0 ≤ low ≤ high` + non-empty unit; INV-18 couples `massive` concurrency to a rack/cluster **compute/GPU/HA** tier, not arbitrary sizing (archive can't serve thousands of sessions).
- **grok market/ZH nits:** `advanced-visualization-3d` + `qc-lims-cds` `io_pattern → mixed`; `ms-proteomics-metabolomics` name_zh → 質譜蛋白質體學與代謝體學資訊分析. grok confirmed the `explosive` data_growth club (pathology/omics/genomics), the retention statute mapping (CMS/CLIA/MQSA/DSCSA/EU-CTR), and the 5 newest categories' ZH as A−.
- **77 tests GREEN**; app + hunting guide rebuilt (deterministic). This is the review-hardened workload layer.
- **Tagged `v1.4`.**

## 2026-07-28 — per-category workload_envelope quantification layer (taxonomy v7) + v1.3
Added the seventh layer of the chain: a per-category **workload_envelope** — the *typical* hardware demand a software category implies — so the taxonomy now bridges (software category) → (concrete SMCI sizing). Built by a **two-workflow chain the user asked for**: `design-next-step` (judge-panel that designed + adversarially self-reviewed the schema) → the `quantify-fields` **skill** (executes the fill). The design workflow's spec came back `survives=False` (3 field-scoped fails); owner-adjudicated 9 findings, then a re-verify workflow confirmed the hardened spec `survives=True` grounded on the real repo.
- **12-field envelope, provenance fixed by field identity** (nothing mislabelable): **derived** (`gpu_role` `capacity_band` `availability_class` `latency_class`) = `tools/workload_ceiling.py`, a PURE tag-only helper, `value == helper(tags)` exactly (INV-14); **framework-judgment** (`data_growth` `io_pattern` `concurrency`) = expert ordinals, same epistemic class as `hardware_opportunity`, no citation; **sourced** (`retention_horizon` `per_unit_data_size`) = real citation or honest null. Plus `scaling_driver` (the SE discovery question), `sources`, `notes`.
- **§8 held under fire**: no fabricated numbers. Bands not fake precision; the ONLY numeric atom is `per_unit_data_size`, gated to confidence A/B/C + a real, cross-listed, non-placeholder citation. Fill ran 8 domain-chunk agents + adversarial verify (16 agents); sourced fields came back conservative — **14/58 retention** (CMS 42 CFR 482.24, CLIA 493.1105, MQSA/ACR — genuine category-wide statutes) and **4/58 per_unit** (whole-slide image, NGS run, cryo-EM movie, imaging study, each cited); everything else honest null.
- **`concurrency`** added as a standalone queryable band on Tuo's call (design flagged it as the one cut sales signal). `single|low|moderate|high|massive`; INV-18 couples `massive` ⇒ a rack/cluster-sized component.
- **18 invariants** (`TestWorkloadEnvelope`, INV-1..18): provenance gate, helper-is-tag-only (so positive-equality can't go vacuous), per_unit/retention source-quality, prose digit guard, GPU crown + totality, capacity/io/growth/availability/latency ↔ tag coherence, SaaS-light degenerate, flagship non-degenerate. RED `be801f8` → GREEN. **76 tests** pass.
- Taxonomy **v6 → v7**; verified NO tool-gate edits needed (`rollup.py` gates `<6`, `drilldown.py` `<4`) — only the cosmetic rollup version string was fixed (it hardcoded "v6"). App + hunting guide rebuilt (deterministic, byte-identical run-to-run); browser clean, Home 31/15, `taxonomy v7`.
- Reusable: re-running the `quantify-fields` skill on category #59+ auto-fills its derived bands and scaffolds the rest. Deferred (separate wave): `drilldown.py --axis workload`.
- **Tagged `v1.3`.**

## 2026-07-28 — completeness-audit categories 53→58 (taxonomy v6) + v1.2
The v1 `.jsx` cross-check stayed blocked (files never on disk — Spotlight/find both empty). Pivoted to its actual purpose — *did we miss anything?* — via a 4-lens opus completeness audit (research-lifecycle · data-modality · role · AI-infra finders + adversarial verifier). 10 candidates surfaced, **5 confirmed genuine gaps**, 5 rejected with reasons.
- **+5 categories** (full six-layer, each aligned to every chain invariant): `pharmacometrics-modeling-simulation`, `ms-proteomics-metabolomics`, `spatial-biology-omics`, `healthcare-llm-serving`, `payer-actuarial-hpc`. These are pharma/omics/AI-infra targets the v1 hospital matrix never covered — `healthcare-llm-serving` (fastest-growing GPU buy) and spatial/MS omics are net-new hunting ground, so the pivot beat the diff it replaced.
- **+21 new vendors** (§8 web-researched + opus verify): Certara, Simulations Plus, ICON, Metrum, Open Systems Pharmacology; Biognosys, SCIEX, Bruker Spatial, Matrix Science, Nonlinear Dynamics (Waters); 10x Genomics, Akoya, Vizgen; NVIDIA NIM/BioNeMo, John Snow Labs, Hippocratic AI, Microsoft/Nuance DAX; Milliman, Moody's Analytics, FIS Prophet, WTW. **+4 category-adds** to existing (Thermo Fisher, Bruker, Indica Labs, Aidoc). Registry now **228 vendors (v6)**.
- RED `eb37cf4` (58 fixtures + 5 glossary terms, vendors:[] pending) → GREEN. **58 tests** pass; every new category ≥4 vendors, headline==max per-buyer, primary∈argmax, sizing keys==profile, payer carries play-exemption. Browser: Home 31/15, all 5 cats + vendors render, zero console errors.
- **Tagged `v1.2`.**

## 2026-07-28 — vendor market-gap adds (registry v5) + v1.1
Closed the vendor-gap backlog flagged by the codex/grok reviews. Same §8 web-research + opus verify discipline.
- **+11 new vendors**: Viz.ai, Hyland Acuo (VNA), Hamamatsu, Indica Labs (HALO), Flatiron Health (Roche), Velsera (Seven Bridges), ABB, Critical Manufacturing, Tulip, Olympus, Medtronic. **+5 category-adds** to existing enriched vendors (Epic Radiant → ris-cvis; GE / Philips / Siemens Healthineers → imaging-ai-deployment; Brainlab → or-surgical-video). Registry now **207 vendors (v5)**.
- §8 caught a resigned exec: Olympus CEO draft "Stefan Kaufmann" (resigned Oct 2024) → corrected to Bob White (current, June 2025); Flatiron/ABB sources swapped to verify current CEOs. Honest-null discipline held.
- imaging-ai-deployment went from a thin/aging list to 9 vendors incl. the major platform channels; ris-cvis gained Epic Radiant. Tests 58 GREEN.
- Also: app build made deterministic (dropped wall-clock "built" timestamp — same fix as hunting_guide; rebuild is now byte-identical run-to-run).
- **Tagged `v1.1`.**

### Still blocked
- v1 `.jsx` cross-check — `/source/` remains empty; drop the two files to diff v1 vendor/category data against the current 207 vendors + 53 categories.


## 2026-07-27 — Home-UX dual review actioned (deep-links + honesty)
codex + grok reviewed the new Home funnel; consensus P1s = the funnel made false promises. `8859aa1` RED → `9b367d6` GREEN (58 tests).
- **Deep-links, not dumps**: `goTab(id, opts)` parameterized; play tiles scroll to their own Play section in Hunt (`hunt-play-*` anchors); HOT stat cards prefilter Explore to the exact per-buyer HOT list.
- **Card count == delivered count**: clicking HOT_customer shows 26, operator 14, OEM 3. The first cut filtered on headline opportunity and wrongly showed 30 — caught by live JS eval (TUo #1: verify against reality), then fixed with a per-buyer opportunity filter.
- **Consistency + honesty**: Explore OEM count now opp≥3 (3, matching Home + guide, was 8); "A trigger fired?" → "Highest-urgency signals" (it is a static slice, not CRM state); hardcoded 14/53 → dynamic lengths; play tiles show operator/OEM opportunity + a ranking tie-break.

## 2026-07-27 — guided Home funnel + classified Explore (wayfinding redesign)
The app landing was a filter-wall (8 dropdowns + 53 flat cards) — no guidance. Grilled (Tuo, Q1 → funnel front door). `5b19eb9` RED → `9453037` GREEN.
- **Home** tab (new default): "Where do you want to hunt?" + §3 gate; 3 HOT stat cards (26/14/8); three Play tiles with their top categories → Hunt; a fired-trigger panel → Triggers. `goTab()` wires the funnel.
- **Taxonomy → Explore** (demoted): 8 filters collapsed into a "Refine" `<details>` panel; defaults to **group-by-domain** (8 clean buckets), never a flat 53-wall. `domain` added as a group-by axis.
- Tests 48 → **53** (Home-is-default + surfaces plays/HOT/trigger + Explore filters collapsible). Browser-verified.

## 2026-07-27 — vendor enrichment: HQ / leadership / history / market (registry v4)
Every vendor now carries the profile a salesperson needs, all sourced. `5fb4dde` RED → `61ffc6a` GREEN.
- 8 web-research agents + 8 opus adversarial verifiers over all **196 vendors** (419 web searches). Added `headquarters`, `founded`, `leadership`, `history`, `market_position`, `sources[]`.
- **§8 fabrication guard, machine-enforced**: unsourced revenue figures → "not publicly disclosed" (InterSystems, Thermo Fisher, Veeva, Yokogawa, Cotiviti…); unconfirmable or stale CEO names → nulled/corrected (Cognex Willett→Moschner; Optum Conway[OptumRx]→Cianfrocco; Ordr/Infinitt/Ziosoft/Connexall/Körber nulled); 404 and copy-paste-error source URLs dropped. Honest nulls beat guesses.
- Coverage: HQ 187/196 · founded 178 · leadership 173 · market_position disclosed 107 (89 honestly "not publicly disclosed" — private companies without public share data).
- Tests 44 → **48**: enrichment schema + the §8 sourcing invariant (any named leader / market claim / history requires ≥1 source). App gains a **Vendors** tab (searchable registry, clickable sources); browser-verified.
- Note: `v1.0` tag predates this; the enriched registry is a superset — re-tag as `v1.1` when the vendor-market-gap adds also land.

## 2026-07-27 — v1.0 freeze: docs + deliverable dual-review + tag
Closed the loop on the deliverable and froze a stable release.
- **Docs**: `docs/glossary.md` now generated from `taxonomy.yaml` glossary (49 terms, single source, `tools/glossary_md.py`); `docs/workflow.md` per-phase checklists expanded to reference the real artifacts; `hunting_guide.py` made deterministic (version+counts, not wall-clock) so the smoke test no longer dirties the tree; `rollup.py` v4→v6 drift fixed.
- **Deliverable dual-review** (codex + grok on `hunting-guide.md`, web-search): actioned P1s — OEM master-HOT filter bug (8→3), §5.4-excluded vendors now marked ⊘, trigger index shows category→play/standalone, fail-closed generator validation; play re-routing (samd off play-a, rwd/ngs-lims/genomics-reporting off play-b); radiation-oncology +storage; NVIDIA product-line name fixed; cloud-cost-pressure action + trigger category opens.
- **Tests 43 → 44** GREEN; determinism proven (repeat runs leave the tree clean).
- **Tag `v1.0`** — taxonomy v6, 53 categories × six-layer chain + domain + name_full + glossary + hardware_profile + sizing, 196 sourced vendors, 14 triggers with foreign keys, the hunting guide, and a 44-test regression net.

### Open backlog (post-v1.0, not blockers)
- Vendor enrichment: market-gap adds flagged by grok (Epic Radiant on ris-cvis; Viz.ai / GE / Siemens / Philips on imaging-ai-deployment; Hyland Acuo on pacs-vna; Flatiron on rwd-rwe; Hamamatsu/Indica on digital-pathology; ABB on scada-dcs). Each needs a cited source per §8.
- Per-buyer "what to quote" (customer vs operator vs OEM hardware split).
- ris-cvis-workflow profile/score (grok flagged; prior opus ruling stands — revisit with evidence).
- v1 `.jsx` cross-check — still blocked on `/source/` file drop.

## 2026-07-27 — hunting guide: the sales-facing deliverable
The payoff — four rounds of verified six-layer data synthesized into the artifact an account manager hunts with. `688391b`.
- `tools/hunting_guide.py` → `docs/hunting-guide.md` (single-source from `/data`): per-play ranked target maps (category × opportunity × what-to-quote [component·sizing] × co-sell/incumbent vendors), cross-play standalone deals, master HOT lists, trigger→action index, component pipelines.
- App gains a **Hunt** tab rendering the per-play ranked view (quote + vendors); browser-verified.
- Correctness fix the guide surfaced: `clinical-data-lakehouse` dropped `play-b` (it's a clinical data warehouse, not genomics/research-AI — grok flagged this in round 1) → `play_exemption`; `hospital-ma` trigger `related_plays` → `[play-a]`.
- Tests 42 → **43** (hunting-guide smoke test). All GREEN.

## 2026-07-27 — refinement round 4: component sizing + vendor dual-review (registry v3)
Two parallel tracks, same TDD + dual-review discipline. `1cf8339` RED → `c09559f` sizing GREEN → `f132f15` vendor fixes.

**Per-component sizing** (`hardware_profile_sizing`): node / rack / cluster deployment scale per component → each category maps to a Supermicro quote size. Opus sizer + opus verifier (18 agents); 2 inflations deflated. Tiers: 50 node, 37 rack, 15 cluster. Test enforces sizing keys == profile and flagship-customer → ≥1 rack/cluster component. App chips show the tier.

**Vendor dual review** (codex on repo + grok on worktree, both web-search + citations):
- Acquisition/ownership updates with cited close dates: AspenTech→Emerson, Dotmatics→Siemens, Nuvolo→Trane, Paige→Tempus AI, Intelerad→GE HealthCare, Fabric Genomics→GeneDx, Congenica→SeqOne, AVEVA→Schneider, Wind River→Aptiv; Siemens scope corrected.
- Deployment corrections (MasterControl/Nuvolo cloud-only, TeraRecon +SaaS, DNAnexus overclaim dropped); blackford-analysis Bayer wind-down noted.
- Removed brightinsight (cloud SaaS mis-filed as embedded-OEM); merged duplicate philips-healthcare→philips.
- Market gaps filled: GE HealthCare & Philips added to pacs-vna; new vendors PathAI (digital-pathology) and Tempus AI (real-world-data + clinical genomics).
- §8 hygiene: 6 unverifiable note claims stripped; 24 confidence B→C downgrades where the sole source was a listicle/blog.
- Registry v3, 196 vendors, every category still ≥2. Tests 41 → **42** GREEN.

**Still blocked:** v1 `.jsx` cross-check — `/source/` empty; drop the files to run a diff of v1 vendor/category data against the current 196 vendors + 53 categories.

## 2026-07-24 — refinement round 3: vendors layer filled (196 vendors, web-researched)
`5ca96df` RED (registry schema + foreign keys + ≥2-per-category invariants) → `1f78bab` GREEN.
- 8 domain research agents (live web search) + 8 opus adversarial verifiers → **196 unique vendors**, every entry source-cited per §8. Confidence: 146 B / 50 C (verifiers downgraded ~25 entries whose only source was an aggregator blog).
- **Verification caught one fabrication** (TriNetX "acquired by Roche" — false; Carlyle majority-owned) and stripped unverifiable revenue/date claims — the §8 no-fabrication rule enforced by machine, not trust.
- Cloud-locked clinical SaaS (Veeva, Medidata, Benchling) carries the §5.4 co-sell-exclusion note.
- Coverage: all 53 categories, 3-8 vendors each. Category vendor lists injected into taxonomy; app cards render vendor chips.
- Tests 34 → **38** GREEN. Note: v1 `.jsx` extraction is now superseded — the researched registry is richer than the v1 vendor examples; drop the files in `/source/` anytime for a cross-check diff.

## 2026-07-24 — refinement round 2 (play-scope honesty + trigger foreign keys + market rulings)
Same discipline loop (test-driven-development RED→GREEN, opus adjudication, codex+grok dual delta review). Commits: `e7868fa` RED → `c315a3e` GREEN → `9fd35dc` opus rulings → `2ff3b2a` dual-review actioned.

1. **Play-scope honesty**: 10 reachable-HOT categories outside the three plays now carry an explicit `play_exemption` reason — no silent unroutable pipeline.
2. **Trigger foreign keys**: all 14 triggers bind `related_categories` + `related_plays` (validated; every trigger routes to ≥1 category; every routed play must be carried by a related category).
3. **Opus market rulings** on the 9-item grok backlog: 3 accepts / 6 evidence-rule rejects (per-buyer score = per-deal size, not market share; graphics-memory ≠ system memory).
4. **Dual delta review**: grok found 5 trigger-binding P1s + 2 weak exemption texts + 7 test escapes; codex found 4 P2s including a dead-binding test gap. **Cross-model consensus overrode two opus accepts** (clinical-trial-suite NVMe, capacity-command-center HPC-CPU — profiles reverted to empty; §5.4 co-sell exclusion + wrong component semantics). 9 trigger bindings fixed; 2 exemptions rewritten.
5. **Test suite: 33 → 34**, all GREEN. App renders trigger Related column + exemption notes.

**Open:** grok's declined suggestions logged (action-text↔play string matching — fragile; exemption-quality semantic checks — not mechanically testable).

## 2026-07-24 — six-layer chain refinement (taxonomy v6) — TDD + grill-me + superpowers + codex/grok dual review
Pipeline per Tuo's directive: three disciplines (test-driven-development · grill-me · using-superpowers), opus refinement agents, codex reviewing this repo + grok reviewing a dedicated worktree (`/Volumes/ClaudeNVME/medical-software-grok-review`).

**Commits:** `398cc59` RED (17 tests, 10 failing) → `828a56f` GREEN v6 → `00849a5` opus audit fixes → `36d8c40` dual-review hardening.

1. **Grill decision D1 (Tuo)**: ids stay compact; every category gains `name_full` (zero-abbreviation full name); enum values + field names expand; `glossary` block (now 49 entries, EN+ZH, Latin-free zh) canonically expands every surviving acronym.
2. **Abbreviations opened everywhere**: `cro`→`contract-research-organization`, `on-prem`→`on-premises`, `SaaS`→`software-as-a-service`, `oem`→`original-equipment-manufacturer`, `dr-backup`→`disaster-recovery-backup`, trigger categories, tool constants, …
3. **Everything classified**: `domain` field (8-value closed enum, was comments); triggers gained closed enums; headline opportunity = max(per-buyer) rule.
4. **Opus layer audit** (6 agents, high effort): 7 accepted fixes — payer added to hie (CMS-0057-F), digital-pathology +biotechnology-pharmaceutical, advanced-visualization-3d de-labbed, 3 name_full fixes, payer-um per-buyer scores un-inverted.
5. **Dual external review**: codex 11 P1 + 4 P2; grok P1/P2 sets. Overlap (highest confidence): rollup.py OEM KeyError crash (real, reproduced — earlier verification had truncated output with `head`, hiding it), no smoke tests, samd domain misfiled, name_full under-expansion, thin glossary. All P1s actioned; market fixes: ai-hpc deflated (GPU double-count), rcm operator deflated, primary_buyer=argmax rule (him-coding/cdss→operator, samd→oem), hyperscaler-buyer↔cloud-substrate coherence, OEM removed from deployment enum.
6. **Test suite v2**: 17 → **29 tests** — inventory lock (53 + exact ids), id→domain fixture, enum membership (not blacklist), primary=argmax, buyer-substrate coherence, glossary coverage + Latin-free zh, trigger vocabulary lock, subprocess smoke tests for rollup/drilldown/score. **29/29 GREEN.**

**Open (for Tuo):** grok P2 backlog not yet actioned (rd-lab modality omics?, ai-drug-discovery high-memory?, population-health storage, HOT-without-play marker, trigger↔category foreign keys) — next refinement loop candidates.

## 2026-07-24 — hardware_profile: category → SMCI component bridge (v5)
Next drill-down layer: what hardware each category actually pulls, structured from the prose `infrastructure_notes` into a controlled component set — the bridge from software category to Supermicro product line.
- `data/taxonomy.yaml` → **v5**. New enum + per-category `hardware_profile` (subset of `gpu-server · hpc-cpu · nvme-performance · capacity-archive · high-memory · edge-industrial · ha-redundant · dr-backup`). Assigned by a 17-agent workflow (profile → adversarial verify → consistency critic). Verify pruned speculative tags (pacs-vna dropped gpu-server — GPU belongs to imaging-ai-deployment; comp-chem dropped then re-added high-memory). 7 consistency fixes applied (icu +nvme; workforce/patient-access dropped thin-terminal edge; ngs-lims + genomics-reporting nvme→[]; comp-chem + cryo-em +high-memory).
- Component pipelines (categories pulling each): **gpu-server 20 (15 customer-HOT)**, edge-industrial 16, ha-redundant 16, nvme-performance 15, capacity-archive 15, dr-backup 9, hpc-cpu 8, high-memory 2. 8 SaaS-light categories carry an empty profile (honest).
- `tools/drilldown.py --axis component` prints the pipelines; `app` gains a hardware filter, hardware_profile group-by, and per-card component chips. CLAUDE.md §3 documents it. Live-verified in browser (no console errors; chips render; pacs-vna correctly GPU-free).

## 2026-07-24 — tidy remaining abbreviated field names
Renamed jargon/abbreviated fields across data + tools + app + spec for readability:
- `smc_reachable` → `supermicro_reachable`
- `play_refs` → `plays` · `vendor_refs` → `vendors` · `vendor_ref` → `vendor`
- `infra_control` → `infrastructure_control` (account lite field + scoring item key)
- `infra_notes` → `infrastructure_notes`
- account `trigger.ref` → `trigger.id`
- 234 + 56 token replacements across taxonomy.yaml, scoring.yaml, accounts/*, score.py, rollup.py, drilldown.py, build_app.py, templates. 0 residual abbreviations. Re-verified: score.py → 77.0 Active pursuit (unchanged); rollup/drilldown/build green; app renders (no console errors, taxonomy cards + badges intact).

## 2026-07-24 — rename hw_pull → hardware_opportunity (clarity)
Field name `hw_pull` was internal jargon. Renamed across data + tools + app + spec to read professionally and pair with `hardware_buyer`:
- `hw_pull` → **`hardware_opportunity`**; `hw_pull_by_buyer` → **`hardware_opportunity_by_buyer`**; `hw_pull_rollup` → `hardware_opportunity_rollup`.
- Added the 1–4 scale in words everywhere: **1 minimal · 2 modest · 3 significant · 4 flagship** (taxonomy enum comment, CLAUDE.md §3, app summary legend, CLI, per-badge tooltips).
- App: filter now reads `opportunity ≥`, group-by shows `opportunity 4 (flagship)`, badges tooltip the tier word.
- 141 token replacements across taxonomy.yaml + 3 tools + templates + README; CLAUDE.md prose reworded. 0 residual `hw_pull`. Tools + app re-verified (v4, 53 cats; HOT_customer 25 / HOT_operator 16 / OEM 8 unchanged; browser-checked).

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
