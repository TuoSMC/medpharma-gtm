# SMCI Medical / Pharma Hunting Guide

> Generated from `/data` (taxonomy v7, 59 categories, 309 vendors). Deterministic — do not edit by hand; regenerate with `python3 tools/hunting_guide.py`.
>
> **Gate question first (CLAUDE.md §3): who controls the infrastructure behind the software?** No answer → not in pipeline.

**Opportunity scale** 1 minimal · 2 modest · 3 significant · 4 flagship. **Sizing** node < rack < cluster. **Buyer motions**: customer = direct · operator = ISV/co-sell · OEM = design-win · hyperscaler = out of scope. *What to quote* is the category's aggregate hardware pull (per-buyer split lives in the taxonomy). Vendors marked ⊘ are co-sell-excluded per §5.4 (cloud-locked clinical SaaS).

## 1 · The three plays — ranked target maps

### Medical Imaging + Digital Pathology  (`play-a`)
*Hardware anchor:* GPU servers (inference-optimized), NVMe storage servers, High-density object/archive storage
*Regulatory:* PHI always; SaMD flag if AI algorithms deployed clinically

| Category | Cust | Oper | OEM | What to quote (component · scale) | Co-sell / incumbent vendors |
|---|:--:|:--:|:--:|---|---|
| **Digital Pathology Platform (WSI workflow + AI-assisted diagnosis)** <br><small>digital-pathology</small> | 4 | 3 | 2 | gpu-server (cluster), nvme-performance-storage (rack), capacity-archive-storage (cluster) | Aiforia Technologies, Deep Bio (DeepDx Prostate), Hamamatsu Photonics, Ibex Medical Analytics (Galen), Indica Labs, Leica Biosystems (Danaher), Mindpeak, Owkin (MSIntuit CRC), Paige (Tempus AI), PathAI, Philips (Koninklijke Philips N.V.), Proscia, Roche Diagnostics, Sectra, Visiopharm |
| **Imaging AI Deployment Platform (Inference Orchestration / Marketplace)** <br><small>imaging-ai-deployment</small> | 4 | 4 | · | gpu-server (cluster), edge-industrial (node), high-availability-redundant (rack) | Aidoc, Annalise.ai, Blackford Analysis (Bayer — imaging-AI platform business winding down), CARPL.ai, Cleerly, deepc, DeepHealth (RadNet), GE HealthCare, Gleamer, HeartFlow, Lunit, Nanox.AI (Zebra Medical Vision), Philips (Koninklijke Philips N.V.), Qure.ai, RapidAI, Riverain Technologies, Sectra, Siemens Healthineers, Viz.ai |
| **PACS / VNA (Medical Imaging Archive)** <br><small>pacs-vna</small> | 4 | 3 | · | nvme-performance-storage (rack), capacity-archive-storage (cluster) | Agfa HealthCare (Agfa-Gevaert Group), Change Healthcare / Enterprise Imaging (now Optum), Fujifilm (Synapse PACS / VNA), FUJIFILM Healthcare Americas Corporation, GE HealthCare, Acuo VNA (Hyland), INFINITT Healthcare, Intelerad Medical Systems (GE HealthCare), Merative (Merge Healthcare), Philips (Koninklijke Philips N.V.), Sectra, Visage Imaging (Pro Medicus) |
| **Advanced Visualization / 3D Image Post-Processing** <br><small>advanced-visualization-3d</small> | 3 | 2 | · | gpu-server (rack) | Canon Medical Systems (Canon Medical Informatics / Vital Images), Circle Cardiovascular Imaging (Circle CVI), GE HealthCare, Philips (Koninklijke Philips N.V.), Siemens Healthineers, TeraRecon (ConcertAI), Visage Imaging (Pro Medicus), Ziosoft |
| **OR Management & Surgical Video Platform** <br><small>or-surgical-video</small> | 3 | 2 | 2 | gpu-server (node), capacity-archive-storage (rack), edge-industrial (node) | Artisight, Brainlab AG, Caresyntax, KARL STORZ, Medtronic, Olympus Corporation, Stryker |
| **Radiation Oncology — Treatment Planning (TPS) & Oncology Information System (OIS)** <br><small>radiation-oncology-tps-ois</small> | 3 | 1 | · | gpu-server (rack), capacity-archive-storage (rack), high-availability-redundant (node) | Brainlab AG, Elekta AB, RaySearch Laboratories AB, Varian Medical Systems (a Siemens Healthineers company) |
| **Radiology & Cardiology Information Systems (RIS/CVIS)** <br><small>ris-cvis-workflow</small> | 3 | 2 | · | capacity-archive-storage (rack) | Epic Systems, FUJIFILM Healthcare Americas Corporation, INFINITT Healthcare, Merative (Merge Healthcare), Philips (Koninklijke Philips N.V.), ScImage, Siemens Healthineers |
| **Smart-Room Ambient Sensing & Clinical Video AI** <br><small>smart-room-ambient-ai</small> | 3 | 3 | 2 | gpu-server (rack), capacity-archive-storage (rack), edge-industrial (node) | Artisight, AvaSure, LookDeep Health, Stryker, VirtuSense Technologies |
| **Clinical Decision Support & Clinical AI (CDSS)** <br><small>cdss-clinical-ai</small> | 2 | 3 | · | gpu-server (node) | Abridge, Aidoc, Ambience Healthcare, Corti, DeepScribe, Microsoft (Nuance DAX Copilot) ⊘, Nabla, Suki, Wolters Kluwer Health (UpToDate) |
| **Health Information Management & Coding** <br><small>him-coding</small> | 2 | 3 | · | gpu-server (rack), capacity-archive-storage (rack) | Dolbey Systems, Inc., Optum, Inc. (UnitedHealth Group), Solventum Corporation (formerly 3M Health Information Systems), TruBridge, Inc. (formerly CPSI) |

