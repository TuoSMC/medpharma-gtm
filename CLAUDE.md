# CLAUDE.md — SMCI Medical/Pharma GTM Playbook v2
> **How to use:** create a new repo (e.g. `medpharma-gtm`), save this file as `CLAUDE.md` at the root, open Claude Code, and say: *"Read CLAUDE.md and execute the First Task."* This file is standing context — re-read it at the start of every session.
## 1. Context
- I am Tuo Cheng, Account Manager at Super Micro Computer (SMCI).
- Goal: a repeatable research + sales playbook to find organizations that **use** medical/pharma software and sell them the hardware infrastructure underneath (GPU servers, storage, HPC, edge).
- Constraint: **one-person execution** (me + FAE support). No marketing team. Everything must be lean and immediately operational — no research-project sprawl.
- My separate financial-analysis system (~6,000 companies) can later feed the account universe — design the account data layer so bulk import is possible.
- Working language: English for data/terminology; Traditional Chinese for docs when I ask.
## 2. What already exists (v1, built in Claude chat)
1. `medpharma-gtm-playbook.jsx` — 5-tab React artifact: software map (10 categories with hardware-opportunity ratings), 8-phase research workflow, buyer personas, 10 trigger signals, 5-stage sales motion + priority stack.
2. `hospital-software-taxonomy.jsx` — hospital software matrix: stakeholder (patient / clinician / device / facility) × dimension (clinical / ops / business / admin / regulatory), ~35 categories with EN/ZH terms, vendor examples, hardware-opportunity ratings.
3. An external strategy framework (text doc) contributing: the 8-factor account formula, deployment-operator decision tree, 4 GTM motions, 6-role buying committee, 10-phase research workflow, 100-pt opportunity scoring, 7 solution plays, facility-level granularity, A–D evidence confidence.
4. A merge analysis was completed. The decisions in §3 are **FINAL** — implement them, don't relitigate.
If I drop the two `.jsx` files into `/source/`, **extract their category and vendor data** into the data layer instead of retyping.
## 3. Binding framework (the spine)
```
Account Opportunity = Segment × Business Workflow × Software Stack
                    × Deployment Operator × Workload Profile
                    × Regulatory Boundary × Buying Committee × Purchase Trigger
```
**Gate question, always first: who controls the infrastructure behind the software?**
No answer → not in pipeline. Software user ≠ hardware buyer.
### Merge decisions (final)
| Dimension | Decision |
|---|---|
| Segments | 8 customer types: Hospital/Health System · Diagnostic/Reference Lab · Academic Medical Center · MedTech/IVD · Biotech/Pharma · CRO · CDMO · Payer |
| Software taxonomy | Every entry tagged on 4 dims: **lifecycle** (research→post-market), **role** (system-of-record / workflow / data-acquisition / integration / analytics-AI / infra-platform / regulated-SaMD), **data modality** (transactional / images / omics / time-series / documents / simulation / AI-models / RWD), **deployment** (on-prem / private / hybrid / public / SaaS / managed / OEM / edge). Hospital matrix (stakeholder × dimension) kept as the hospital drill-down view. Vendor names live in **data files, never in code** — they go stale. |
| Deployment operator | Decision tree drives GTM motion: customer-operated → **direct** · SaaS → **ISV platform team** · CRO/CDMO-run → **service provider** · embedded-in-device → **OEM** |
| Workload | Quantified fields per account: data/day, total capacity, growth %, retention, GPU type+qty, train/inference, IOPS, throughput, latency, concurrency, RTO/RPO, platform (bare-metal/VM/K8s/HPC). The 4-level `hardware_opportunity` rating (1 minimal · 2 modest · 3 significant · 4 flagship) survives only as a rollup summary. |
| Regulatory | **Cross-cutting field, not a category**: PHI / GxP / Part 11 / SaMD flags per account. In regulated deals, documentation IS the product: controlled BOM, firmware/driver matrix, change notification, lifecycle statement, hardening guide. |
| Buying committee | 6 roles per opportunity: Business Owner · Application Owner · Infrastructure Owner · Data/AI Owner · Risk Approver · Economic Buyer. Keep v1's sales-cycle estimates and entry points. |
| Triggers | Keep v1's operationalized list (each = signal + source + window + action); add the four from the framework doc. Full seed list in §6. |
| Scoring | 100-pt weighted model (§4). The v1 priority stack is a hypothesis only — replaced by per-account scores. |
### Taxonomy evolution — the `hardware_buyer` axis (added 2026-07-24, taxonomy v4)
A second-opinion review showed the deployment tag conflated *substrate* with *who buys the iron*, and buried the operator (ISV/managed) deals the gate question is meant to surface. So the taxonomy now carries **`hardware_buyer`** — the authoritative answer to §3's gate — per category:
- **customer** → SMCI **direct** (end org buys its own on-prem iron)
- **operator** → **ISV / service-provider co-sell** (a vendor/CRO/CDMO runs dedicated single-tenant iron to deliver the software as a service)
- **oem** → **OEM design-win** (software embedded in a device/instrument; per-unit BOM)
- **hyperscaler** → out of scope (public cloud; hardware bought by the hyperscaler)

Each buyer carries its **own** `hardware_opportunity_by_buyer` score (a customer deal and an operator deal for the same category are sized independently; scale 1 minimal · 2 modest · 3 significant · 4 flagship). `deployment` survives only as a secondary substrate descriptor. Derived, single-source lenses live in `tools/rollup.py` and `tools/drilldown.py`; the app filters/groups on buyer. HOT lists: **HOT_customer** (customer opportunity≥3, direct), **HOT_operator** (operator opportunity≥3, co-sell), **OEM design-wins**.

