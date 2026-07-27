# SMCI Medical / Pharma Hunting Guide

> Generated from `/data` (taxonomy v6, 53 categories, 196 vendors). Deterministic — do not edit by hand; regenerate with `python3 tools/hunting_guide.py`.
>
> **Gate question first (CLAUDE.md §3): who controls the infrastructure behind the software?** No answer → not in pipeline.

**Opportunity scale** 1 minimal · 2 modest · 3 significant · 4 flagship. **Sizing** node < rack < cluster. **Buyer motions**: customer = direct · operator = ISV/co-sell · OEM = design-win · hyperscaler = out of scope.

## 1 · The three plays — ranked target maps

### Medical Imaging + Digital Pathology  (`play-a`)
*Hardware anchor:* GPU servers (inference-optimized), NVMe storage servers, High-density object/archive storage
*Regulatory:* PHI always; SaMD flag if AI algorithms deployed clinically

| Category | Cust | Oper | OEM | What to quote (component · scale) | Co-sell / incumbent vendors |
|---|:--:|:--:|:--:|---|---|
| **Digital Pathology Platform (WSI workflow + AI-assisted diagnosis)** <br><small>digital-pathology</small> | 4 | 3 | 2 | gpu-server (cluster), nvme-performance-storage (rack), capacity-archive-storage (cluster) | Leica Biosystems (Danaher), Paige (Tempus AI), PathAI, Philips (Koninklijke Philips N.V.), Proscia, Roche Diagnostics, Sectra |
| **Imaging AI Deployment Platform (Inference Orchestration / Marketplace)** <br><small>imaging-ai-deployment</small> | 4 | 4 | · | gpu-server (cluster), edge-industrial (node), high-availability-redundant (rack) | Aidoc, Blackford Analysis (Bayer — imaging-AI platform business winding down), CARPL.ai, deepc, Sectra |
| **PACS / VNA (Medical Imaging Archive)** <br><small>pacs-vna</small> | 4 | 3 | · | nvme-performance-storage (rack), capacity-archive-storage (cluster) | Agfa HealthCare (Agfa-Gevaert Group), FUJIFILM Healthcare Americas Corporation, GE HealthCare, INFINITT Healthcare, Intelerad Medical Systems (GE HealthCare), Merative (Merge Healthcare), Philips (Koninklijke Philips N.V.), Sectra, Visage Imaging (Pro Medicus) |
| **Advanced Visualization / 3D Image Post-Processing** <br><small>advanced-visualization-3d</small> | 3 | 2 | · | gpu-server (rack) | Canon Medical Systems (Canon Medical Informatics / Vital Images), Circle Cardiovascular Imaging (Circle CVI), GE HealthCare, Philips (Koninklijke Philips N.V.), Siemens Healthineers, TeraRecon (ConcertAI), Visage Imaging (Pro Medicus), Ziosoft |
| **OR Management & Surgical Video Platform** <br><small>or-surgical-video</small> | 3 | 2 | 2 | gpu-server (node), capacity-archive-storage (rack), edge-industrial (node) | Artisight, Caresyntax, KARL STORZ, Stryker |
| **Radiation Oncology — Treatment Planning (TPS) & Oncology Information System (OIS)** <br><small>radiation-oncology-tps-ois</small> | 3 | 1 | · | gpu-server (rack), high-availability-redundant (node) | Brainlab AG, Elekta AB, RaySearch Laboratories AB, Varian Medical Systems (a Siemens Healthineers company) |
| **Radiology & Cardiology Information Systems (RIS/CVIS)** <br><small>ris-cvis-workflow</small> | 3 | 2 | · | capacity-archive-storage (rack) | FUJIFILM Healthcare Americas Corporation, INFINITT Healthcare, Merative (Merge Healthcare), Philips (Koninklijke Philips N.V.), ScImage, Siemens Healthineers |
| **SaMD & Embedded Device Software Platform (OEM)** <br><small>samd-embedded-oem-platform</small> | 3 | · | 3 | gpu-server (rack), high-performance-computing-cpu (rack), edge-industrial (node) | BlackBerry QNX, Green Hills Software (INTEGRITY), NVIDIA Corporation (IGX / Holoscan), Wind River (Aptiv) |