### Genomics / Bioinformatics / Research AI  (`play-b`)
*Hardware anchor:* HPC nodes (CPU-dense), GPU training servers, NVMe scratch tiers + object storage
*Regulatory:* Mostly research-side; PHI if clinical genomics, GxP if GLP pipelines

| Category | Cust | Oper | OEM | What to quote (component · scale) | Co-sell / incumbent vendors |
|---|:--:|:--:|:--:|---|---|
| **AI Drug Discovery Platform** <br><small>ai-drug-discovery</small> | 4 | 4 | · | gpu-server (cluster), nvme-performance-storage (rack) | Absci (ABSI), BenevolentAI, Cadence Design Systems, Inc. (OpenEye), Chemical Computing Group ULC, Cresset Group, Genesis Therapeutics, Iambic Therapeutics, Insilico Medicine, Insitro, Isomorphic Labs, NVIDIA Corporation, Recursion Pharmaceuticals (RXRX), Schrödinger (SDGR), Schrodinger, Inc. |
| **Bioinformatics Secondary/Tertiary Analysis** <br><small>bioinformatics-secondary</small> | 4 | 3 | · | gpu-server (cluster), high-performance-computing-cpu (cluster), nvme-performance-storage (rack), capacity-archive-storage (cluster) | DNAnexus, Inc., Illumina, NVIDIA Corporation, QIAGEN Digital Insights, Sentieon Inc., Seqera Labs, S.L., Velsera |
| **Computational Chemistry / Molecular Modeling & Simulation** <br><small>comp-chem-simulation</small> | 4 | 3 | · | gpu-server (cluster), high-performance-computing-cpu (cluster), nvme-performance-storage (rack), high-memory (rack) | Cadence Design Systems, Inc. (OpenEye), Chemical Computing Group ULC, Cresset Group, Dassault Systemes SE (BIOVIA), Schrodinger, Inc. |
| **Structural Biology / Cryo-EM Image Processing** <br><small>cryo-em-structural-bio</small> | 4 | 2 | · | gpu-server (rack), nvme-performance-storage (rack), capacity-archive-storage (cluster), high-memory (node) | Gatan, Inc. (AMETEK), Structura Biotechnology Inc., Thermo Fisher Scientific Inc. |
| **Healthcare Foundation-Model / LLM Serving Platform** <br><small>healthcare-llm-serving</small> | 4 | 3 | · | gpu-server (cluster), high-memory (rack) | Aidoc, Google (MedLM / Med-PaLM on Vertex AI), Hippocratic AI, John Snow Labs, Microsoft (Nuance Dragon / DAX Copilot), NVIDIA (NIM / BioNeMo), OpenEvidence |
| **AI / HPC Workload Orchestration & MLOps (cluster scheduling)** <br><small>ai-hpc-orchestration</small> | 3 | 3 | · | gpu-server (cluster), high-performance-computing-cpu (cluster) | Altair Engineering (Siemens), Hewlett Packard Enterprise Company, IBM Corporation, NVIDIA Corporation, Seqera Labs, S.L. |
| **Mass-Spectrometry Proteomics & Metabolomics Informatics** <br><small>ms-proteomics-metabolomics</small> | 3 | 2 | · | high-performance-computing-cpu (rack), high-memory (node), nvme-performance-storage (rack), capacity-archive-storage (rack) | Biognosys, Bruker Corporation (Optimal Industrial Technologies), Matrix Science, Nonlinear Dynamics (Waters Corporation), SCIEX (Danaher), Thermo Fisher Scientific Inc. |
| **Pharmacometrics & Clinical Pharmacology Modeling & Simulation** <br><small>pharmacometrics-modeling-simulation</small> | 3 | 2 | · | high-performance-computing-cpu (rack), high-memory (node) | Certara, ICON plc, Metrum Research Group, Open Systems Pharmacology (PK-Sim/MoBi, originated at Bayer), Simulations Plus |
| **Spatial Biology / Spatial-Omics Analysis** <br><small>spatial-biology-omics</small> | 3 | 2 | · | gpu-server (rack), nvme-performance-storage (rack), capacity-archive-storage (cluster) | 10x Genomics, Akoya Biosciences (a Quanterix company), Bruker Spatial Biology (NanoString / CosMx), Indica Labs, Vizgen |