Each category also carries **`hardware_profile`** (taxonomy v5) — the SMCI component set it pulls, the bridge from software category to product line: `gpu-server · hpc-cpu · nvme-performance · capacity-archive · high-memory · edge-industrial · ha-redundant · dr-backup`. `tools/drilldown.py --axis component` prints the per-component pipelines (e.g. gpu-server = 20 categories, 15 customer-HOT); the app filters/groups on it. SaaS-light categories legitimately carry an empty profile.
## 4. Scoring model (100 pts)
Each item scored 0–5, weighted score = (item ÷ 5) × weight.
| Item | Weight |
|---|---|
| Customer controls infrastructure | 20 |
| Compute / storage intensity | 20 |
| Clear refresh or expansion trigger | 15 |
| Mission criticality / availability | 10 |
| Data growth / retention | 10 |
| Multi-site repeatability | 10 |
| ISV / SI partner access | 10 |
| Competitive differentiation | 5 |
Tiers: **≥70 Active pursuit** · 50–69 Nurture/partner-led · 30–49 Monitor · <30 Drop.
## 5. Hard scope constraints
1. **4 solution plays** (started as a 3-play trio; **Play D added 2026-07-29** after an adversarial data review — see plays.yaml header. A proposed **Play E (payer/RWD) was rejected** as a segment bucket, not a hardware anchor; "payer" stays a segment tag):
   - **Play A — Medical Imaging + Digital Pathology**: GPU inference, NVMe ingest, PB-scale archive. Targets: hospitals, imaging centers, pathology labs, PACS/pathology ISVs.
   - **Play B — Genomics / Bioinformatics / Research AI** (incl. cloud-repatriation targets): HPC + GPU clusters, NVMe scratch, object storage. Targets: AMCs, biotech, pharma R&D, AI-native drug-discovery companies.
   - **Play C — GMP Manufacturing Edge**: MES / SCADA / Historian / EBR — redundant plant servers, industrial edge, DR. Targets: pharma plants, biologics facilities, CDMOs, MES ISVs + automation SIs.
   - **Play D — Clinical Core Resilience & Ransomware DR**: NVMe-OLTP DB nodes + HA-redundant failover + immutable DR/backup (explicitly zero-GPU). Routes the only play-less flagship (EHR/EMR) plus LIS, Hospital ERP, device integration, HIE, payer core admin. Targets: hospital/health-system core-IT & payer claims-IT (direct). Ties to the cyber/ransomware, EHR go-live, hospital M&A, new-campus triggers.
2. **30 target accounts max**, researched at **facility level** (a pharma's genomics center ≠ its sterile plant — different stack, budget, buyer).
3. **Lite card first; full card only at score ≥70.**
4. ISV co-sell **excludes** AWS-committed clinical SaaS (Veeva, Medidata — near-zero co-sell room). Focus on ISVs still deploying on-prem: PACS/pathology, LIMS, MES vendors.
5. Every factual claim in data files carries evidence confidence: **A** customer/RFP/contract · **B** official public source · **C** job posting/conference/case study · **D** inference. Job postings are never "confirmed installed base."
## 6. Trigger seed list (for `triggers.yaml`)
Each entry: signal · category · urgency · monitoring window · source · prescribed action.
From v1: new EHR go-live · FDA IND filing (ClinicalTrials.gov) · FDA NDA/BLA approval · new sequencer purchase (90-day hardware window) · cloud-repatriation signals (earnings calls, "reducing cloud spend") · hospital M&A / consolidation · pharma AI-strategy announcement · new hospital campus/expansion · HPC/bioinformatics job postings · KLAS/HIMSS rankings.
Added from framework doc: cyber incident / ransomware · plant modernization or new plant · serialization mandate · cloud cost pressure.
## 7. Repo structure to build
```
/data       taxonomy.yaml · plays.yaml · triggers.yaml · scoring.yaml
            vendors.yaml · accounts/*.yaml
/templates  account-card-lite.md · account-card-full.md
/tools      score.py  (CLI: reads an account yaml → weighted score + tier + gap fields)
/app        v2 single-page playbook UI (tabs: Taxonomy · Plays · Triggers · Scoring · Accounts)
            — renders from /data, no hardcoded content
/docs       workflow.md (lean 10-phase process) · glossary.md (EN/ZH terms)
/source     drop zone for v1 .jsx files and research docs
CHANGELOG.md
```
### Lite account card (screening — 10 fields)
Company · Facility · Segment · Software domain + vendor · Deployment model · Operator · Trigger + timing · Infra control (Y/N/partial) · Evidence + confidence · Next step
### Full account card (score ≥70 only)
Extends lite with: business workflow + KPI + pain point · workload profile (all §3 quantified fields) · regulatory flags · full 6-role buying committee · hardware hypothesis + proposed reference architecture · competitive position · estimated value · PoC success criteria.
## 8. Working rules
- **Data and code stay separate.** The UI renders whatever is in `/data`; updating a vendor list must never require touching code.
- **Never fabricate** vendor, account, or market facts. Unverified entries get confidence `D` + a `TODO` marker. If web research is used, cite the source in the yaml.
- When I paste research notes, normalize them into `/data/accounts/` using the card schema — ask only when a required field is genuinely absent.
- Keep the app dependency-light (single-page React or plain HTML is fine). Prefer small diffs.
- End every session with a CHANGELOG entry (date · what changed · open questions).
## 9. First task
1. Scaffold the repo per §7.
2. Seed `scoring.yaml`, `plays.yaml` (3 plays), `triggers.yaml` directly from this file.
3. Build `tools/score.py` and demonstrate it end-to-end on ONE example account card (use a fictional-but-realistic digital-pathology hospital account, all fields confidence `D`).
4. Propose the `taxonomy.yaml` schema (show me the structure with 2–3 filled examples) — **stop and wait for my approval before filling the full taxonomy.**