### Genomics / Bioinformatics / Research AI  (`play-b`)
*Hardware anchor:* HPC nodes (CPU-dense), GPU training servers, NVMe scratch tiers + object storage
*Regulatory:* Mostly research-side; PHI if clinical genomics, GxP if GLP pipelines

| Category | Cust | Oper | OEM | What to quote (component · scale) | Co-sell / incumbent vendors |
|---|:--:|:--:|:--:|---|---|
| **AI Drug Discovery Platform** <br><small>ai-drug-discovery</small> | 4 | 4 | · | gpu-server (cluster), nvme-performance-storage (rack) | Cadence Design Systems, Inc. (OpenEye), Chemical Computing Group ULC, Cresset Group, NVIDIA Corporation (IGX / Holoscan), Schrodinger, Inc. |
| **Bioinformatics Secondary/Tertiary Analysis** <br><small>bioinformatics-secondary</small> | 4 | 3 | · | gpu-server (cluster), high-performance-computing-cpu (cluster), nvme-performance-storage (rack), capacity-archive-storage (cluster) | DNAnexus, Inc., Illumina, NVIDIA Corporation (IGX / Holoscan), QIAGEN Digital Insights, Sentieon Inc., Seqera Labs, S.L. |
| **Computational Chemistry / Molecular Modeling & Simulation** <br><small>comp-chem-simulation</small> | 4 | 3 | · | gpu-server (cluster), high-performance-computing-cpu (cluster), nvme-performance-storage (rack), high-memory (rack) | Cadence Design Systems, Inc. (OpenEye), Chemical Computing Group ULC, Cresset Group, Dassault Systemes SE (BIOVIA), Schrodinger, Inc. |
| **Structural Biology / Cryo-EM Image Processing** <br><small>cryo-em-structural-bio</small> | 4 | 2 | · | gpu-server (rack), nvme-performance-storage (rack), capacity-archive-storage (cluster), high-memory (node) | Gatan, Inc. (AMETEK), Structura Biotechnology Inc., Thermo Fisher Scientific Inc. |
| **AI / HPC Workload Orchestration & MLOps (cluster scheduling)** <br><small>ai-hpc-orchestration</small> | 3 | 3 | · | gpu-server (cluster), high-performance-computing-cpu (cluster) | Altair Engineering (Siemens), Hewlett Packard Enterprise Company, IBM Corporation, NVIDIA Corporation (IGX / Holoscan), Seqera Labs, S.L. |
| **RWD/RWE Analytics Platform** <br><small>rwd-rwe-analytics</small> | 2 | 3 | · | gpu-server (rack), capacity-archive-storage (cluster) | Aetion, Inc. (a Datavant company), IQVIA Holdings Inc., Komodo Health, Inc., Tempus AI, TriNetX, LLC, Truveta, Inc. |
| **NGS Wet-Lab LIMS (run & sample tracking)** <br><small>ngs-lab-lims</small> | 2 | 2 | · | — | Illumina, L7 Informatics, AgileBio (LabCollector), Ovation.io |
| **Clinical Genomics Interpretation & Reporting** <br><small>clinical-genomics-reporting</small> | 1 | 2 | · | — | Congenica (SeqOne Genomics), Fabric Genomics (GeneDx), Golden Helix, QIAGEN Digital Insights, SOPHiA GENETICS, Tempus AI |

### GMP Manufacturing Edge  (`play-c`)
*Hardware anchor:* Short-depth / industrial edge servers, Redundant tower/rack pairs, DR storage
*Regulatory:* GxP + Part 11 core. Documentation IS the product: controlled BOM, firmware/driver matrix, change notification, lifecycle statement, hardening guide