### GMP Manufacturing Edge  (`play-c`)
*Hardware anchor:* Short-depth / industrial edge servers, Redundant tower/rack pairs, DR storage
*Regulatory:* GxP + Part 11 core. Documentation IS the product: controlled BOM, firmware/driver matrix, change notification, lifecycle statement, hardening guide

| Category | Cust | Oper | OEM | What to quote (component · scale) | Co-sell / incumbent vendors |
|---|:--:|:--:|:--:|---|---|
| **Automated Visual Inspection / Machine-Vision QC (deep learning)** <br><small>automated-visual-inspection</small> | 3 | · | 3 | gpu-server (node), edge-industrial (node) | Antares Vision Group S.p.A., Cognex Corporation, Keyence Corporation, Körber AG (Körber Pharma / Werum), OPTEL Group, Syntegon Technology GmbH |
| **MES / EBR (Manufacturing Execution)** <br><small>mes-ebr</small> | 3 | 1 | · | edge-industrial (node), high-availability-redundant (node), disaster-recovery-backup (node) | Critical Manufacturing (ASMPT), Emerson Electric Co., Körber AG (Körber Pharma / Werum), MasterControl Solutions, Inc., Rockwell Automation, Inc., Siemens AG (Smart Infrastructure / Digital Industries), Tulip Interfaces |
| **PAT & Process Digital Twin (Process Development Analytics / Simulation)** <br><small>pat-process-twin</small> | 3 | · | · | gpu-server (rack), high-performance-computing-cpu (rack), edge-industrial (node) | AspenTech (Emerson), Bruker Corporation (Optimal Industrial Technologies), Sartorius AG, Siemens AG (Smart Infrastructure / Digital Industries), Tulip Interfaces |
| **Plant Historian (Time-Series Data)** <br><small>plant-historian</small> | 3 | · | · | nvme-performance-storage (node), capacity-archive-storage (rack) | AspenTech (Emerson), AVEVA (Schneider Electric), Canary Labs, Inc., GE Vernova (Proficy) |
| **SCADA / DCS (Process Control)** <br><small>scada-dcs</small> | 3 | · | · | edge-industrial (node), high-availability-redundant (node) | ABB, AVEVA (Schneider Electric), Emerson Electric Co., Honeywell, Rockwell Automation, Inc., Siemens AG (Smart Infrastructure / Digital Industries), Yokogawa Electric Corporation |
| **QC Lab Informatics (LIMS / Chromatography Data)** <br><small>qc-lims-cds</small> | 2 | 1 | · | capacity-archive-storage (node), disaster-recovery-backup (node) | Agilent Technologies, Inc., LabVantage Solutions, Inc., LabWare, Inc., STARLIMS Corporation, Thermo Fisher Scientific Inc., Waters Corporation |
| **Serialization / Track-and-Trace (L4-L5)** <br><small>serialization-track-trace</small> | 2 | 2 | · | high-availability-redundant (node) | Antares Vision Group S.p.A., OPTEL Group, SAP SE, Systech International (a Dover company), TraceLink Inc. ⊘ |
| **Warehouse & Cold-Chain Management (WMS / Environmental Monitoring)** <br><small>warehouse-cold-chain</small> | 2 | 1 | · | edge-industrial (node) | Blue Yonder Group, Inc., Ellab A/S, Körber AG (Körber Pharma / Werum), Manhattan Associates, Inc., SAP SE, Vaisala Oyj |

