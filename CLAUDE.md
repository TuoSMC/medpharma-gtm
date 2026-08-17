# SMCI Medical / Pharma GTM — standing context

I am Tuo Cheng, SMCI account manager. This repo is a **classification / hunt map**
that maps medical & pharma software to the hardware underneath
(GPU, HPC, NVMe, archive, edge, HA/DR). It is **not** a 30-account CRM.
Re-read this file at the start of every session. It is the memory — not the CHANGELOG.

## Gate (always first)
Who controls the infrastructure behind the software?
- **customer** → SMCI **direct** (end org buys its own on-prem iron)
- **operator** → **ISV / service-provider co-sell** (vendor/CRO/CDMO runs dedicated single-tenant iron)
- **oem** → **design-win** (software embedded in a device/instrument; per-unit BOM)
- **hyperscaler** → **out of scope** (public cloud; hardware bought by the hyperscaler)

No answer → not a deal. **Software user ≠ hardware buyer.**

## Spine
```
Gate → Play A/B/C/D → 59 locked categories → door → battle card → vendor slug → quote
 S0        S1              S2                  S3       S4            S5         S6
```
Each category carries `primary_buyer`/`hardware_buyer` (S0), `hardware_profile` (the SMCI
component set it pulls: `gpu-server · hpc-cpu · nvme-performance · capacity-archive ·
high-memory · edge-industrial · ha-redundant · dr-backup`), and per-buyer
`hardware_opportunity` (1 minimal · 2 modest · 3 significant · 4 flagship).
**Enum values and field names live in `data/taxonomy.yaml` enums, not in this file.**
The 100-pt scoring model lives in `data/scoring.yaml`; plays in `data/plays.yaml`;
triggers in `data/triggers.yaml`. Do not hand-maintain parallel copies here.

## Current state (2026-08-17, plan-v6.1)
- taxonomy v7: **59 locked categories** (`TestInventoryLocked`), **999 subcategories**
  (L1 225 / L2 461 / L3 240 / L4 44 / L5 29) — the tree is an **archive, not the spine**.
- Default tree: **categories only**. L1 on the open card. L2+ archived.
- HOT list for humans = the **35** categories with `hardware_opportunity >= 3` (opp≥4 = 9). Not 472 subs.
- Vendors: **309** (slug PK). Intel: **408** web-verified (FK incomplete — E4a). Plays: **4**. Triggers: **14**.
- Accounts: **1** fictional example card. Do not invent real accounts.
- App: single-file HTML built by `tools/build_app.py` from `data/*.yaml`; `app/index.html` ==
  `docs/index.html` byte-identical (GitHub Pages). Live tabs: **Explore · Method · Vendors**.
- Branch: **taxonomy-tree**. `main` serves stable Pages (v5.2-era). Do not merge until plan-v6 L1–L3 green.
- Plan of record: `plan-v6/PLAN.md` (v6.1). Next ticket: whichever E-phase is open. Paste its §9 ticket header.

## Agent contract (plan-v6.1 discipline)
- **Do not Read** `data/taxonomy.yaml`, `app/index.html`, or `docs/index.html` (2.27 MB / 3.8 MB).
  Interpreters may parse them; **models may not** load them into context.
- After `tools/taxquery.py` exists (E2): use `python3 tools/taxquery.py …` to query the tree.
- **One index is the source of truth** (C2/D7): app + taxquery read `taxonomy_index.yaml`;
  neither recomputes `visibility` / HOT / the card diversity rollup.
- **Ship default-only HTML** (C3/D8): build injects 59 + card L1 + rollup; archived L2+ is lazy JSON.
- **Do not add subcategories** unless Tuo approved in writing **and** a buyer-or-profile change the
  default tree actually needs (D6). Default answer is no. No deepen factories. No 12-agent panels. One executor.
- UI edits read functions in `tools/build_app.py` (or `app/template.html` after E5), never generated HTML.
- End session: ≤8-line CHANGELOG. This Current state block is the memory.

## Hard scope
- **4 plays only** — A imaging + digital pathology · B genomics / bioinformatics / research-AI ·
  C GMP manufacturing edge · D clinical core resilience & ransomware DR. **Play E rejected**
  (payer stays a segment tag, not a hardware anchor). One-liners + targets in `data/plays.yaml`.
- ISV co-sell **excludes** AWS-committed clinical SaaS (Veeva, Medidata — near-zero co-sell room).
- Evidence confidence on every factual claim: **A** customer/RFP/contract · **B** official public
  source · **C** job posting/conference/case study · **D** inference. Job postings ≠ installed base.
- **Never fabricate** vendors, accounts, or market facts. Unverified → confidence `D` + `TODO`; cite the source in the yaml.
- **Data and code stay separate.** Edit yaml, rebuild. Never hand-edit `index.html`.