| Category | Cust | Oper | OEM | What to quote (component · scale) | Co-sell / incumbent vendors |
|---|:--:|:--:|:--:|---|---|
| **Automated Visual Inspection / Machine-Vision QC (deep learning)** <br><small>automated-visual-inspection</small> | 3 | · | 3 | gpu-server (node), edge-industrial (node) | Antares Vision Group S.p.A., Cognex Corporation, Keyence Corporation, Körber AG (Körber Pharma / Werum), OPTEL Group, Syntegon Technology GmbH |
| **MES / EBR (Manufacturing Execution)** <br><small>mes-ebr</small> | 3 | 1 | · | edge-industrial (node), high-availability-redundant (node), disaster-recovery-backup (node) | Emerson Electric Co., Körber AG (Körber Pharma / Werum), MasterControl Solutions, Inc., Rockwell Automation, Inc., Siemens AG (Smart Infrastructure / Digital Industries) |
| **PAT & Process Digital Twin (Process Development Analytics / Simulation)** <br><small>pat-process-twin</small> | 3 | · | · | gpu-server (rack), high-performance-computing-cpu (rack), edge-industrial (node) | AspenTech (Emerson), Bruker Corporation (Optimal Industrial Technologies), Sartorius AG, Siemens AG (Smart Infrastructure / Digital Industries) |
| **Plant Historian (Time-Series Data)** <br><small>plant-historian</small> | 3 | · | · | nvme-performance-storage (node), capacity-archive-storage (rack) | AspenTech (Emerson), AVEVA (Schneider Electric), Canary Labs, Inc., GE Vernova (Proficy) |
| **SCADA / DCS (Process Control)** <br><small>scada-dcs</small> | 3 | · | · | edge-industrial (node), high-availability-redundant (node) | AVEVA (Schneider Electric), Emerson Electric Co., Honeywell, Rockwell Automation, Inc., Siemens AG (Smart Infrastructure / Digital Industries), Yokogawa Electric Corporation |
| **QC Lab Informatics (LIMS / Chromatography Data)** <br><small>qc-lims-cds</small> | 2 | 1 | · | capacity-archive-storage (node), disaster-recovery-backup (node) | Agilent Technologies, Inc., LabVantage Solutions, Inc., LabWare, Inc., STARLIMS Corporation, Thermo Fisher Scientific Inc., Waters Corporation |
| **Serialization / Track-and-Trace (L4-L5)** <br><small>serialization-track-trace</small> | 2 | 2 | · | high-availability-redundant (node) | Antares Vision Group S.p.A., OPTEL Group, SAP SE, Systech International (a Dover company), TraceLink Inc. |
| **Warehouse & Cold-Chain Management (WMS / Environmental Monitoring)** <br><small>warehouse-cold-chain</small> | 2 | 1 | · | edge-industrial (node) | Blue Yonder Group, Inc., Ellab A/S, Körber AG (Körber Pharma / Werum), Manhattan Associates, Inc., SAP SE, Vaisala Oyj |

## 2 · Cross-play standalone deals (reachable-HOT, outside the three plays)