## 2 · Cross-play standalone deals (reachable-HOT, outside the three plays)

| Category | Cust | Oper | OEM | What to quote | Why it's outside the plays |
|---|:--:|:--:|:--:|---|---|
| **Clinical Data Warehouse / Health Data Lakehouse** <br><small>clinical-data-lakehouse</small> | 3 | · | · | gpu-server (node), high-performance-computing-cpu (rack), nvme-performance-storage (rack), capacity-archive-storage (rack) | Cross-cutting clinical data warehouse / lakehouse — a standalone data-platform infrastructure deal (object + fast-analytics tier + growing clinical-note NLP GPU), not the sequencing/research-AI motion of Play B |
| **ICU Central Monitoring & Clinical Surveillance** <br><small>icu-central-monitoring</small> | 2 | · | 3 | nvme-performance-storage (node), edge-industrial (node), high-availability-redundant (node) | Device-maker (original-equipment-manufacturer) channel deal for regulator-cleared central stations; outside the three solution plays |
| **Payer Actuarial & Underwriting Risk Modeling** <br><small>payer-actuarial-hpc</small> | 3 | · | · | high-performance-computing-cpu (rack), high-memory (node) | Payer actuarial / underwriting compute grid; the payer segment sits outside the three provider/pharma solution plays |
| **Payer Care/Utilization Management & Fraud Analytics** <br><small>payer-um-fraud-analytics</small> | 3 | 2 | · | high-performance-computing-cpu (rack) | Payer analytics; payer segment sits outside the three provider/pharma plays |
| **RWD/RWE Analytics Platform** <br><small>rwd-rwe-analytics</small> | 2 | 3 | · | gpu-server (rack), capacity-archive-storage (cluster) | Operator-side real-world-data / claims analytics platform (warehouse + software-as-a-service); a data-platform co-sell, not the sequencing / research-AI motion of Play B |
| **SaMD & Embedded Device Software Platform (OEM)** <br><small>samd-embedded-oem-platform</small> | 3 | · | 3 | gpu-server (rack), high-performance-computing-cpu (rack), edge-industrial (node) | OEM embedded design-win — medtech / in-vitro-diagnostics device software; a per-unit board/edge bill-of-materials channel deal, not a hospital imaging/genomics/manufacturing play |