| Category | Cust | Oper | OEM | What to quote | Why it's outside the plays |
|---|:--:|:--:|:--:|---|---|
| **EHR/EMR Core System** <br><small>ehr-emr-core</small> | 4 | 4 | · | nvme-performance-storage (rack), high-availability-redundant (cluster), disaster-recovery-backup (rack) | General datacenter refresh / disaster-recovery deal (high-availability database + virtual desktops); not an imaging, genomics, or manufacturing-edge motion — pursue as a standalone infrastructure deal |
| **Clinical Decision Support & Clinical AI (CDSS)** <br><small>cdss-clinical-ai</small> | 2 | 3 | · | gpu-server (node) | Clinical inference graphics-processing-unit capacity attaches to the electronic-health-record estate or the vendor's inference fleet; not a play-A/B/C motion |
| **Clinical Data Warehouse / Health Data Lakehouse** <br><small>clinical-data-lakehouse</small> | 3 | · | · | gpu-server (node), high-performance-computing-cpu (rack), nvme-performance-storage (rack), capacity-archive-storage (rack) | Cross-cutting clinical data warehouse / lakehouse — a standalone data-platform infrastructure deal (object + fast-analytics tier + growing clinical-note NLP GPU), not the sequencing/research-AI motion of Play B |
| **Health Information Management & Coding** <br><small>him-coding</small> | 2 | 3 | · | gpu-server (rack), capacity-archive-storage (rack) | Operator-side coding natural-language-processing plus the customer-side scanned-chart archive refresh (7-15 year retention); attaches to the revenue-cycle / electronic-health-record estate rather than a play motion |
| **Hospital ERP (Finance / Supply Chain / HR)** <br><small>hospital-erp</small> | 3 | · | · | nvme-performance-storage (rack), high-availability-redundant (rack), disaster-recovery-backup (node) | Back-office transactional high-availability cluster; standalone infrastructure refresh deal |
| **ICU Central Monitoring & Clinical Surveillance** <br><small>icu-central-monitoring</small> | 2 | · | 3 | nvme-performance-storage (node), edge-industrial (node), high-availability-redundant (node) | Device-maker (original-equipment-manufacturer) channel deal for regulator-cleared central stations; outside the three solution plays |
| **Laboratory Information System (LIS)** <br><small>lis</small> | 3 | 3 | · | nvme-performance-storage (node), high-availability-redundant (rack), disaster-recovery-backup (node) | Clinical laboratory transactional high-availability / disaster-recovery footprint; standalone infrastructure deal |
| **Medical Device Integration & Alarm Management** <br><small>medical-device-integration</small> | 3 | 1 | · | nvme-performance-storage (rack), edge-industrial (node), high-availability-redundant (node) | Hospital integration-engine high-availability pairs; standalone clinical-information-technology infrastructure deal |
| **Payer Core Administration (Claims Adjudication)** <br><small>payer-core-admin</small> | 3 | 3 | · | nvme-performance-storage (rack), high-availability-redundant (rack), disaster-recovery-backup (rack) | Payer claims core; payer segment sits outside the three provider/pharma plays |
| **Payer Care/Utilization Management & Fraud Analytics** <br><small>payer-um-fraud-analytics</small> | 3 | 2 | · | high-performance-computing-cpu (rack) | Payer analytics; payer segment sits outside the three provider/pharma plays |
| **Smart-Room Ambient Sensing & Clinical Video AI** <br><small>smart-room-ambient-ai</small> | 3 | 3 | 2 | gpu-server (rack), capacity-archive-storage (rack), edge-industrial (node) | Clinical video artificial intelligence adjacent to Play A but outside the fixed three-play scope; pursue as a standalone ward-video edge deal alongside the imaging estate |

## 3 · Master HOT lists

### HOT_customer (direct sale) — 26 categories (direct sale)
- **4** [B] `ai-drug-discovery` — AI Drug Discovery Platform
- **4** [B] `bioinformatics-secondary` — Bioinformatics Secondary/Tertiary Analysis
- **4** [B] `comp-chem-simulation` — Computational Chemistry / Molecular Modeling & Simulation
- **4** [B] `cryo-em-structural-bio` — Structural Biology / Cryo-EM Image Processing
- **4** [A] `digital-pathology` — Digital Pathology Platform (WSI workflow + AI-assisted diagnosis)
- **4** [cross-play] `ehr-emr-core` — EHR/EMR Core System
- **4** [A] `imaging-ai-deployment` — Imaging AI Deployment Platform (Inference Orchestration / Marketplace)
- **4** [A] `pacs-vna` — PACS / VNA (Medical Imaging Archive)
- **3** [A] `advanced-visualization-3d` — Advanced Visualization / 3D Image Post-Processing
- **3** [B] `ai-hpc-orchestration` — AI / HPC Workload Orchestration & MLOps (cluster scheduling)
- **3** [C] `automated-visual-inspection` — Automated Visual Inspection / Machine-Vision QC (deep learning)
- **3** [cross-play] `clinical-data-lakehouse` — Clinical Data Warehouse / Health Data Lakehouse
- **3** [cross-play] `hospital-erp` — Hospital ERP (Finance / Supply Chain / HR)
- **3** [cross-play] `lis` — Laboratory Information System (LIS)
- **3** [cross-play] `medical-device-integration` — Medical Device Integration & Alarm Management
- **3** [C] `mes-ebr` — MES / EBR (Manufacturing Execution)
- **3** [A] `or-surgical-video` — OR Management & Surgical Video Platform
- **3** [C] `pat-process-twin` — PAT & Process Digital Twin (Process Development Analytics / Simulation)
- **3** [cross-play] `payer-core-admin` — Payer Core Administration (Claims Adjudication)
- **3** [cross-play] `payer-um-fraud-analytics` — Payer Care/Utilization Management & Fraud Analytics
- **3** [C] `plant-historian` — Plant Historian (Time-Series Data)
- **3** [A] `radiation-oncology-tps-ois` — Radiation Oncology — Treatment Planning (TPS) & Oncology Information System (OIS)
- **3** [A] `ris-cvis-workflow` — Radiology & Cardiology Information Systems (RIS/CVIS)
- **3** [A] `samd-embedded-oem-platform` — SaMD & Embedded Device Software Platform (OEM)
- **3** [C] `scada-dcs` — SCADA / DCS (Process Control)
- **3** [cross-play] `smart-room-ambient-ai` — Smart-Room Ambient Sensing & Clinical Video AI