## 3 · Master HOT lists

### HOT_customer (direct sale) — 31 categories (direct sale)
- **4** [B] `ai-drug-discovery` — AI Drug Discovery Platform
- **4** [B] `bioinformatics-secondary` — Bioinformatics Secondary/Tertiary Analysis
- **4** [B] `comp-chem-simulation` — Computational Chemistry / Molecular Modeling & Simulation
- **4** [B] `cryo-em-structural-bio` — Structural Biology / Cryo-EM Image Processing
- **4** [A] `digital-pathology` — Digital Pathology Platform (WSI workflow + AI-assisted diagnosis)
- **4** [D] `ehr-emr-core` — EHR/EMR Core System
- **4** [B] `healthcare-llm-serving` — Healthcare Foundation-Model / LLM Serving Platform
- **4** [A] `imaging-ai-deployment` — Imaging AI Deployment Platform (Inference Orchestration / Marketplace)
- **4** [A] `pacs-vna` — PACS / VNA (Medical Imaging Archive)
- **3** [A] `advanced-visualization-3d` — Advanced Visualization / 3D Image Post-Processing
- **3** [B] `ai-hpc-orchestration` — AI / HPC Workload Orchestration & MLOps (cluster scheduling)
- **3** [C] `automated-visual-inspection` — Automated Visual Inspection / Machine-Vision QC (deep learning)
- **3** [cross-play] `clinical-data-lakehouse` — Clinical Data Warehouse / Health Data Lakehouse
- **3** [D] `hospital-erp` — Hospital ERP (Finance / Supply Chain / HR)
- **3** [D] `lis` — Laboratory Information System (LIS)
- **3** [D] `medical-device-integration` — Medical Device Integration & Alarm Management
- **3** [C] `mes-ebr` — MES / EBR (Manufacturing Execution)
- **3** [B] `ms-proteomics-metabolomics` — Mass-Spectrometry Proteomics & Metabolomics Informatics
- **3** [A] `or-surgical-video` — OR Management & Surgical Video Platform
- **3** [C] `pat-process-twin` — PAT & Process Digital Twin (Process Development Analytics / Simulation)
- **3** [cross-play] `payer-actuarial-hpc` — Payer Actuarial & Underwriting Risk Modeling
- **3** [D] `payer-core-admin` — Payer Core Administration (Claims Adjudication)
- **3** [cross-play] `payer-um-fraud-analytics` — Payer Care/Utilization Management & Fraud Analytics
- **3** [B] `pharmacometrics-modeling-simulation` — Pharmacometrics & Clinical Pharmacology Modeling & Simulation
- **3** [C] `plant-historian` — Plant Historian (Time-Series Data)
- **3** [A] `radiation-oncology-tps-ois` — Radiation Oncology — Treatment Planning (TPS) & Oncology Information System (OIS)
- **3** [A] `ris-cvis-workflow` — Radiology & Cardiology Information Systems (RIS/CVIS)
- **3** [cross-play] `samd-embedded-oem-platform` — SaMD & Embedded Device Software Platform (OEM)
- **3** [C] `scada-dcs` — SCADA / DCS (Process Control)
- **3** [A] `smart-room-ambient-ai` — Smart-Room Ambient Sensing & Clinical Video AI
- **3** [B] `spatial-biology-omics` — Spatial Biology / Spatial-Omics Analysis

### HOT_operator (ISV co-sell) — 15 categories (ISV / service-provider co-sell)
- **4** [B] `ai-drug-discovery` — AI Drug Discovery Platform
- **4** [D] `ehr-emr-core` — EHR/EMR Core System
- **4** [A] `imaging-ai-deployment` — Imaging AI Deployment Platform (Inference Orchestration / Marketplace)
- **3** [B] `ai-hpc-orchestration` — AI / HPC Workload Orchestration & MLOps (cluster scheduling)
- **3** [B] `bioinformatics-secondary` — Bioinformatics Secondary/Tertiary Analysis
- **3** [A] `cdss-clinical-ai` — Clinical Decision Support & Clinical AI (CDSS)
- **3** [B] `comp-chem-simulation` — Computational Chemistry / Molecular Modeling & Simulation
- **3** [A] `digital-pathology` — Digital Pathology Platform (WSI workflow + AI-assisted diagnosis)
- **3** [B] `healthcare-llm-serving` — Healthcare Foundation-Model / LLM Serving Platform
- **3** [A] `him-coding` — Health Information Management & Coding
- **3** [D] `lis` — Laboratory Information System (LIS)
- **3** [A] `pacs-vna` — PACS / VNA (Medical Imaging Archive)
- **3** [D] `payer-core-admin` — Payer Core Administration (Claims Adjudication)
- **3** [cross-play] `rwd-rwe-analytics` — RWD/RWE Analytics Platform
- **3** [A] `smart-room-ambient-ai` — Smart-Room Ambient Sensing & Clinical Video AI

### OEM design-wins — 3 categories (OEM design-win)
- **3** `automated-visual-inspection` — Automated Visual Inspection / Machine-Vision QC (deep learning)
- **3** `icu-central-monitoring` — ICU Central Monitoring & Clinical Surveillance
- **3** `samd-embedded-oem-platform` — SaMD & Embedded Device Software Platform (OEM)

## 4 · Trigger → action index

| Signal | Urgency | Window | Opens (category → play / standalone) | Action |
|---|---|---|---|---|
| **New sequencer purchase** | critical | 90-day hardware window post-purchase | `bioinformatics-secondary` (B), `ngs-lab-lims` (standalone) | Immediate outreach — sequencer needs compute+storage behind it (Play B) |
| **Cyber incident / ransomware** | critical | 0-6 months post-incident (budget unlocked) | `ehr-emr-core` (D), `pacs-vna` (A), `hospital-erp` (D), `scada-dcs` (C), `mes-ebr` (C), `plant-historian` (C), `lis` (D) | DR/backup/rebuild conversation — air-gapped backup, immutable storage angle |
| **New EHR go-live** | high | 6-18 months before go-live (infra buy happens early) | `ehr-emr-core` (D), `medical-device-integration` (D) | Map infra operator; approach Infrastructure Owner re: compute/storage/VDI refresh |
| **FDA NDA/BLA approval** | high | 0-6 months post-approval (commercial scale-up) | `mes-ebr` (C), `scada-dcs` (C), `serialization-track-trace` (C), `plant-historian` (C) | Manufacturing scale-up imminent — enter via Play C (MES/plant infra) |
| **Cloud repatriation signals** | high | Budget cycle following the statement | `ai-hpc-orchestration` (B), `bioinformatics-secondary` (B), `clinical-data-lakehouse` (standalone), `ehr-emr-core` (D), `pacs-vna` (A) | TCO conversation with Infrastructure Owner + Economic Buyer |
| **Pharma AI-strategy announcement** | high | 3-12 months post-announcement | `ai-drug-discovery` (B), `ai-hpc-orchestration` (B), `comp-chem-simulation` (B) | Probe: cloud or on-prem? If on-prem/hybrid → Play B GPU cluster pitch |
| **Plant modernization or new plant** | high | 12-24 months before validation | `mes-ebr` (C), `scada-dcs` (C), `plant-historian` (C), `automated-visual-inspection` (C) | Play C entry — automation SI mapping, MES vendor identification |
| **FDA IND filing** | medium | 0-12 months post-filing | `ai-drug-discovery` (B), `bioinformatics-secondary` (B) | Flag account; R&D compute demand rising — probe genomics/AI workloads (Play B) |
| **Hospital M&A / consolidation** | medium | 12-24 months (IT consolidation follows close) | `pacs-vna` (A), `ehr-emr-core` (D), `clinical-data-lakehouse` (standalone) | Consolidated datacenter/imaging archive opportunity; find surviving IT org |
| **New hospital campus / expansion** | medium | 12-36 months before opening | `ehr-emr-core` (D), `pacs-vna` (A), `medical-device-integration` (D) | New datacenter/edge closets get spec'd early — reach facility IT planning |
| **Serialization / traceability mandate** | medium | Mandate deadline minus 12-18 months | `serialization-track-trace` (C), `mes-ebr` (C) | Serialization = plant-edge servers per line; bundle with Play C |
| **Cloud cost pressure** | medium | Budget planning season | `ai-hpc-orchestration` (B), `clinical-data-lakehouse` (standalone), `ehr-emr-core` (D) | Soft repatriation signal — total-cost-of-ownership conversation with Infrastructure Owner + Economic Buyer; nurture |
| **HPC / bioinformatics job postings** | low | Rolling | `bioinformatics-secondary` (B), `ai-hpc-orchestration` (B) | Evidence C only — never 'confirmed installed base'. Add to monitor list, seek corroboration |
| **KLAS / HIMSS rankings movement** | low | Annual cycles | `ehr-emr-core` (D) | EMRAM stage jump = infra investment underway; qualify operator |