### HOT_operator (ISV co-sell) — 14 categories (ISV / service-provider co-sell)
- **4** [B] `ai-drug-discovery` — AI Drug Discovery Platform
- **4** [cross-play] `ehr-emr-core` — EHR/EMR Core System
- **4** [A] `imaging-ai-deployment` — Imaging AI Deployment Platform (Inference Orchestration / Marketplace)
- **3** [B] `ai-hpc-orchestration` — AI / HPC Workload Orchestration & MLOps (cluster scheduling)
- **3** [B] `bioinformatics-secondary` — Bioinformatics Secondary/Tertiary Analysis
- **3** [cross-play] `cdss-clinical-ai` — Clinical Decision Support & Clinical AI (CDSS)
- **3** [B] `comp-chem-simulation` — Computational Chemistry / Molecular Modeling & Simulation
- **3** [A] `digital-pathology` — Digital Pathology Platform (WSI workflow + AI-assisted diagnosis)
- **3** [cross-play] `him-coding` — Health Information Management & Coding
- **3** [cross-play] `lis` — Laboratory Information System (LIS)
- **3** [A] `pacs-vna` — PACS / VNA (Medical Imaging Archive)
- **3** [cross-play] `payer-core-admin` — Payer Core Administration (Claims Adjudication)
- **3** [B] `rwd-rwe-analytics` — RWD/RWE Analytics Platform
- **3** [cross-play] `smart-room-ambient-ai` — Smart-Room Ambient Sensing & Clinical Video AI

### OEM design-wins — 8 categories (OEM design-win)
- **3** `automated-visual-inspection` — Automated Visual Inspection / Machine-Vision QC (deep learning)
- **3** `icu-central-monitoring` — ICU Central Monitoring & Clinical Surveillance
- **3** `samd-embedded-oem-platform` — SaMD & Embedded Device Software Platform (OEM)
- **2** `digital-pathology` — Digital Pathology Platform (WSI workflow + AI-assisted diagnosis)
- **2** `lab-middleware-automation` — Lab Middleware & Automation Orchestration
- **2** `or-surgical-video` — OR Management & Surgical Video Platform
- **2** `pharmacy-automation` — Pharmacy Automation & Medication Management
- **2** `smart-room-ambient-ai` — Smart-Room Ambient Sensing & Clinical Video AI

## 4 · Trigger → action index

| Signal | Urgency | Window | Opens (categories) | Play | Action |
|---|---|---|---|:--:|---|
| **New sequencer purchase** | critical | 90-day hardware window post-purchase | `bioinformatics-secondary` | B | Immediate outreach — sequencer needs compute+storage behind it (Play B) |
| **Cyber incident / ransomware** | critical | 0-6 months post-incident (budget unlocked) | `ehr-emr-core`, `pacs-vna`, `hospital-erp` | — | DR/backup/rebuild conversation — air-gapped backup, immutable storage angle |
| **New EHR go-live** | high | 6-18 months before go-live (infra buy happens early) | `ehr-emr-core`, `medical-device-integration` | — | Map infra operator; approach Infrastructure Owner re: compute/storage/VDI refresh |
| **FDA NDA/BLA approval** | high | 0-6 months post-approval (commercial scale-up) | `mes-ebr`, `scada-dcs`, `serialization-track-trace`, `plant-historian` | C | Manufacturing scale-up imminent — enter via Play C (MES/plant infra) |
| **Cloud repatriation signals** | high | Budget cycle following the statement | `ai-hpc-orchestration`, `bioinformatics-secondary`, `clinical-data-lakehouse`, `ehr-emr-core`, `pacs-vna` | A,B | TCO conversation with Infrastructure Owner + Economic Buyer |
| **Pharma AI-strategy announcement** | high | 3-12 months post-announcement | `ai-drug-discovery`, `ai-hpc-orchestration`, `comp-chem-simulation` | B | Probe: cloud or on-prem? If on-prem/hybrid → Play B GPU cluster pitch |
| **Plant modernization or new plant** | high | 12-24 months before validation | `mes-ebr`, `scada-dcs`, `plant-historian`, `automated-visual-inspection` | C | Play C entry — automation SI mapping, MES vendor identification |
| **FDA IND filing** | medium | 0-12 months post-filing | `ai-drug-discovery`, `bioinformatics-secondary` | B | Flag account; R&D compute demand rising — probe genomics/AI workloads (Play B) |
| **Hospital M&A / consolidation** | medium | 12-24 months (IT consolidation follows close) | `pacs-vna`, `ehr-emr-core`, `clinical-data-lakehouse` | A | Consolidated datacenter/imaging archive opportunity; find surviving IT org |
| **New hospital campus / expansion** | medium | 12-36 months before opening | `ehr-emr-core`, `pacs-vna`, `medical-device-integration` | A | New datacenter/edge closets get spec'd early — reach facility IT planning |
| **Serialization / traceability mandate** | medium | Mandate deadline minus 12-18 months | `serialization-track-trace`, `mes-ebr` | C | Serialization = plant-edge servers per line; bundle with Play C |
| **Cloud cost pressure** | medium | Budget planning season | `ai-hpc-orchestration`, `clinical-data-lakehouse`, `ehr-emr-core` | B | Soft version of repatriation — plant TCO seed, nurture |
| **HPC / bioinformatics job postings** | low | Rolling | `bioinformatics-secondary`, `ai-hpc-orchestration` | B | Evidence C only — never 'confirmed installed base'. Add to monitor list, seek corroboration |
| **KLAS / HIMSS rankings movement** | low | Annual cycles | `ehr-emr-core` | — | EMRAM stage jump = infra investment underway; qualify operator |

## 5 · Component pipelines (which categories feed each SMCI product line)

- **gpu-server** — 20 categories, 15 customer-HOT: `ai-drug-discovery`, `bioinformatics-secondary`, `comp-chem-simulation`, `cryo-em-structural-bio`, `digital-pathology`, `imaging-ai-deployment`, `advanced-visualization-3d`, `ai-hpc-orchestration` …
- **high-performance-computing-cpu** — 8 categories, 7 customer-HOT: `bioinformatics-secondary`, `comp-chem-simulation`, `ai-hpc-orchestration`, `clinical-data-lakehouse`, `pat-process-twin`, `payer-um-fraud-analytics`, `samd-embedded-oem-platform`, `population-health-analytics`
- **nvme-performance-storage** — 15 categories, 13 customer-HOT: `ai-drug-discovery`, `bioinformatics-secondary`, `comp-chem-simulation`, `cryo-em-structural-bio`, `digital-pathology`, `ehr-emr-core`, `pacs-vna`, `clinical-data-lakehouse` …
- **capacity-archive-storage** — 16 categories, 9 customer-HOT: `bioinformatics-secondary`, `cryo-em-structural-bio`, `digital-pathology`, `pacs-vna`, `clinical-data-lakehouse`, `or-surgical-video`, `plant-historian`, `ris-cvis-workflow` …
- **high-memory** — 2 categories, 2 customer-HOT: `comp-chem-simulation`, `cryo-em-structural-bio`
- **edge-industrial** — 16 categories, 9 customer-HOT: `imaging-ai-deployment`, `automated-visual-inspection`, `medical-device-integration`, `mes-ebr`, `or-surgical-video`, `pat-process-twin`, `samd-embedded-oem-platform`, `scada-dcs` …
- **high-availability-redundant** — 16 categories, 9 customer-HOT: `ehr-emr-core`, `imaging-ai-deployment`, `hospital-erp`, `lis`, `medical-device-integration`, `mes-ebr`, `payer-core-admin`, `radiation-oncology-tps-ois` …
- **disaster-recovery-backup** — 9 categories, 5 customer-HOT: `ehr-emr-core`, `hospital-erp`, `lis`, `mes-ebr`, `payer-core-admin`, `hie-interoperability-engine`, `qc-lims-cds`, `rcm-billing-claims` …