## 5 · Component pipelines (which categories feed each SMCI product line)

- **gpu-server** — 22 categories, 17 customer-HOT: `ai-drug-discovery`, `bioinformatics-secondary`, `comp-chem-simulation`, `cryo-em-structural-bio`, `digital-pathology`, `healthcare-llm-serving`, `imaging-ai-deployment`, `advanced-visualization-3d` …
- **high-performance-computing-cpu** — 11 categories, 10 customer-HOT: `bioinformatics-secondary`, `comp-chem-simulation`, `ai-hpc-orchestration`, `clinical-data-lakehouse`, `ms-proteomics-metabolomics`, `pat-process-twin`, `payer-actuarial-hpc`, `payer-um-fraud-analytics` …
- **nvme-performance-storage** — 17 categories, 15 customer-HOT: `ai-drug-discovery`, `bioinformatics-secondary`, `comp-chem-simulation`, `cryo-em-structural-bio`, `digital-pathology`, `ehr-emr-core`, `pacs-vna`, `clinical-data-lakehouse` …
- **capacity-archive-storage** — 19 categories, 12 customer-HOT: `bioinformatics-secondary`, `cryo-em-structural-bio`, `digital-pathology`, `pacs-vna`, `clinical-data-lakehouse`, `ms-proteomics-metabolomics`, `or-surgical-video`, `plant-historian` …
- **high-memory** — 6 categories, 6 customer-HOT: `comp-chem-simulation`, `cryo-em-structural-bio`, `healthcare-llm-serving`, `ms-proteomics-metabolomics`, `payer-actuarial-hpc`, `pharmacometrics-modeling-simulation`
- **edge-industrial** — 17 categories, 9 customer-HOT: `imaging-ai-deployment`, `automated-visual-inspection`, `medical-device-integration`, `mes-ebr`, `or-surgical-video`, `pat-process-twin`, `samd-embedded-oem-platform`, `scada-dcs` …
- **high-availability-redundant** — 17 categories, 9 customer-HOT: `ehr-emr-core`, `imaging-ai-deployment`, `hospital-erp`, `lis`, `medical-device-integration`, `mes-ebr`, `payer-core-admin`, `radiation-oncology-tps-ois` …
- **disaster-recovery-backup** — 9 categories, 5 customer-HOT: `ehr-emr-core`, `hospital-erp`, `lis`, `mes-ebr`, `payer-core-admin`, `hie-interoperability-engine`, `qc-lims-cds`, `rcm-billing-claims` …

