#!/usr/bin/env python3
"""Chain-integrity test suite for the six-layer taxonomy chain.

    segment → software category → hardware_buyer → hardware_opportunity
            → hardware_profile → play

Test-driven refinement: these tests encode the TARGET state (decisions D1-D3 in
docs/refinement-plan.md). They are expected to FAIL (RED) until the refinement
waves land, then stay green as the permanent regression net.

Run: python3 -m pytest tools/tests/ -q   (or python3 tools/tests/test_chain_integrity.py)
"""
import re
import sys
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
TAX = yaml.safe_load(open(REPO / "data" / "taxonomy.yaml", encoding="utf-8"))
TRIGGERS = yaml.safe_load(open(REPO / "data" / "triggers.yaml", encoding="utf-8"))
SCORING = yaml.safe_load(open(REPO / "data" / "scoring.yaml", encoding="utf-8"))
PLAYS = yaml.safe_load(open(REPO / "data" / "plays.yaml", encoding="utf-8"))
CATS = TAX["categories"]
ENUMS = TAX["enums"]

# ---- D1: target enum vocabularies (lazy abbreviations expanded; GPU/CPU/NVMe
# stay as universally-recognized professional vocabulary, expanded in glossary) ----
TARGET_ENUMS = {
    "lifecycle": {"research", "preclinical", "clinical", "manufacturing", "commercial", "post-market"},
    "role": {"system-of-record", "workflow", "data-acquisition", "integration",
             "analytics-artificial-intelligence", "infrastructure-platform",
             "regulated-software-as-a-medical-device"},
    "data_modality": {"transactional", "images", "omics", "time-series", "documents",
                      "simulation", "artificial-intelligence-models", "real-world-data"},
    "deployment": {"on-premises", "private-cloud", "hybrid", "public-cloud",
                   "software-as-a-service", "vendor-managed", "edge"},
    "segments": {"hospital-health-system", "diagnostic-reference-laboratory",
                 "academic-medical-center", "medical-technology-in-vitro-diagnostics",
                 "biotechnology-pharmaceutical", "contract-research-organization",
                 "contract-development-manufacturing-organization", "payer"},
    "hardware_buyer": {"customer", "operator", "hyperscaler", "original-equipment-manufacturer"},
    "hardware_profile": {"gpu-server", "high-performance-computing-cpu", "nvme-performance-storage",
                         "capacity-archive-storage", "high-memory", "edge-industrial",
                         "high-availability-redundant", "disaster-recovery-backup"},
    "domain": {"hospital-clinical-core", "hospital-business-administration",
               "hospital-device-facility-operations", "diagnostics-laboratory",
               "pharmaceutical-research-clinical-development", "manufacturing-quality-supply-chain",
               "data-analytics-payer-platforms", "medical-technology-device-software"},
}
FORBIDDEN_ABBREVIATED_VALUES = {
    # old value -> replacement (kept here as documentation of the wave-1 rename)
    "cro", "cdmo", "medtech-ivd", "biotech-pharma", "diagnostic-reference-lab",
    "RWD", "AI-models", "analytics-AI", "infra-platform", "regulated-SaMD",
    "on-prem", "SaaS", "managed", "public", "OEM", "oem", "hpc-cpu",
    "nvme-performance", "capacity-archive", "ha-redundant", "dr-backup",
}

REQUIRED_CATEGORY_FIELDS = [
    "id", "name_en", "name_zh", "name_full", "domain", "lifecycle", "role",
    "data_modality", "deployment", "segments", "hardware_opportunity",
    "hardware_buyer", "primary_buyer", "supermicro_reachable",
    "hardware_opportunity_by_buyer", "hardware_profile", "infrastructure_notes",
    "plays", "vendors", "evidence_note", "workload_envelope", "home_stakeholder",
]
HOME_STAKEHOLDERS = {"facility", "doctor", "nurse", "patient", "other"}

# ---- taxonomy v7: per-category workload_envelope (see .claude/skills/quantify-fields) ----
sys.path.insert(0, str(REPO / "tools"))
import workload_ceiling  # noqa: E402  the SINGLE source of truth for DERIVED bands

WORKLOAD_ENUMS = {
    "workload_gpu_role": {"none", "inference", "training", "mixed", "visualization"},
    "workload_capacity_band": {"none", "terabyte", "tens-of-terabytes",
                               "hundreds-of-terabytes", "petabyte-plus"},
    "workload_availability_class": {"best-effort", "standard", "high-availability",
                                    "mission-critical"},
    "workload_latency_class": {"batch", "interactive", "real-time", "deterministic-real-time"},
    "workload_data_growth": {"static", "low", "moderate", "high", "explosive"},
    "workload_io_pattern": {"light", "random-transactional", "sequential-throughput",
                            "high-throughput-parallel", "mixed"},
    "workload_concurrency": {"single", "low", "moderate", "high", "massive"},
    "workload_retention_horizon": {"transient", "short", "medium", "long", "permanent"},
}
WE_DERIVED = ("gpu_role", "capacity_band", "availability_class", "latency_class")
WE_JUDGMENT = ("data_growth", "io_pattern", "concurrency")
WE_SOURCED = ("retention_horizon", "per_unit_data_size")
WE_KEYS = ("scaling_driver",) + WE_DERIVED + WE_JUDGMENT + WE_SOURCED + ("sources", "notes")
WE_ENUM_OF = {  # envelope field -> which WORKLOAD_ENUMS key governs it
    "gpu_role": "workload_gpu_role", "capacity_band": "workload_capacity_band",
    "availability_class": "workload_availability_class", "latency_class": "workload_latency_class",
    "data_growth": "workload_data_growth", "io_pattern": "workload_io_pattern",
    "concurrency": "workload_concurrency", "retention_horizon": "workload_retention_horizon",
}
WE_CUT_KEYS = {"iops", "throughput", "total_capacity", "gpu_type_and_qty", "gpu_quantity",
               "accelerator_count_band", "rto_minutes", "rpo_minutes", "retention_years",
               "growth_pct_per_year", "data_ingested_per_day", "train_vs_inference_split",
               "ingest_rate_band", "compute_platform", "basis"}
WE_PLACEHOLDER_SOURCES = {"structural-inference", "TODO", "derived", "inference", "", "n/a"}
_DIGIT = re.compile(r"\d")
_STORAGE_COMPONENTS = {"nvme-performance-storage", "capacity-archive-storage"}

ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


class TestSchemaCompleteness(unittest.TestCase):
    def test_every_category_has_every_required_field(self):
        for c in CATS:
            missing = [f for f in REQUIRED_CATEGORY_FIELDS if f not in c]
            self.assertFalse(missing, f"{c.get('id','?')}: missing fields {missing}")

    def test_ids_unique_and_kebab(self):
        ids = [c["id"] for c in CATS]
        self.assertEqual(len(ids), len(set(ids)), "duplicate ids")
        for i in ids:
            self.assertRegex(i, ID_RE)

    def test_glossary_block_expands_every_acronym(self):
        """D1: taxonomy carries a glossary mapping every acronym-bearing enum value
        (including GPU/CPU/NVMe survivors and every category-id acronym) to full
        English + Traditional Chinese."""
        self.assertIn("glossary", TAX, "taxonomy.yaml needs a top-level glossary block")
        gl = TAX["glossary"]
        for needed in ["gpu-server", "high-performance-computing-cpu", "nvme-performance-storage"]:
            self.assertIn(needed, gl, f"glossary missing {needed}")
            self.assertIn("full_en", gl[needed])
            self.assertIn("full_zh", gl[needed])


class TestNoAbbreviations(unittest.TestCase):
    def test_enum_vocabularies_match_target(self):
        for key, want in TARGET_ENUMS.items():
            have = set(ENUMS.get(key, []))
            self.assertEqual(have, want, f"enums.{key}: {sorted(have ^ want)} differ")

    def test_no_forbidden_abbreviated_values_in_category_tags(self):
        for c in CATS:
            for field in ["lifecycle", "role", "data_modality", "deployment", "segments",
                          "hardware_buyer", "hardware_profile"]:
                vals = c.get(field) or []
                bad = [v for v in vals if v in FORBIDDEN_ABBREVIATED_VALUES]
                self.assertFalse(bad, f"{c['id']}.{field}: abbreviated values {bad}")
            pb = c.get("primary_buyer")
            self.assertNotIn(pb, FORBIDDEN_ABBREVIATED_VALUES, f"{c['id']}.primary_buyer: {pb}")

    def test_name_full_is_complete_and_distinct(self):
        """D1: name_full carries the fully-written-out name (no bare acronym tokens)."""
        acro = re.compile(r"\b(PACS|VNA|MES|EBR|LIS|LIMS|RIS|CVIS|EHR|EMR|CDSS|NGS|SaMD|RWD|RCM|HIM|ERP|BMS|CMMS|RTLS|TPS|OIS|SCADA|DCS|QC|CDS|PAT|HIE|OR|ICU|HPC|AI)\b")
        for c in CATS:
            nf = c.get("name_full")
            self.assertTrue(nf, f"{c['id']}: name_full missing/empty")
            m = acro.search(nf or "")
            self.assertIsNone(m, f"{c['id']}.name_full contains bare acronym '{m.group(0) if m else ''}' — write it out")


class TestDomainClassification(unittest.TestCase):
    def test_every_category_has_domain_from_closed_enum(self):
        for c in CATS:
            self.assertIn("domain", c, f"{c['id']}: no domain")
            self.assertIn(c["domain"], TARGET_ENUMS["domain"], f"{c['id']}: domain '{c.get('domain')}' not in enum")

    def test_domains_all_used(self):
        used = {c.get("domain") for c in CATS}
        self.assertTrue(TARGET_ENUMS["domain"] <= used, f"unused domains: {TARGET_ENUMS['domain'] - used}")

    def test_home_stakeholder_from_enum(self):
        """Home page groups on home_stakeholder (facility/doctor/nurse/patient/other)."""
        self.assertEqual(set(ENUMS.get("home_stakeholder", [])), HOME_STAKEHOLDERS)
        for c in CATS:
            self.assertIn(c.get("home_stakeholder"), HOME_STAKEHOLDERS,
                          f"{c['id']}: home_stakeholder '{c.get('home_stakeholder')}' not in enum")


class TestBuyerLayer(unittest.TestCase):
    def test_primary_buyer_in_buyer_set(self):
        for c in CATS:
            self.assertIn(c["primary_buyer"], c["hardware_buyer"], c["id"])

    def test_reachability_consistent(self):
        for c in CATS:
            reach = any(b != "hyperscaler" for b in c["hardware_buyer"])
            self.assertEqual(c["supermicro_reachable"], reach, c["id"])


class TestOpportunityLayer(unittest.TestCase):
    def test_per_buyer_keys_match_non_hyperscaler_buyers(self):
        for c in CATS:
            want = {b for b in c["hardware_buyer"] if b != "hyperscaler"}
            self.assertEqual(set(c["hardware_opportunity_by_buyer"]), want, c["id"])

    def test_scores_in_range(self):
        for c in CATS:
            self.assertIn(c["hardware_opportunity"], (1, 2, 3, 4), c["id"])
            for b, v in c["hardware_opportunity_by_buyer"].items():
                self.assertIn(v, (1, 2, 3, 4), f"{c['id']}.{b}")

    def test_headline_equals_max_per_buyer(self):
        """D2: headline rollup must equal the max per-buyer opportunity."""
        for c in CATS:
            mx = max(c["hardware_opportunity_by_buyer"].values())
            self.assertEqual(c["hardware_opportunity"], mx,
                             f"{c['id']}: headline {c['hardware_opportunity']} != max per-buyer {mx}")


class TestProfileLayer(unittest.TestCase):
    def test_profile_subset_of_enum(self):
        for c in CATS:
            bad = [h for h in c["hardware_profile"] if h not in TARGET_ENUMS["hardware_profile"]]
            self.assertFalse(bad, f"{c['id']}: {bad}")

    def test_flagship_categories_have_components(self):
        for c in CATS:
            if c["hardware_opportunity"] == 4:
                self.assertTrue(c["hardware_profile"], f"{c['id']}: flagship but empty hardware_profile")


class TestPlayLayer(unittest.TestCase):
    def test_plays_valid(self):
        valid = {p["id"] for p in PLAYS["plays"]}
        for c in CATS:
            for p in c["plays"]:
                self.assertIn(p, valid, c["id"])


class TestTriggersClassified(unittest.TestCase):
    def test_trigger_categories_closed_enum(self):
        """D3-adjacent: triggers.yaml declares its category enum; every trigger uses it."""
        self.assertIn("enums", TRIGGERS, "triggers.yaml needs an enums block declaring category + urgency")
        cat_enum = set(TRIGGERS["enums"]["category"])
        urg_enum = set(TRIGGERS["enums"]["urgency"])
        for t in TRIGGERS["triggers"]:
            self.assertIn(t["category"], cat_enum, t["id"])
            self.assertIn(t["urgency"], urg_enum, t["id"])




# ============================================================
# v2 invariants — added after codex + grok dual review
# ============================================================
import subprocess

APPROVED_IDS = {
    "pacs-vna", "bioinformatics-secondary", "mes-ebr", "ehr-emr-core", "cdss-clinical-ai",
    "ris-cvis-workflow", "or-surgical-video", "icu-central-monitoring", "telehealth-platform",
    "radiation-oncology-tps-ois", "advanced-visualization-3d", "patient-portal-engagement",
    "patient-access-scheduling", "rcm-billing-claims", "him-coding", "hospital-erp",
    "workforce-management", "medical-device-integration", "rtls-asset-tracking", "healthcare-cmms",
    "pharmacy-automation", "medical-iot-security", "hospital-bms", "capacity-command-center",
    "smart-room-ambient-ai", "lis", "lab-middleware-automation", "digital-pathology",
    "ngs-lab-lims", "clinical-genomics-reporting", "rd-lab-informatics", "comp-chem-simulation",
    "ai-drug-discovery", "cryo-em-structural-bio", "clinical-trial-suite", "pv-regulatory-information",
    "scada-dcs", "plant-historian", "qc-lims-cds", "eqms-calibration", "serialization-track-trace",
    "warehouse-cold-chain", "pat-process-twin", "automated-visual-inspection", "clinical-data-lakehouse",
    "population-health-analytics", "rwd-rwe-analytics", "hie-interoperability-engine",
    "imaging-ai-deployment", "payer-core-admin", "payer-um-fraud-analytics",
    "samd-embedded-oem-platform", "ai-hpc-orchestration",
    "pharmacometrics-modeling-simulation", "ms-proteomics-metabolomics",
    "spatial-biology-omics", "healthcare-llm-serving", "payer-actuarial-hpc",
    "clinical-communication-collaboration",
}

APPROVED_DOMAIN = {
    "pacs-vna": "hospital-clinical-core", "bioinformatics-secondary": "pharmaceutical-research-clinical-development",
    "mes-ebr": "manufacturing-quality-supply-chain", "ehr-emr-core": "hospital-clinical-core",
    "cdss-clinical-ai": "hospital-clinical-core", "ris-cvis-workflow": "hospital-clinical-core",
    "or-surgical-video": "hospital-clinical-core", "icu-central-monitoring": "hospital-clinical-core",
    "telehealth-platform": "hospital-clinical-core", "radiation-oncology-tps-ois": "hospital-clinical-core",
    "advanced-visualization-3d": "hospital-clinical-core", "patient-portal-engagement": "hospital-business-administration",
    "patient-access-scheduling": "hospital-business-administration", "rcm-billing-claims": "hospital-business-administration",
    "him-coding": "hospital-business-administration", "hospital-erp": "hospital-business-administration",
    "workforce-management": "hospital-business-administration", "medical-device-integration": "hospital-device-facility-operations",
    "rtls-asset-tracking": "hospital-device-facility-operations", "healthcare-cmms": "hospital-device-facility-operations",
    "pharmacy-automation": "hospital-device-facility-operations", "medical-iot-security": "hospital-device-facility-operations",
    "hospital-bms": "hospital-device-facility-operations", "capacity-command-center": "hospital-device-facility-operations",
    "smart-room-ambient-ai": "hospital-device-facility-operations", "lis": "diagnostics-laboratory",
    "lab-middleware-automation": "diagnostics-laboratory", "digital-pathology": "diagnostics-laboratory",
    "ngs-lab-lims": "diagnostics-laboratory", "clinical-genomics-reporting": "diagnostics-laboratory",
    "rd-lab-informatics": "pharmaceutical-research-clinical-development", "comp-chem-simulation": "pharmaceutical-research-clinical-development",
    "ai-drug-discovery": "pharmaceutical-research-clinical-development", "cryo-em-structural-bio": "pharmaceutical-research-clinical-development",
    "clinical-trial-suite": "pharmaceutical-research-clinical-development", "pv-regulatory-information": "pharmaceutical-research-clinical-development",
    "scada-dcs": "manufacturing-quality-supply-chain", "plant-historian": "manufacturing-quality-supply-chain",
    "qc-lims-cds": "manufacturing-quality-supply-chain", "eqms-calibration": "manufacturing-quality-supply-chain",
    "serialization-track-trace": "manufacturing-quality-supply-chain", "warehouse-cold-chain": "manufacturing-quality-supply-chain",
    "pat-process-twin": "manufacturing-quality-supply-chain", "automated-visual-inspection": "manufacturing-quality-supply-chain",
    "clinical-data-lakehouse": "data-analytics-payer-platforms", "population-health-analytics": "data-analytics-payer-platforms",
    "rwd-rwe-analytics": "data-analytics-payer-platforms", "hie-interoperability-engine": "data-analytics-payer-platforms",
    "imaging-ai-deployment": "hospital-clinical-core", "payer-core-admin": "data-analytics-payer-platforms",
    "payer-um-fraud-analytics": "data-analytics-payer-platforms", "samd-embedded-oem-platform": "medical-technology-device-software",
    "ai-hpc-orchestration": "pharmaceutical-research-clinical-development",
    "pharmacometrics-modeling-simulation": "pharmaceutical-research-clinical-development",
    "ms-proteomics-metabolomics": "pharmaceutical-research-clinical-development",
    "spatial-biology-omics": "pharmaceutical-research-clinical-development",
    "healthcare-llm-serving": "data-analytics-payer-platforms",
    "payer-actuarial-hpc": "data-analytics-payer-platforms",
    "clinical-communication-collaboration": "hospital-device-facility-operations",
}

REQUIRED_GLOSSARY_KEYS = {
    "gpu-server", "high-performance-computing-cpu", "nvme-performance-storage",
    "pacs", "vna", "ehr", "emr", "cdss", "ris", "cvis", "or", "icu", "tps", "ois",
    "rcm", "him", "erp", "hr", "rtls", "cmms", "iomt", "ot", "bms", "lis", "lims",
    "ngs", "eln", "edc", "ctms", "etmf", "rtsm", "pv", "scada", "dcs", "qc", "cds",
    "eqms", "wms", "pat", "gxp", "hie", "rwd", "rwe", "samd", "oem", "mlops", "hpc",
    "ai", "cryo-em",
}

TRIGGER_CATEGORIES = {
    "clinical-information-technology", "genomics", "hospital-corporate-activity",
    "hospital-facility-expansion", "infrastructure-strategy", "pharmaceutical-manufacturing",
    "pharmaceutical-research-development", "regulatory-mandate", "security-incident", "talent-signal",
}
CLOUD_SUBSTRATE = {"public-cloud", "software-as-a-service", "hybrid", "vendor-managed"}


class TestInventoryLocked(unittest.TestCase):
    def test_exactly_53_categories_with_approved_ids(self):
        ids = {c["id"] for c in CATS}
        self.assertEqual(len(CATS), 59)
        self.assertEqual(ids, APPROVED_IDS)

    def test_domain_fixture_locked(self):
        for c in CATS:
            self.assertEqual(c["domain"], APPROVED_DOMAIN[c["id"]],
                             f"{c['id']}: domain moved without updating the approved fixture")


class TestTagsAgainstDeclaredEnums(unittest.TestCase):
    def test_every_tag_value_is_member_of_declared_enum(self):
        for c in CATS:
            for field, enum_key in [("lifecycle", "lifecycle"), ("role", "role"),
                                    ("data_modality", "data_modality"), ("deployment", "deployment"),
                                    ("segments", "segments"), ("hardware_buyer", "hardware_buyer"),
                                    ("hardware_profile", "hardware_profile")]:
                declared = set(ENUMS[enum_key])
                for v in c[field]:
                    self.assertIn(v, declared, f"{c['id']}.{field}: '{v}' not in declared enum")
            self.assertIn(c["primary_buyer"], set(ENUMS["hardware_buyer"]), c["id"])
            self.assertIn(c["domain"], set(ENUMS["domain"]), c["id"])


class TestBuyerCoherence(unittest.TestCase):
    def test_primary_buyer_is_among_argmax(self):
        for c in CATS:
            obb = c["hardware_opportunity_by_buyer"]
            mx = max(obb.values())
            argmax = {b for b, v in obb.items() if v == mx}
            self.assertIn(c["primary_buyer"], argmax,
                          f"{c['id']}: primary_buyer {c['primary_buyer']} not among max-opportunity buyers {argmax}")

    def test_hyperscaler_buyer_implies_cloud_substrate(self):
        for c in CATS:
            if "hyperscaler" in c["hardware_buyer"]:
                self.assertTrue(set(c["deployment"]) & CLOUD_SUBSTRATE,
                                f"{c['id']}: hyperscaler buyer but no cloud substrate in deployment")

    def test_oem_buyer_has_edge_substrate_or_embedded_notes(self):
        for c in CATS:
            if "original-equipment-manufacturer" in c["hardware_buyer"]:
                ok = ("edge" in c["deployment"]) or any(
                    k in c["infrastructure_notes"].lower()
                    for k in ("embedded", "scanner", "bill-of-materials", "device maker", "appliance"))
                self.assertTrue(ok, f"{c['id']}: oem buyer without edge substrate or embedded-path notes")


class TestGlossaryCoverage(unittest.TestCase):
    def test_all_required_keys_present_with_both_languages(self):
        gl = TAX["glossary"]
        missing = REQUIRED_GLOSSARY_KEYS - set(gl)
        self.assertFalse(missing, f"glossary missing: {sorted(missing)}")
        for k in REQUIRED_GLOSSARY_KEYS:
            self.assertTrue(gl[k].get("full_en"), k)
            self.assertTrue(gl[k].get("full_zh"), k)

    def test_full_zh_contains_no_latin(self):
        for k, v in TAX["glossary"].items():
            self.assertFalse(re.search(r"[A-Za-z]", v["full_zh"]),
                             f"glossary.{k}.full_zh contains Latin characters: {v['full_zh']}")


class TestTriggersLocked(unittest.TestCase):
    def test_fixed_vocabulary_and_required_fields(self):
        self.assertEqual(set(TRIGGERS["enums"]["category"]), TRIGGER_CATEGORIES)
        ids = [t["id"] for t in TRIGGERS["triggers"]]
        self.assertEqual(len(ids), len(set(ids)), "duplicate trigger ids")
        for t in TRIGGERS["triggers"]:
            for f in ("id", "signal", "category", "urgency", "window", "source", "action"):
                self.assertIn(f, t, f"trigger {t.get('id','?')} missing {f}")
            self.assertIn(t["category"], TRIGGER_CATEGORIES, t["id"])


class TestToolsSmoke(unittest.TestCase):
    def _run(self, *args):
        r = subprocess.run([sys.executable, *args], capture_output=True, text=True,
                           cwd=str(REPO), timeout=60)
        blob = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0, f"{args}: exit {r.returncode}\n{blob[-800:]}")
        for bad in ("Traceback", "KeyError"):
            self.assertNotIn(bad, blob, f"{args}: {bad} in output")
        return r.stdout

    def test_rollup_runs_clean(self):
        out = self._run("tools/rollup.py")
        self.assertIn("OEM design-wins", out)
        self.assertNotIn("oem?", out)

    def test_drilldown_runs_clean(self):
        out = self._run("tools/drilldown.py", "--axis", "component")
        self.assertIn("gpu-server", out)

    def test_drilldown_workload_axis(self):
        """v7: --axis workload slices reachable categories by envelope bands
        (reads stored envelope values — never recomputes; INV-14 owns derivation)."""
        out = self._run("tools/drilldown.py", "--axis", "workload")
        for lens in ("gpu_role", "capacity_band", "concurrency", "availability_class"):
            self.assertIn(lens, out, f"workload axis missing '{lens}' slice")
        self.assertIn("petabyte-plus", out)  # a real band value must appear

    def test_score_runs_clean(self):
        out = self._run("tools/score.py", "data/accounts/example-riverbend-pathology.yaml")
        self.assertIn("Tier:", out)

    def test_hunting_guide_runs_clean(self):
        out = self._run("tools/hunting_guide.py")
        self.assertIn("hunting-guide.md", out)
        md = (REPO / "docs" / "hunting-guide.md").read_text(encoding="utf-8")
        for play in ("Medical Imaging", "Genomics", "GMP Manufacturing"):
            self.assertIn(play, md, f"hunting guide missing play {play}")
        self.assertIn("Trigger", md)

    def test_glossary_md_generated_from_taxonomy(self):
        out = self._run("tools/glossary_md.py")
        self.assertIn("glossary.md", out)
        md = (REPO / "docs" / "glossary.md").read_text(encoding="utf-8")
        # every taxonomy glossary key must appear in the rendered doc
        for key in TAX["glossary"]:
            self.assertIn(f"`{key}`", md, f"glossary.md missing {key}")




# ============================================================
# Round-2 invariants: play-scope honesty + trigger foreign keys
# ============================================================

class TestPlayScopeHonesty(unittest.TestCase):
    def test_hot_categories_have_play_or_exemption(self):
        """A reachable-HOT category (any buyer opportunity >= 3) with no play must
        carry play_exemption explaining why it sits outside the 3-play scope —
        otherwise the pipeline silently carries unroutable deals."""
        for c in CATS:
            if c["supermicro_reachable"] and max(c["hardware_opportunity_by_buyer"].values()) >= 3 and not c["plays"]:
                self.assertTrue(c.get("play_exemption"),
                                f"{c['id']}: HOT with no play and no play_exemption")

    def test_exemption_only_where_meaningful(self):
        for c in CATS:
            if c.get("play_exemption"):
                self.assertFalse(c["plays"], f"{c['id']}: has both plays and play_exemption")

    def test_play_d_added_and_routes_the_flagship_orphan(self):
        """v3.4: Play D (Clinical Core Resilience) added after adversarial review. The
        taxonomy's only play-less flagship (EHR/EMR) — and the NVMe/HA/DR clinical/payer
        siblings — now route to it; the stripped GPU categories route to Play A."""
        play_ids = {p["id"] for p in PLAYS["plays"]}
        self.assertIn("play-d", play_ids, "Play D must exist in plays.yaml")
        self.assertNotIn("play-e", play_ids, "Play E was rejected (segment bucket, not a hardware anchor)")
        byid = {c["id"]: c for c in CATS}
        self.assertEqual(byid["ehr-emr-core"]["plays"], ["play-d"], "flagship EHR must route to Play D")
        for cid in ("lis", "hospital-erp", "medical-device-integration", "payer-core-admin"):
            self.assertIn("play-d", byid[cid]["plays"], f"{cid} (NVMe/HA/DR anchor) must be in Play D")
        for cid in ("cdss-clinical-ai", "smart-room-ambient-ai", "him-coding"):
            self.assertIn("play-a", byid[cid]["plays"], f"{cid} (GPU) must route to Play A, not the resilience play")
        # no flagship or customer-HOT category is left play-less any more (every high-value deal is routable)
        for c in CATS:
            hot = max(c["hardware_opportunity_by_buyer"].values()) >= 3
            if c["supermicro_reachable"] and hot:
                self.assertTrue(c["plays"] or c.get("play_exemption"),
                                f"{c['id']}: HOT deal with no play and no exemption")


class TestTriggerForeignKeys(unittest.TestCase):
    def test_triggers_bind_to_taxonomy_and_plays(self):
        cat_ids = {c["id"] for c in CATS}
        play_ids = {p["id"] for p in PLAYS["plays"]}
        for t in TRIGGERS["triggers"]:
            self.assertIn("related_categories", t, f"{t['id']}: no related_categories")
            self.assertIn("related_plays", t, f"{t['id']}: no related_plays")
            for cid in t["related_categories"]:
                self.assertIn(cid, cat_ids, f"{t['id']}: unknown category {cid}")
            for pid in t["related_plays"]:
                self.assertIn(pid, play_ids, f"{t['id']}: unknown play {pid}")

    def test_every_trigger_references_at_least_one_category(self):
        """codex: plays alone must not satisfy the binding — a trigger needs a
        concrete taxonomy category to route to."""
        for t in TRIGGERS["triggers"]:
            self.assertTrue(t.get("related_categories"),
                            f"{t['id']}: no related_categories — dead trigger")

    def test_related_plays_consistent_with_related_categories(self):
        """grok: every play a trigger routes to must be carried by at least one
        of its related categories (no play/category mismatch)."""
        by_id = {c["id"]: c for c in CATS}
        for t in TRIGGERS["triggers"]:
            play_union = set()
            for cid in t["related_categories"]:
                play_union |= set(by_id[cid]["plays"])
            for pid in t["related_plays"]:
                self.assertIn(pid, play_union,
                              f"{t['id']}: routes to {pid} but no related category carries it")




# ============================================================
# Round-3 invariants: vendors layer
# ============================================================
VENDORS_DOC = yaml.safe_load(open(REPO / "data" / "vendors.yaml", encoding="utf-8"))


class TestVendorsLayer(unittest.TestCase):
    def test_registry_schema(self):
        """Every vendors.yaml entry: id, name, deployment_models, confidence (A-D),
        source (citation URL or named public source). §8: never fabricate."""
        vendors = VENDORS_DOC["vendors"]
        self.assertTrue(vendors, "vendors registry is empty")
        ids = [v["id"] for v in vendors]
        self.assertEqual(len(ids), len(set(ids)), "duplicate vendor ids")
        for v in vendors:
            for f in ("id", "name", "deployment_models", "confidence", "source"):
                self.assertIn(f, v, f"vendor {v.get('id','?')} missing {f}")
            self.assertRegex(v["id"], ID_RE)
            self.assertIn(v["confidence"], ("A", "B", "C", "D"), v["id"])
            self.assertTrue(str(v["source"]).strip(), f"{v['id']}: empty source")
            for d in v["deployment_models"]:
                self.assertIn(d, TARGET_ENUMS["deployment"], f"{v['id']}: bad deployment {d}")

    def test_category_vendor_foreign_keys(self):
        vids = {v["id"] for v in VENDORS_DOC["vendors"]}
        for c in CATS:
            for vid in c["vendors"]:
                self.assertIn(vid, vids, f"{c['id']}: unknown vendor {vid}")

    def test_every_category_has_vendors(self):
        for c in CATS:
            self.assertGreaterEqual(len(c["vendors"]), 2,
                                    f"{c['id']}: fewer than 2 vendors")

    def test_every_vendor_referenced(self):
        used = set()
        for c in CATS:
            used |= set(c["vendors"])
        for v in VENDORS_DOC["vendors"]:
            self.assertIn(v["id"], used, f"vendor {v['id']} referenced by no category")




# ============================================================
# Round-4 invariants: per-component sizing
# ============================================================
SIZING_TIERS = {"node", "rack", "cluster"}


class TestComponentSizing(unittest.TestCase):
    def test_sizing_keys_match_hardware_profile(self):
        """Every component in hardware_profile carries a deployment-scale tier
        (node < rack < cluster) so a quote can be sized. Empty profile -> empty."""
        for c in CATS:
            sizing = c.get("hardware_profile_sizing", {})
            self.assertEqual(set(sizing), set(c["hardware_profile"]),
                             f"{c['id']}: sizing keys {set(sizing)} != profile {set(c['hardware_profile'])}")

    def test_sizing_tiers_valid(self):
        for c in CATS:
            for comp, tier in (c.get("hardware_profile_sizing") or {}).items():
                self.assertIn(tier, SIZING_TIERS, f"{c['id']}.{comp}: bad tier {tier}")

    def test_flagship_customer_has_a_large_tier(self):
        """A flagship customer deal (customer opportunity 4) must pull at least one
        rack- or cluster-scale component — otherwise the score is unsupported."""
        for c in CATS:
            if c["hardware_opportunity_by_buyer"].get("customer", 0) == 4:
                tiers = set((c.get("hardware_profile_sizing") or {}).values())
                self.assertTrue(tiers & {"rack", "cluster"},
                                f"{c['id']}: flagship customer but no rack/cluster-scale component")




# ============================================================
# Round-5 invariants: vendor enrichment (name/HQ/leadership/history/market)
# §8: every enrichment claim carries a source; unverifiable -> honest null.
# ============================================================
_VDOC = yaml.safe_load(open(REPO / "data" / "vendors.yaml", encoding="utf-8"))
ENRICH_FIELDS = ["headquarters", "founded", "leadership", "history", "market_position",
                 "market_share", "sources"]
UNKNOWN = {None, "", "unknown", "not publicly disclosed", "n/a", "not disclosed"}


class TestVendorEnrichment(unittest.TestCase):
    def test_every_vendor_has_enrichment_fields(self):
        for v in _VDOC["vendors"]:
            missing = [f for f in ENRICH_FIELDS if f not in v]
            self.assertFalse(missing, f"vendor {v['id']}: missing enrichment {missing}")

    def test_market_share_pct_is_numeric_and_sourced(self):
        """v3.5: the market-share bar reads market_share_pct. It must be a plausible
        number AND traceable — only present where the vendor carries market_share prose
        (its cited source). Never a bare, unsourced percentage."""
        n = 0
        for v in _VDOC["vendors"]:
            if "market_share_pct" in v and v["market_share_pct"] is not None:
                n += 1
                p = v["market_share_pct"]
                self.assertTrue(isinstance(p, (int, float)) and 0 < p <= 100,
                                f"{v['id']}: market_share_pct {p!r} not a 0-100 number")
                self.assertTrue(v.get("market_share"),
                                f"{v['id']}: has market_share_pct but no market_share prose to source it")
        self.assertGreaterEqual(n, 15, "expected the structured share numbers to be populated")
        byid = {v["id"]: v for v in _VDOC["vendors"]}
        self.assertEqual(byid["epic-systems"]["market_share_pct"], 42.3)
        self.assertEqual(byid["oracle-health"]["market_share_pct"], 22.9)
        self.assertEqual(byid["athenahealth"]["market_share_pct"], 7.5)  # researched + kept
        # adoption/reach and tech-tracker figures were REJECTED, not stamped as market share
        self.assertIsNone(byid.get("openevidence", {}).get("market_share_pct"))  # 65% = physician adoption
        self.assertIsNone(byid.get("greenway", {}).get("market_share_pct"))       # 6sense tech-tracker
        self.assertIsNone(byid.get("phreesia", {}).get("market_share_pct"))       # visits-enabled reach

    def test_partnerships_are_structured_and_sourced(self):
        """v3.7: researched partnerships give the co-sell / displacement map. Every
        partnership must be fully structured and carry a source (never unsourced)."""
        n = 0
        for v in _VDOC["vendors"]:
            for p in (v.get("partnerships") or []):
                n += 1
                for f in ("partner", "kind", "note", "source"):
                    self.assertIn(f, p, f"{v['id']}: partnership missing '{f}'")
                self.assertIn(p["kind"], ("hardware", "cloud", "clinical", "channel", "other"),
                              f"{v['id']}: bad partnership kind {p['kind']!r}")
                self.assertTrue(p["source"], f"{v['id']}: partnership '{p['partner']}' has no source")
        self.assertGreaterEqual(n, 100, "expected partnerships to be populated from research")

    def test_founded_is_year_or_null(self):
        for v in _VDOC["vendors"]:
            f = v.get("founded")
            self.assertTrue(f is None or (isinstance(f, int) and 1800 <= f <= 2026),
                            f"{v['id']}: founded {f!r} not a plausible year or null")

    def test_history_non_empty(self):
        for v in _VDOC["vendors"]:
            self.assertTrue(str(v.get("history", "")).strip(), f"{v['id']}: empty history")

    def test_claims_are_sourced(self):
        """§8: a named leader, a market-position claim, or a history statement
        requires at least one source. Honest nulls need none."""
        for v in _VDOC["vendors"]:
            claims = bool(str(v.get("history", "")).strip())
            if v.get("leadership") not in UNKNOWN:
                claims = True
            if v.get("market_position") not in UNKNOWN:
                claims = True
            if v.get("market_share") not in UNKNOWN:
                claims = True
            if claims:
                srcs = v.get("sources") or []
                self.assertTrue(isinstance(srcs, list) and any(str(x).strip() for x in srcs),
                                f"{v['id']}: makes claims but has no source (§8 fabrication guard)")

    def test_leadership_shape(self):
        for v in _VDOC["vendors"]:
            ld = v.get("leadership")
            self.assertTrue(ld is None or isinstance(ld, str), f"{v['id']}: leadership not str/null")

    def test_market_share_shape(self):
        """market_share is a cited figure STRING (market + value) or null — never a
        bare number (a percentage with no market/source is §8-meaningless)."""
        for v in _VDOC["vendors"]:
            ms = v.get("market_share")
            self.assertTrue(ms is None or isinstance(ms, str),
                            f"{v['id']}: market_share must be a descriptive string or null, not {type(ms).__name__}")


_LB = yaml.safe_load(open(REPO / "data" / "leaderboards.yaml", encoding="utf-8"))


class TestLeaderboards(unittest.TestCase):
    """Market vendor leaderboards (AI + No-AI), ranked by market share / installed
    base. §8: every entry carries a market_basis; ranking is a dense 1..N sequence."""

    def test_both_boards_present(self):
        lb = _LB["leaderboards"]
        for board in ("ai", "no_ai"):
            self.assertIn(board, lb, f"leaderboards missing '{board}'")
            self.assertTrue(lb[board]["entries"], f"{board}: no entries")
            self.assertEqual(lb[board]["count"], len(lb[board]["entries"]), f"{board}: count mismatch")

    def test_entries_shaped_and_ranked(self):
        for board in ("ai", "no_ai"):
            entries = _LB["leaderboards"][board]["entries"]
            ranks = [e["rank"] for e in entries]
            self.assertEqual(ranks, list(range(1, len(entries) + 1)), f"{board}: ranks not a dense 1..N")
            for e in entries:
                for f in ("rank", "name", "segment", "market_basis"):
                    self.assertIn(f, e, f"{board} entry missing {f}")
                self.assertTrue(str(e["market_basis"]).strip(),
                                f"{board} #{e['rank']} {e['name']}: empty market_basis (§8 needs a ranking basis)")

    def test_mostly_sourced(self):
        """§8: a ranked market claim should be sourced. Allow a few honest nulls,
        but the boards must be overwhelmingly cited, not asserted."""
        for board in ("ai", "no_ai"):
            entries = _LB["leaderboards"][board]["entries"]
            sourced = sum(1 for e in entries if e.get("source"))
            self.assertGreaterEqual(sourced, 0.8 * len(entries),
                                    f"{board}: only {sourced}/{len(entries)} sourced — below §8 bar")

    def test_vendor_id_foreign_key(self):
        """Fusion FK: every entry carries vendor_id (a real registry id, or null
        when the leader is not in the registry). Links Leaderboards <-> Vendors."""
        vids = {v["id"] for v in _VDOC["vendors"]}
        linked = 0
        for board in ("ai", "no_ai"):
            for e in _LB["leaderboards"][board]["entries"]:
                self.assertIn("vendor_id", e, f"{board} #{e['rank']}: no vendor_id key")
                if e["vendor_id"] is not None:
                    self.assertIn(e["vendor_id"], vids,
                                  f"{board} #{e['rank']} {e['name']}: vendor_id '{e['vendor_id']}' not in registry")
                    linked += 1
        self.assertGreater(linked, 0, "no leaderboard entries link to the registry — fusion FK is dead")




_DETAIL = yaml.safe_load(open(REPO / "data" / "detail.yaml", encoding="utf-8"))


class TestCategoryDetail(unittest.TestCase):
    """data/detail.yaml — bilingual per-category explainers (purpose / usage flow /
    tech / Supermicro fit) powering the Explore detail pane's hierarchy diagram."""

    def test_every_category_has_bilingual_detail(self):
        det = _DETAIL["details"]
        for c in CATS:
            self.assertIn(c["id"], det, f"{c['id']}: no detail explainer")
            d = det[c["id"]]
            for f in ("purpose_en", "purpose_zh", "tech_en", "tech_zh", "smci_en", "smci_zh"):
                self.assertTrue(str(d.get(f, "")).strip(), f"{c['id']}: empty {f}")
            self.assertTrue(d.get("usage_flow"), f"{c['id']}: no usage_flow steps")
            for s in d["usage_flow"]:
                self.assertTrue(str(s.get("en", "")).strip() and str(s.get("zh", "")).strip(),
                                f"{c['id']}: usage_flow step missing en/zh")

    def test_detail_pane_renders_hierarchy(self):
        html = (REPO / "app" / "index.html").read_text(encoding="utf-8")
        for marker in ("function detailCard(", "tiers6", "SMCI_FAMILY", "flowstrip"):
            self.assertIn(marker, html, f"detail render missing '{marker}'")


# ============================================================
# Round-6 invariants: app guided-home wayfinding (Q1 locked = funnel front door)
# ============================================================

class TestAppGuidance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import subprocess
        subprocess.run([sys.executable, "tools/build_app.py"], cwd=str(REPO),
                       capture_output=True, text=True, timeout=60)
        cls.html = (REPO / "app" / "index.html").read_text(encoding="utf-8")

    def test_default_tab_is_unified_explore(self):
        """Home folded into Explore: the unified universe (id=tab-taxonomy) is the
        landing tab; there is no separate Home tab."""
        self.assertIn('class="tab on" id="tab-taxonomy"', self.html,
                      "the unified Explore must be the default-active landing tab")
        self.assertNotIn('id="tab-home"', self.html, "the separate Home tab must be gone")

    def test_unified_explore_registered_first_in_nav(self):
        self.assertIn("const TABS=[['taxonomy',", self.html, "the unified Explore must be first in TABS")

    def test_home_surfaces_the_three_plays(self):
        for name in ("Medical Imaging", "Genomics", "GMP Manufacturing"):
            self.assertIn(name, self.html, f"Home must surface play '{name}'")

    def test_hot_lists_reachable_via_shortcuts(self):
        """The HOT target lists must be reachable by one click — plain-language
        shortcut chips that prefilter Explore (not buried jargon)."""
        for marker in ("exploreFilter", "sc-cust", "sc-oper", "sc-oem", "tab-method"):
            self.assertIn(marker, self.html, f"missing HOT-list shortcut '{marker}'")

    def test_explore_filters_are_collapsible(self):
        """Classification cleanup: the 8 filters live in a collapsible Refine panel,
        not sprayed across the landing view."""
        self.assertIn("el('details'", self.html,
                      "Explore filters must be built into a collapsible <details> Refine panel")

    def test_gotab_is_parameterized_for_deeplinks(self):
        """codex+grok P1: goTab must accept options so tiles/cards deep-link
        (scroll to a play, prefilter Explore) instead of dumping to a generic tab."""
        self.assertIn("function goTab(id,opts", self.html,
                      "goTab must take an opts arg for deep-linking")

    def test_cross_tab_fusion_wired(self):
        """Home/Explore/Vendors/Leaderboards are fused: category<->vendor<->
        leaderboard navigation helpers + the leaderboard-rank badge exist."""
        for marker in ("function goVendor(", "function goCategory(", "lbBadge", "LB_BY_VID"):
            self.assertIn(marker, self.html, f"fusion wiring missing '{marker}'")

    def test_home_groups_by_stakeholder_and_ai(self):
        """Home organises the universe by point-of-care stakeholder (facility /
        doctor / nurse / patient / other), each split AI-driven vs No-AI."""
        self.assertIn("const isAI=", self.html, "Home needs the AI/no-AI derivation helper")
        self.assertIn("c.home_stakeholder===", self.html, "Home must group on home_stakeholder")
        for marker in ("AI-driven", "No-AI"):
            self.assertIn(marker, self.html, f"Home missing the '{marker}' split")

    def test_hot_cards_prefilter_explore(self):
        self.assertIn("exploreFilter", self.html,
                      "HOT stat cards must prefilter Explore to the buyer + opportunity>=3, not open unfiltered Hunt")

    def test_home_counts_are_dynamic_not_hardcoded(self):
        for lie in ("All 14 triggers", "all 53 categories"):
            self.assertNotIn(lie, self.html, f"Home hardcodes '{lie}' — will drift; use array length")

    def test_no_false_crm_state_label(self):
        """grok P1 (still binding): never imply fired-CRM state the app does not have."""
        self.assertNotIn("A trigger fired", self.html,
                         "misleading 'trigger fired' label implies CRM state it does not have")

    def test_explore_top_is_an_active_hunt_launcher_not_a_passive_summary(self):
        """v3.2: the passive summary dashboard is replaced by an ACTIVE launcher with
        four doors (search · SMCI product line · trigger · play). Each door filters the
        category tree (catFilter) and lands on the battle card — no read-only poster."""
        self.assertIn("Start the hunt", self.html, "the launcher must front the four hunt doors")
        self.assertIn("class:'hsearch'", self.html, "door 4: a search box")
        for door in ("Product line", "Trigger", "Play"):
            self.assertIn(door, self.html, f"missing hunt door '{door}'")
        # doors drive a real filter that the tree respects, then scroll to the battle card
        self.assertIn("catFilter", self.html, "doors must drive a category filter")
        self.assertIn("getElementById('twopane')", self.html, "a door must land on the tree + battle card")
        # the signal definitions survive (folded key), not lost in the reshape
        for label in ("What do flagship / customer-HOT / market-leader mean?",):
            self.assertIn(label, self.html, "the 3-signal definitions must remain available")

    def test_battle_card_is_an_actionable_sell_layer(self):
        """v3.2: the category detail pane leads with a battle card — the seller's motion,
        the SMCI reference architecture to pitch, and the trigger→action to act on —
        pulled from data (hardware_profile → SMCI family; triggers reverse-looked-up)."""
        self.assertIn("class:'battle'", self.html, "detail pane must carry the battle-card sell layer")
        for row in ("Your motion", "Reference arch", "Trigger → move"):
            self.assertIn(row, self.html, f"battle card missing row '{row}'")
        # reference architecture is the SMCI family map, not free text
        self.assertIn("smciFam(h)", self.html, "reference architecture must render the SMCI server family")
        # triggers are reverse-looked-up by category, not hardcoded
        self.assertIn("related_categories||[]).includes(c.id)", self.html,
                      "trigger-to-watch must be derived from the category's triggers")

    def test_trigger_door_is_grouped_and_opens_an_organized_brief(self):
        """v3.3: the trigger door is grouped by urgency (not a flat chip row), and a
        click renders an organized brief — window · where to catch · the move · the
        markets it opens (each drilling to a battle card), all from trigger data."""
        self.assertIn("function triggerBrief(", self.html, "clicking a trigger must open an organized brief")
        for row in ("Window", "Where to catch", "The move", "Markets this opens"):
            self.assertIn(row, self.html, f"trigger brief missing '{row}'")
        # the brief is built from the real trigger fields, not hardcoded
        for field in ("t.window", "t.source", "t.action", "t.related_categories"):
            self.assertIn(field, self.html, f"brief must render trigger field '{field}'")
        # the door is grouped by urgency, and every seed trigger is present
        self.assertIn("t.urgency===uk", self.html, "trigger door must group by urgency")
        for sig in ("New sequencer purchase", "Cyber incident", "FDA IND filing",
                    "Serialization", "Cloud repatriation", "Plant modernization"):
            self.assertIn(sig, self.html, f"trigger '{sig}' must be present")

    def test_partner_landscape_drawer(self):
        """v3.7: a second drawer shows who each vendor partners with, hardware/cloud
        partners highlighted as SMCI co-sell / displacement angles, read from data."""
        self.assertIn("Who these vendors partner with", self.html)
        self.assertIn("class:'pchip'", self.html)
        self.assertIn("pk-hw", self.html)
        self.assertIn(".partnerships||[]", self.html)

    def test_method_is_a_how_to_use_learn_page(self):
        """v3.9: Method is one teaching page ('how to use this map') with a static
        system-flow diagram, not the old plays/signals/scoring/accounts sub-nav."""
        self.assertIn("How to use this map", self.html)
        self.assertIn("class:'sysflow'", self.html, "Method needs the system-flow diagram")
        self.assertNotIn("renderAccountsInto", self.html, "the fictional Accounts sub-tab must be gone")

    def test_single_search_input(self):
        """v3.9: exactly one search field (the prominent launcher input, also read by
        render); the duplicate toolbar search was removed."""
        self.assertEqual(self.html.count("id:'fTxt'"), 1, "there must be exactly one fTxt search input")

    def test_no_ai_slop_side_stripes_and_oklch_palette(self):
        """v3.9 premium pass: no side-stripe accent borders (impeccable ban), and the
        palette is OKLCH-based (harmonized shelf), not ad-hoc hex."""
        import re as _re
        stripes = _re.findall(r"border-(?:left|right):[2-9]\d*px", self.html)
        self.assertEqual(stripes, [], f"side-stripe accents are banned: {stripes[:3]}")
        self.assertIn("oklch(", self.html, "palette must be OKLCH")
        self.assertIn("tabular-nums", self.html, "numbers must use tabular figures")

    def test_tree_auto_collapses_when_browsing_many(self):
        """v3.9: category-tree groups collapse by default when browsing many, and the
        group holding the selected category auto-opens."""
        self.assertIn("openIf=list=>shown.length", self.html,
                      "the tree must auto-collapse groups (open the selected one)")

    def test_back_navigation_exists(self):
        """v3.6: every drill-down (door -> brief -> battle card, chip -> chip) is
        reversible — a Back button pops a nav stack of {catFilter, detail-view} and
        restores the prior view."""
        for marker in ("navStack", "function goBack(", "function pushNav(",
                       "function viewCat(", "class:'backbtn'"):
            self.assertIn(marker, self.html, f"back-navigation missing '{marker}'")
        # the pushing navigations are wired
        self.assertIn("function applyDv(", self.html, "back must restore the detail view by kind")

    def test_vendor_market_share_drawer_with_proportional_bars(self):
        """v3.5: the category vendor list is a collapsible drawer; each vendor gets a
        proportional market-share bar from a cited number (market_share_pct) or 'n/a'.
        Tracks are a fixed width so bars are comparable; never fabricated."""
        self.assertIn("class:'vdrawer'", self.html, "vendor list must be a collapsible drawer")
        self.assertIn("market_share_pct", self.html, "bars must read the structured share field")
        self.assertIn("class:'msfill'", self.html, "each share must render a proportional bar")
        # a fixed-width track column so bars are comparable across rows
        self.assertIn("grid-template-columns:minmax(120px,1fr) clamp(", self.html,
                      "the track column must be a fixed width so bars share one scale")
        # missing data shows n/a, not a fabricated bar
        self.assertIn("'n/a','未公開'", self.html, "vendors without a cited share must show n/a, not a made-up bar")

    def test_plays_are_navigable_and_open_a_play_brief(self):
        """v3.4: a play is a navigable filter, not a decoration. Play chips everywhere
        (door, trigger brief, battle card) call goPlay -> a play brief (anchor · segments ·
        the triggers that open it · target categories), closing trigger<->play<->category."""
        self.assertIn("function playBrief(", self.html, "clicking a play must open a play brief")
        self.assertIn("function goPlay(", self.html, "play chips must be navigable")
        self.assertIn("function goTrigger(", self.html, "trigger chips must be navigable")
        for row in ("Hardware anchor", "Triggers that open this play", "Target categories"):
            self.assertIn(row, self.html, f"play brief missing '{row}'")
        # Play D must have a distinct chip colour (colour/weight, no emoji)
        self.assertIn(".playd{background:var(--d)}", self.html, "Play D needs its own chip colour")
        # the play chips are wired to goPlay (not inert labels)
        self.assertIn("ch.onclick=()=>goPlay(p)", self.html, "battle-card play chip must call goPlay")

    def test_detail_does_not_conflate_leaderboard_with_cosell_motion(self):
        """codex-lens finding: leaderboard rank is a VENDOR standing signal, not the
        co-sell MOTION (which is set by hardware_buyer). The old 'co-sell' label on
        every ranked-vendor list wrongly implied the motion; it must be motion-neutral."""
        self.assertNotIn("服務本類的市場領導者 — 共銷", self.html,
                         "detail-pane must not label ranked vendors 'co-sell' (motion-conflation)")
        self.assertNotIn("Co-sell rank", self.html,
                         "no rank column may be labelled 'Co-sell rank' (motion-conflation)")


class TestWorkloadEnvelope(unittest.TestCase):
    """taxonomy v7 — per-category workload_envelope (12 keys). Provenance is FIXED
    by field identity: derived (== workload_ceiling helper, no citation) /
    framework-judgment (expert ordinal, no citation) / sourced (real citation).
    Spec: .claude/skills/quantify-fields/reference/workload-envelope-spec.json."""

    def _envs(self):
        """(id, envelope) pairs for categories that carry a dict envelope. INV-1 is
        the presence gate; the coherence INVs iterate only well-formed envelopes."""
        return [(c["id"], c["workload_envelope"]) for c in CATS
                if isinstance(c.get("workload_envelope"), dict)]

    # INV-1 presence + exact key set
    def test_every_category_has_envelope_with_all_keys(self):
        for c in CATS:
            we = c.get("workload_envelope")
            self.assertIsInstance(we, dict, f"{c['id']}: workload_envelope missing/not a mapping")
            missing = [k for k in WE_KEYS if k not in we]
            self.assertFalse(missing, f"{c['id']}: envelope missing keys {missing}")
            extra = [k for k in we if k not in WE_KEYS]
            self.assertFalse(extra, f"{c['id']}: envelope has unexpected keys {extra}")

    # INV-2 enum declaration + membership
    def test_enum_membership(self):
        for ek, want in WORKLOAD_ENUMS.items():
            have = set(ENUMS.get(ek, []))
            self.assertEqual(have, want, f"enums.{ek}: {sorted(have ^ want)} differ")
        for cid, we in self._envs():
            for field, ek in WE_ENUM_OF.items():
                v = we.get(field)
                if v is None:
                    continue
                self.assertIn(v, WORKLOAD_ENUMS[ek], f"{cid}.{field}='{v}' not in {ek}")

    # INV-3 no fabricated precision (only per_unit value_low/high may be numeric)
    def test_no_fabricated_precision(self):
        def walk(node, path):
            if isinstance(node, bool):
                return
            if isinstance(node, (int, float)):
                self.fail(f"{path}: raw number {node} outside per_unit_data_size")
            if isinstance(node, dict):
                for k, v in node.items():
                    walk(v, f"{path}.{k}")
            elif isinstance(node, list):
                for i, v in enumerate(node):
                    walk(v, f"{path}[{i}]")
        for cid, we in self._envs():
            for k, v in we.items():
                if k == "per_unit_data_size":
                    continue
                walk(v, f"{cid}.{k}")

    # INV-4 per_unit shape + real cross-listed source
    def test_per_unit_shape_and_source(self):
        for cid, we in self._envs():
            pu = we.get("per_unit_data_size")
            if pu is None:
                continue
            self.assertIsInstance(pu, dict, f"{cid}.per_unit_data_size must be mapping or null")
            self.assertEqual(set(pu), {"value_low", "value_high", "unit", "confidence", "source"},
                             f"{cid}.per_unit_data_size must have EXACTLY the 5 keys, got {sorted(pu)}")
            for nk in ("value_low", "value_high"):
                v = pu[nk]
                self.assertTrue(isinstance(v, (int, float)) and not isinstance(v, bool),
                                f"{cid}.per_unit_data_size.{nk} must be a finite number")
                self.assertEqual(v, v, f"{cid}.{nk} is NaN")           # NaN != NaN
                self.assertNotIn(v, (float("inf"), float("-inf")), f"{cid}.{nk} is infinite")
            self.assertGreaterEqual(pu["value_low"], 0, f"{cid}: value_low must be >= 0")
            self.assertLessEqual(pu["value_low"], pu["value_high"], f"{cid}: value_low>value_high")
            self.assertTrue(isinstance(pu["unit"], str) and pu["unit"].strip(),
                            f"{cid}.per_unit_data_size.unit must be a non-empty string")
            self.assertIn(pu["confidence"], {"A", "B", "C"}, f"{cid}: per_unit confidence must be A/B/C")
            src = pu["source"]
            self.assertTrue(isinstance(src, str) and src and src not in WE_PLACEHOLDER_SOURCES,
                            f"{cid}: per_unit source empty/placeholder ('{src}')")
            self.assertIn(src, we.get("sources") or [],
                          f"{cid}: per_unit source not cross-listed in sources")

    # INV-4b retention source-quality (symmetric to INV-4; A/B is fill convention —
    # a flat sources list can only machine-enforce a real, non-placeholder citation)
    def test_retention_source_quality(self):
        for cid, we in self._envs():
            if we.get("retention_horizon") is None:
                continue
            good = [s for s in (we.get("sources") or [])
                    if isinstance(s, str) and s and s not in WE_PLACEHOLDER_SOURCES]
            self.assertTrue(good, f"{cid}: retention_horizon set but no real citation in sources")

    # INV-5 GPU crown + totality
    def test_gpu_crown_and_totality(self):
        for c in CATS:
            we = c.get("workload_envelope")
            if not isinstance(we, dict):
                continue
            gr = we.get("gpu_role")
            has_gpu = "gpu-server" in (c.get("hardware_profile") or [])
            self.assertEqual(gr not in ("none", None), has_gpu,
                             f"{c['id']}: gpu_role={gr} but gpu-server-in-profile={has_gpu}")
            if gr == "training":
                self.assertIn((c.get("hardware_profile_sizing") or {}).get("gpu-server"),
                              {"rack", "cluster"}, f"{c['id']}: training gpu must be rack/cluster")

    # INV-6 capacity <-> storage + sizing
    def test_capacity_storage_sizing(self):
        for c in CATS:
            we = c.get("workload_envelope")
            if not isinstance(we, dict):
                continue
            prof = c.get("hardware_profile") or []
            siz = c.get("hardware_profile_sizing") or {}
            cb = we.get("capacity_band")
            storage = [s for s in _STORAGE_COMPONENTS if s in prof]
            if cb == "petabyte-plus":
                self.assertTrue(storage, f"{c['id']}: petabyte-plus but no storage component")
                self.assertIn("cluster", {siz.get(s) for s in storage},
                              f"{c['id']}: petabyte-plus needs a cluster-sized storage tier")
            if cb == "none":
                self.assertFalse(storage, f"{c['id']}: capacity 'none' but storage present")

    # INV-7 io <-> nvme/hpc
    def test_io_nvme_hpc(self):
        for c in CATS:
            we = c.get("workload_envelope")
            if isinstance(we, dict) and we.get("io_pattern") == "high-throughput-parallel":
                prof = set(c.get("hardware_profile") or [])
                self.assertTrue({"nvme-performance-storage", "high-performance-computing-cpu"} & prof,
                                f"{c['id']}: high-throughput-parallel needs nvme or hpc-cpu")

    # INV-8 growth <-> storage
    def test_growth_storage(self):
        for c in CATS:
            we = c.get("workload_envelope")
            if isinstance(we, dict) and we.get("data_growth") == "explosive":
                self.assertTrue(_STORAGE_COMPONENTS & set(c.get("hardware_profile") or []),
                                f"{c['id']}: explosive growth needs a storage component")

    # INV-10 availability <-> HA/DR (one-directional)
    def test_availability_ha_dr(self):
        for c in CATS:
            we = c.get("workload_envelope")
            if isinstance(we, dict) and we.get("availability_class") == "mission-critical":
                self.assertTrue({"high-availability-redundant", "disaster-recovery-backup"}
                                & set(c.get("hardware_profile") or []),
                                f"{c['id']}: mission-critical needs HA or DR component")

    # INV-11 latency <-> edge / time-series
    def test_latency_edge_timeseries(self):
        for c in CATS:
            we = c.get("workload_envelope")
            if not isinstance(we, dict):
                continue
            lat = we.get("latency_class")
            prof = set(c.get("hardware_profile") or [])
            mod = set(c.get("data_modality") or [])
            dep = set(c.get("deployment") or [])
            if lat in ("real-time", "deterministic-real-time"):
                self.assertTrue(("time-series" in mod) or ("edge" in dep) or ("edge-industrial" in prof),
                                f"{c['id']}: {lat} needs time-series/edge/edge-industrial")
            if lat == "deterministic-real-time":
                self.assertIn("edge-industrial", prof, f"{c['id']}: deterministic needs edge-industrial")

    # INV-12 SaaS-light degenerate (concurrency intentionally unconstrained)
    def test_saas_light_degenerate(self):
        for c in CATS:
            we = c.get("workload_envelope")
            if c.get("hardware_profile") or not isinstance(we, dict):
                continue
            self.assertIn(we.get("gpu_role"), ("none", None), c["id"])
            self.assertIn(we.get("capacity_band"), ("none", None), c["id"])
            self.assertIn(we.get("data_growth"), ("static", "low", None), c["id"])
            self.assertIn(we.get("availability_class"), ("best-effort", "standard", None), c["id"])
            self.assertIsNone(we.get("per_unit_data_size"), c["id"])

    # INV-13 scaling_driver presence
    def test_scaling_driver_presence(self):
        for c in CATS:
            we = c.get("workload_envelope")
            if not isinstance(we, dict):
                continue
            sd = we.get("scaling_driver")
            if c.get("hardware_profile"):
                self.assertTrue(isinstance(sd, str) and sd.strip(),
                                f"{c['id']}: scaling_driver required (non-empty hardware_profile)")

    # INV-14 provenance gate — derived == pure-helper(tags), exactly
    def test_provenance_gate(self):
        for c in CATS:
            we = c.get("workload_envelope")
            if not isinstance(we, dict):
                continue
            derived = workload_ceiling.derive_for_category(c)
            for f in WE_DERIVED:
                self.assertIn(f, derived, f"helper produced no rule for derived '{f}' ({c['id']})")
                self.assertEqual(we.get(f), derived[f],
                                 f"{c['id']}.{f}={we.get(f)} != helper {derived[f]} (derived must equal ceiling)")

    def test_helper_signature_is_tag_only(self):
        import inspect
        params = set(inspect.signature(workload_ceiling.derive_bands).parameters)
        self.assertFalse(params & {"workload_envelope", "envelope"},
                         "helper signature leaks the envelope — positive-equality would go vacuous")
        self.assertTrue(params <= set(workload_ceiling.TAG_PARAMS),
                        f"helper takes non-tag params: {params - set(workload_ceiling.TAG_PARAMS)}")

    # INV-15 no cut/precision keys + prose digit guard
    def test_no_cut_keys_and_prose_digit_guard(self):
        for cid, we in self._envs():
            bad = WE_CUT_KEYS & set(we.keys())
            self.assertFalse(bad, f"{cid}: resurrected cut/precision keys {bad}")
            for pf in ("scaling_driver", "notes"):
                v = we.get(pf)
                if isinstance(v, str):
                    self.assertIsNone(_DIGIT.search(v),
                                      f"{cid}.{pf} contains a raw digit — spell magnitudes out")

    # INV-16 flagship non-degenerate
    def test_flagship_non_degenerate(self):
        for c in CATS:
            we = c.get("workload_envelope")
            if c.get("hardware_opportunity") != 4 or not isinstance(we, dict):
                continue
            ok = (we.get("gpu_role") in ("inference", "training", "mixed")
                  or we.get("capacity_band") == "petabyte-plus"
                  or we.get("availability_class") == "mission-critical"
                  or we.get("io_pattern") == "high-throughput-parallel")
            self.assertTrue(ok, f"{c['id']}: flagship envelope is degenerate")

    # INV-18 concurrency <-> scale (codex: couple to a serving/compute tier, not
    # arbitrary sizing — archive storage does not serve thousands of sessions)
    def test_concurrency_scale(self):
        SERVING = ("gpu-server", "high-performance-computing-cpu",
                   "high-memory", "high-availability-redundant")
        for c in CATS:
            we = c.get("workload_envelope")
            if isinstance(we, dict) and we.get("concurrency") == "massive":
                siz = c.get("hardware_profile_sizing") or {}
                ok = any(siz.get(comp) in ("rack", "cluster") for comp in SERVING)
                self.assertTrue(ok, f"{c['id']}: 'massive' concurrency needs a rack/cluster-sized "
                                    f"compute/GPU/HA tier (not archive-only)")


# ============================================================
# Load-time integrity: the app's inline JS must not reference a function it
# never defines. Regression guard for the v3.9 dead-code sweep, which deleted
# renderLeaderboardsInto while renderVendors still called it -> renderAll() threw
# at load, leaving Vendors empty and the language toggle unbound (line after
# renderAll() never ran). Static string tests could not catch it; this can.
# ============================================================

class TestNoUndefinedRenderRefs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import subprocess
        subprocess.run([sys.executable, "tools/build_app.py"], cwd=str(REPO),
                       capture_output=True, text=True, timeout=60)
        cls.src = (REPO / "tools" / "build_app.py").read_text(encoding="utf-8")

    def test_every_render_into_called_is_defined(self):
        """Any render*Into wired into a subNav/renderAll must have a definition —
        otherwise renderAll() throws at load and cascades (Vendors blank, toggle dead)."""
        called = set(re.findall(r"\brender\w+Into\b", self.src))
        defined = set(re.findall(r"function\s+(render\w+Into)\s*\(", self.src))
        missing = sorted(called - defined)
        self.assertEqual(missing, [], f"render*Into called but never defined: {missing}")

    def test_renderall_tab_renderers_defined(self):
        """The three tab renderers renderAll() calls must all exist."""
        for fn in ("renderTaxonomy", "renderMethod", "renderVendors"):
            self.assertRegex(self.src, r"function\s+%s\s*\(" % fn,
                             f"renderAll() calls {fn}() but it is not defined")

    def test_langtog_bind_after_initial_render(self):
        """langtog.onclick is bound on the line AFTER renderAll(); if the initial
        renderAll() can throw, the toggle never binds. Keep them adjacent so the
        guard above (no undefined refs) actually protects the binding."""
        m = re.search(r"renderAll\(\);\s*\n\s*\$\('#langtog'\)\.onclick", self.src)
        self.assertIsNotNone(m, "langtog.onclick must be bound immediately after renderAll()")


# ============================================================
# Vendor bundle-filters + ranking matrix (region / state / coverage / Fortune / US share)
# ============================================================

class TestVendorFiltersAndRanking(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import subprocess
        subprocess.run([sys.executable, "tools/build_app.py"], cwd=str(REPO),
                       capture_output=True, text=True, timeout=60)
        cls.src = (REPO / "tools" / "build_app.py").read_text(encoding="utf-8")
        cls.vd = yaml.safe_load(open(REPO / "data" / "vendors.yaml", encoding="utf-8"))
        cls.vs = cls.vd["vendors"]

    def test_filter_helpers_and_ranking_defined(self):
        for fn in ("hqParse", "coverageOf", "fortuneOf", "usShareOf", "bundleScore",
                   "vfMatch", "renderFilterBar", "renderBundleRankingInto",
                   "listedOf", "neuroOf", "listedLabel"):
            self.assertRegex(self.src, r"function\s+%s\s*\(" % fn,
                             f"vendor filter/ranking needs {fn}() defined")

    def test_ranking_wired_into_vendor_subnav(self):
        self.assertIn("renderBundleRankingInto]", self.src,
                      "Bundle ranking must be a Vendors sub-tab")

    def test_listing_and_neuro_filters_wired(self):
        """The listing (public/private) and neuro filters must live in the shared VF model
        and be applied by vfMatch, so both the registry and the bundle ranking honour them."""
        self.assertRegex(self.src, r"VF\s*=\s*\{[^}]*listed\s*:", "VF must carry a listed filter")
        self.assertRegex(self.src, r"VF\s*=\s*\{[^}]*neuro\s*:", "VF must carry a neuro filter")
        self.assertIn("VF.listed", self.src)
        self.assertIn("VF.neuro", self.src)

    def test_fortune_blocks_are_sourced_and_valid(self):
        """No fabrication: every fortune block carries a valid list + a source string."""
        valid = {"fortune-500", "fortune-1000", "global-500"}
        fort = [v for v in self.vs if v.get("fortune")]
        self.assertGreaterEqual(len(fort), 50, "expected the researched Fortune members")
        for v in fort:
            f = v["fortune"]
            self.assertIn(f.get("list"), valid, f"{v['id']}: bad fortune list {f.get('list')}")
            self.assertTrue(str(f.get("source", "")).strip(),
                            f"{v['id']}: fortune claim must carry a source")

    def test_us_share_is_sourced_us_only(self):
        us = [v for v in self.vs if isinstance(v.get("us_market_share_pct"), (int, float))]
        self.assertGreaterEqual(len(us), 10, "expected researched US market-share figures")
        for v in us:
            self.assertTrue(0 < v["us_market_share_pct"] <= 100, f"{v['id']}: US share out of range")
            self.assertTrue(str(v.get("us_share_basis", "")).strip(),
                            f"{v['id']}: US share needs a basis note (proves it is a US figure)")

    def test_no_null_headquarters(self):
        """HQ-fill closed every gap — region/state derivation depends on a parseable HQ."""
        nulls = [v["id"] for v in self.vs if not v.get("headquarters")]
        self.assertEqual(nulls, [], f"vendors with null HQ break region filtering: {nulls}")


class TestComputeClass(unittest.TestCase):
    """v4.2: compute_class — the 'what iron does the software pull' axis (GPU rack / CPU
    workstation / CPU server / edge / storage). Derived, surfaced as an Explore lens + a
    launcher door + a per-play split. Locks the derivation to the current taxonomy."""
    _tax = yaml.safe_load(open(REPO / "data" / "taxonomy.yaml", encoding="utf-8"))["categories"]

    @classmethod
    def setUpClass(cls):
        cls.src = (REPO / "tools" / "build_app.py").read_text(encoding="utf-8")

    @staticmethod
    def _cc(c):
        hp = set(c.get("hardware_profile") or [])
        gr = (c.get("workload_envelope") or {}).get("gpu_role")
        if "gpu-server" in hp or gr in ("inference", "training", "mixed"):
            return "gpu-mixed" if gr == "mixed" else "gpu"
        if hp & {"high-performance-computing-cpu", "high-memory"}:
            return "cpu-workstation"
        if "high-availability-redundant" in hp:
            return "cpu-db"
        if "edge-industrial" in hp:
            return "cpu-edge"
        if hp & {"capacity-archive-storage", "nvme-performance-storage", "disaster-recovery-backup"}:
            return "storage"
        return "saas-light"

    def test_helpers_and_lens_wired_in_app(self):
        for fn in ("computeClassOf", "ccLabel", "ccSku", "exploreCompute"):
            self.assertRegex(self.src, r"function\s+%s\s*\(|%s\s*=" % (fn, fn),
                             f"compute lens needs {fn}")
        self.assertIn("fCompute", self.src, "compute-type filter must exist")
        self.assertRegex(self.src, r"\['compute',", "compute must be a group-by option")
        self.assertIn("exploreCompute", self.src, "the compute-type door must call exploreCompute")
        self.assertRegex(self.src, r"axis===?'compute'", "groupsOf must handle the compute axis")

    def test_class_distribution_locked(self):
        from collections import Counter
        dist = Counter(self._cc(c) for c in self._tax)
        # regression lock — matches the verified web/taxonomy state (v4.2)
        self.assertEqual(dist["cpu-workstation"], 5, f"cpu-workstation drift: {dist}")
        self.assertEqual(dist["gpu"] + dist["gpu-mixed"], 22, f"GPU total drift: {dist}")
        self.assertEqual(dist["cpu-db"], 14, f"cpu-db drift: {dist}")
        self.assertEqual(sum(dist.values()), len(self._tax))

    def test_key_categories_classified_right(self):
        byid = {c["id"]: c for c in self._tax}
        expect = {"pharmacometrics-modeling-simulation": "cpu-workstation",
                  "ehr-emr-core": "cpu-db", "pacs-vna": "storage"}
        for cid, want in expect.items():
            if cid in byid:
                self.assertEqual(self._cc(byid[cid]), want, f"{cid} should be {want}")

    def test_no_gpu_in_cpu_classes(self):
        """A CPU-* class must never carry a gpu-server component (would contradict the badge)."""
        for c in self._tax:
            k = self._cc(c)
            if k.startswith("cpu-") or k == "storage":
                self.assertNotIn("gpu-server", c.get("hardware_profile") or [],
                                 f"{c['id']}: {k} but has gpu-server")


class TestVendorPartnerType(unittest.TestCase):
    """v4.7: GTM partner-type (web-verified) — how SMCI engages each vendor. Every vendor carries a
    primary type from the closed set + confidence; also_types (multi-tag) are from the same set."""
    SET = {"isv", "var", "si", "msp", "channel-partner", "reseller", "oem-device"}

    def test_every_vendor_has_partner_type(self):
        for v in _VDOC["vendors"]:
            pt = v.get("partner_type")
            self.assertIsInstance(pt, dict, f"{v['id']}: missing partner_type")
            self.assertIn(pt.get("primary"), self.SET, f"{v['id']}: bad primary {pt.get('primary')!r}")
            self.assertIn(pt.get("confidence"), {"A", "B", "C", "D"}, f"{v['id']}: partner_type needs confidence")
            for t in (pt.get("also") or []):
                self.assertIn(t, self.SET, f"{v['id']}: bad also-type {t!r}")
                self.assertNotEqual(t, pt["primary"], f"{v['id']}: also duplicates primary")

    def test_partner_type_distribution_sane(self):
        from collections import Counter
        dist = Counter(v["partner_type"]["primary"] for v in _VDOC["vendors"])
        self.assertGreater(dist["isv"], 150, f"most software vendors should be ISV: {dist}")
        self.assertGreater(dist["oem-device"], 20, f"expected the device/imaging OEMs: {dist}")
        byid = {v["id"]: v for v in _VDOC["vendors"]}
        # spot-checks: an imaging OEM and a pure ISV
        for oem in ("philips", "canon-medical", "ge-healthcare"):
            if oem in byid:
                self.assertEqual(byid[oem]["partner_type"]["primary"], "oem-device", f"{oem} should be oem-device")


class TestVendorListingNeuro(unittest.TestCase):
    """v4.1: public-listing status + brain/neuro flag enrichment (web-verified). §8: every
    listing verdict carries a confidence AND a source; a ticker only on a public status."""
    LISTED = {"public", "subsidiary_of_public", "subsidiary_of_private", "private",
              "acquired", "nonprofit_or_gov", "unknown"}

    def test_every_vendor_has_listing_block(self):
        for v in _VDOC["vendors"]:
            l = v.get("listing")
            self.assertIsInstance(l, dict, f"{v['id']}: missing listing block")
            self.assertIn(l.get("status"), self.LISTED, f"{v['id']}: bad listing status {l.get('status')!r}")
            self.assertIn(l.get("confidence"), {"A", "B", "C", "D"}, f"{v['id']}: listing needs A/B/C/D confidence")

    def test_listing_is_sourced(self):
        """No fabrication: a resolved listing status (anything but unknown) must carry a
        source — a URL or a named basis (Fortune / ticker-in-registry)."""
        for v in _VDOC["vendors"]:
            l = v["listing"]
            if l["status"] != "unknown":
                self.assertTrue(str(l.get("source", "")).strip(),
                                f"{v['id']}: listing '{l['status']}' has no source (§8)")

    def test_ticker_only_on_public(self):
        for v in _VDOC["vendors"]:
            l = v["listing"]; tk = l.get("ticker")
            if tk:
                self.assertIn(l["status"], {"public", "subsidiary_of_public"},
                              f"{v['id']}: ticker {tk} but status {l['status']}")
                # EXCHANGE:SYMBOL (web-verified) or a bare SYMBOL (from the registry name); never empty
                self.assertRegex(tk, r"^([A-Za-z.\-]+:)?[A-Za-z0-9.\-]{1,7}$",
                                 f"{v['id']}: ticker {tk!r} not a valid symbol / EXCHANGE:SYMBOL")

    def test_no_unknown_left_after_verification(self):
        """The web sweep resolved every vendor; publishing 'unknown' to the public site is
        not allowed (that was the whole point of the verification pass)."""
        unk = [v["id"] for v in _VDOC["vendors"] if v["listing"]["status"] == "unknown"]
        self.assertEqual(unk, [], f"unresolved listing status must not ship: {unk}")

    def test_neuro_flag_shape_and_known_members(self):
        byid = {v["id"]: v for v in _VDOC["vendors"]}
        for v in _VDOC["vendors"]:
            if "neuro" in v:
                self.assertIsInstance(v["neuro"], bool, f"{v['id']}: neuro must be boolean")
        neuro_ids = {v["id"] for v in _VDOC["vendors"] if v.get("neuro") is True}
        self.assertGreaterEqual(len(neuro_ids), 8, "expected the researched neuro set")
        for nid in ("brainlab", "viz-ai", "rapidai", "qure-ai", "elekta"):
            if nid in byid:
                self.assertTrue(byid[nid].get("neuro") is True, f"{nid} should be flagged neuro")
        # a clearly non-neuro system-of-record vendor must not be flagged
        if "epic-systems" in byid:
            self.assertNotEqual(byid["epic-systems"].get("neuro"), True, "epic-systems is not neuro")

    def test_no_bci_makers_in_a_software_list(self):
        """The full 309 web scan found zero implantable brain-chip makers; guard that no
        vendor is mislabelled with a bci=true (this is a software registry, not implants)."""
        bci = [v["id"] for v in _VDOC["vendors"] if v.get("bci") is True]
        self.assertEqual(bci, [], f"no implantable-BCI makers expected in a software registry: {bci}")


# ============================================================
# taxonomy-tree pilot — level-2 sub-markets nest under a category via `parent`
# (categories stay LOCKED at 59 via TestInventoryLocked; the tree grows here)
# ============================================================
SUBS = TAX.get("subcategories", [])
_CAT_IDS = {c["id"] for c in CATS}
_SUB_REQUIRED = ["id", "parent", "name_en", "name_zh", "scope_en", "scope_zh",
                 "role", "data_modality", "hardware_profile", "hardware_opportunity",
                 "primary_buyer", "segments", "vendors", "confidence", "source"]


class TestSubcategories(unittest.TestCase):
    def test_present_and_nonempty(self):
        self.assertTrue(SUBS, "taxonomy.yaml should carry a non-empty subcategories list")

    def test_required_fields(self):
        for s in SUBS:
            for f in _SUB_REQUIRED:
                self.assertIn(f, s, f"subcategory {s.get('id','?')} missing field {f}")

    def test_ids_unique_kebab_and_no_category_collision(self):
        seen = set()
        for s in SUBS:
            sid = s["id"]
            self.assertRegex(sid, r"^[a-z0-9]+(-[a-z0-9]+)*$", f"{sid}: id must be kebab-case")
            self.assertNotIn(sid, seen, f"{sid}: duplicate subcategory id")
            seen.add(sid)
            self.assertNotIn(sid, _CAT_IDS, f"{sid}: subcategory id collides with a category id")

    def test_parent_resolves_and_no_cycle(self):
        """parent must point at a category or another subcategory; walking parents terminates."""
        sub_ids = {s["id"] for s in SUBS}
        by_id = {s["id"]: s for s in SUBS}
        for s in SUBS:
            self.assertNotEqual(s["parent"], s["id"], f"{s['id']}: self-parent")
            self.assertIn(s["parent"], _CAT_IDS | sub_ids, f"{s['id']}: parent {s['parent']} unknown")
            # walk up: a subcategory chain must reach a category without looping
            seen, cur, hops = set(), s, 0
            while cur["parent"] in sub_ids:
                self.assertNotIn(cur["id"], seen, f"{s['id']}: cycle in parent chain")
                seen.add(cur["id"])
                cur = by_id[cur["parent"]]
                hops += 1
                self.assertLess(hops, 50, f"{s['id']}: parent chain too deep / cyclic")
            self.assertIn(cur["parent"], _CAT_IDS, f"{s['id']}: chain does not root at a category")

    def test_vendors_nonempty(self):
        for s in SUBS:
            self.assertTrue(s.get("vendors"), f"{s['id']}: vendors must be non-empty")

    def test_hardware_profile_subset_of_enum(self):
        for s in SUBS:
            bad = [h for h in s["hardware_profile"] if h not in TARGET_ENUMS["hardware_profile"]]
            self.assertFalse(bad, f"{s['id']}: hardware_profile not in enum: {bad}")

    def test_opportunity_in_range(self):
        for s in SUBS:
            self.assertIn(s["hardware_opportunity"], (1, 2, 3, 4), s["id"])

    def test_primary_buyer_in_enum(self):
        for s in SUBS:
            self.assertIn(s["primary_buyer"], TARGET_ENUMS["hardware_buyer"], s["id"])

    def test_no_forbidden_abbreviations(self):
        for s in SUBS:
            for h in s["hardware_profile"]:
                self.assertNotIn(h, FORBIDDEN_ABBREVIATED_VALUES, f"{s['id']}: abbreviated {h}")

    def test_app_renders_subcategories(self):
        """build_app.py must load and render the sub-markets tree."""
        src = (REPO / "tools" / "build_app.py").read_text(encoding="utf-8")
        self.assertIn("subcategories", src, "build_app.py must read DATA.taxonomy.subcategories")
        self.assertIn("subcatsOf", src, "build_app.py must expose a subcatsOf helper")

    def test_tree_depth_is_optional_but_wellformed(self):
        """plan-v6 E1: depth is LEGAL, not REQUIRED. The old test forced grandchildren to exist
        (the deepen-factory root cause). A flat 59→子 tree is now equally valid; but IF any 孫
        exists (a subcategory whose parent is itself a subcategory), its parent must be a real
        subcategory id. Structure check only — never forces the tree to go deeper.
        (The spine-invariant guard that DOES assert 'default tree = 59' arrives in E3.)"""
        subids = {s["id"] for s in SUBS}
        for s in SUBS:
            if s["parent"] in subids:  # this node is a grandchild-or-deeper
                self.assertIn(s["parent"], subids,
                              f"{s['id']}: deeper node's parent must be a real subcategory")

    def test_play_depth_is_optional(self):
        """plan-v6 E1: a play is NOT required to carry deepened categories. The old test forced
        every play to have sub-markets (drove the factory). Now: depth per play is optional; if a
        deepened category exists it must belong to a real category with a well-formed plays list."""
        by_cat = {c["id"]: c for c in CATS}
        for s in SUBS:
            if s["parent"] in by_cat:  # a 子 hanging directly off a category
                self.assertIsInstance(by_cat[s["parent"]].get("plays") or [], list,
                                      f"{s['parent']}: plays must be a list")


# ============================================================
# Explore redesign — the Play spine + the dead-control sweep (audit-driven)
# ============================================================
class TestExploreSpine(unittest.TestCase):
    SRC = (REPO / "tools" / "build_app.py").read_text(encoding="utf-8")

    def test_playtree_defined_and_routed(self):
        self.assertIn("function playTree(", self.SRC, "the Play-spine renderer must exist")
        self.assertIn("if(gp==='play'){playTree(shown);}", self.SRC,
                       "render() must route the 'play' grouping to playTree")

    def test_four_dead_orphan_selects_stay_removed(self):
        # each was created via mk('fX',...) but never appended — shadowing a live control. Guard re-introduction.
        for dead in ("mk('fBuyer'", "mk('fPlay'", "mk('fDep'", "mk('fProfile'"):
            self.assertNotIn(dead, self.SRC, f"dead orphan select re-introduced: {dead}")
        self.assertNotIn("fSpansBox=el(", self.SRC, "dead fSpans checkbox re-introduced")

    def test_compute_filter_not_duplicated(self):
        # the one LIVE duplicate: fCompute select in the More-filters drawer duplicated the launcher chip.
        self.assertNotIn("compute type (SKU)','計算類型(SKU)'),fCompute", self.SRC,
                         "fCompute must not be re-added to the More-filters drawer (duplicates the launcher chip)")

    def test_launcher_play_chip_row_removed(self):
        # Play is the tree spine now; the launcher .dchip Play-chip row was deleted.
        self.assertNotIn("class:'dchip'", self.SRC, "launcher Play-chip row re-introduced (Play is the spine)")

    def test_subcard_scroll_anchor_present(self):
        self.assertIn("id:'sub-'+s.id", self.SRC, "subcards need id=sub-<id> for the L4 spine scroll target")

    def test_recursive_tree_and_sub_detail(self):
        # the tree renders any depth via a recursive node builder + each sub-market gets its own card
        self.assertIn("function treeNodeInto(", self.SRC, "recursive tree-node renderer must exist")
        self.assertIn("function subDetailCard(", self.SRC, "each sub-market needs its own detail card")
        self.assertIn("function chainOf(", self.SRC, "breadcrumb ancestry walk must exist")


# ============================================================
# plan-v6.1 E2 — the retrieval index (data/taxonomy_index.yaml + _tree_index.yaml)
# ============================================================
def _load_index(name):
    p = REPO / "data" / name
    doc = yaml.safe_load(p.read_text(encoding="utf-8"))
    return doc, {r["id"]: r for r in (doc.get("rows") or [])}


_SPINE_DOC, _SPINE = _load_index("taxonomy_index.yaml")
_TREE_DOC, _TREE = _load_index("taxonomy_tree_index.yaml")
_INDEX = {**_SPINE, **_TREE}


class TestTaxIndex(unittest.TestCase):
    """The index is the single retrieval surface + source of truth for visibility/HOT (D7).
    These guard E2: models query this instead of reading the 2.27 MB taxonomy.yaml (D2)."""

    def test_spine_is_the_59_categories_default_visible(self):
        self.assertEqual(len(_SPINE), len(CATS), "spine index must hold exactly the categories")
        self.assertEqual({r["id"] for r in _SPINE.values()}, {c["id"] for c in CATS})
        for r in _SPINE.values():
            self.assertEqual(r["depth"], 0, r["id"])
            self.assertEqual(r["visibility"], "default", r["id"])
            self.assertIsNone(r["parent"], r["id"])

    def test_hot_default_is_35(self):
        """the acceptance gate (D4): default-visible categories with hardware_opportunity>=3 == 35.
        If this is not 35 the index is stale or the taxonomy changed — rebuild + reconcile."""
        hot = [r for r in _SPINE.values() if (r.get("hardware_opportunity") or 0) >= 3]
        self.assertEqual(len(hot), 35, f"HOT_default={len(hot)} (expected 35)")
        self.assertEqual(_SPINE_DOC["counts"]["hot_default"], 35, "spine header hot_default drifted from rows")

    def test_tree_is_the_999_subs_depth_and_visibility(self):
        self.assertEqual(len(_TREE), len(SUBS), "tree index must hold exactly the subcategories")
        for r in _TREE.values():
            self.assertGreaterEqual(r["depth"], 1, r["id"])
            expected = "card" if r["depth"] == 1 else "archived"
            self.assertEqual(r["visibility"], expected, f"{r['id']} depth {r['depth']} -> {r['visibility']}")

    def test_every_index_row_parent_resolves(self):
        for r in _TREE.values():
            self.assertIn(r["parent"], _INDEX, f"{r['id']}: parent {r['parent']} not in index")

    def test_c1_rollup_wellformed(self):
        """C1: category rows carry child_count / descendant_profiles / divergent_children;
        divergent is <=3 real L1 child ids whose profile-set or buyer differs from the parent."""
        for r in _SPINE.values():
            self.assertIn("divergent_children", r, r["id"])
            self.assertLessEqual(len(r["divergent_children"]), 3, r["id"])
            l1 = {s["id"] for s in SUBS if s["parent"] == r["id"]}
            self.assertEqual(r["child_count"], len(l1), r["id"])
            for cid in r["divergent_children"]:
                self.assertIn(cid, l1, f"{r['id']}: divergent child {cid} is not an L1 child")

    def test_spine_index_under_100kb(self):
        """L1 lamp: the loadable retrieval surface stays small. (The tree index is machine-only.)"""
        kb = (REPO / "data" / "taxonomy_index.yaml").stat().st_size / 1024
        self.assertLess(kb, 100, f"spine index {kb:.1f} KB exceeds the 100 KB L1 target")

    def test_index_not_stale(self):
        """freshness signal (brain #4): rebuilding from taxonomy.yaml must reproduce the committed
        counts. Catches 'edited taxonomy.yaml but forgot to run build_index.py'."""
        import importlib.util
        spec = importlib.util.spec_from_file_location("build_index", REPO / "tools" / "build_index.py")
        bi = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bi)
        cats, subs = bi.load_taxonomy()
        rows = bi.build_rows(cats, subs)
        live_hot = sum(1 for r in rows if r["depth"] == 0 and (r["hardware_opportunity"] or 0) >= 3)
        self.assertEqual(len(cats), len(_SPINE), "category count drifted — rebuild the index")
        self.assertEqual(len(subs), len(_TREE), "subcategory count drifted — rebuild the index")
        self.assertEqual(live_hot, 35, "live HOT != 35 — taxonomy changed; rebuild + reconcile")


class TestE3Fold(unittest.TestCase):
    """plan-v6.1 E3a — the Explore tree folds to the 59-category spine; the app consumes the
    index for HOT + the C1 card rollup (C2/D7), and does not recompute HOT or walk 999 nodes."""

    SRC = (REPO / "tools" / "build_app.py").read_text(encoding="utf-8")
    HTML = (REPO / "app" / "index.html").read_text(encoding="utf-8")

    def test_build_injects_the_index(self):
        self.assertIn('"taxonomy_index"', self.SRC, "build_app must inject data/taxonomy_index.yaml")

    def test_hot_reads_the_index_not_customer_pull(self):
        """C2/D7: HOT is the index set, not a recomputed hardware_opportunity_by_buyer.customer filter."""
        self.assertIn("const HOT_IDS=new Set(", self.SRC, "HOT_IDS must be built from the index")
        self.assertIn("isHot=c=>HOT_IDS.has(c.id)", self.SRC, "isHot must read the index HOT set")
        self.assertNotIn("hotN=l=>l.filter(c=>(c.hardware_opportunity_by_buyer.customer||0)>=3)", self.SRC,
                         "hotN must no longer recompute HOT from customer-pull")

    def test_tree_stops_at_category(self):
        """the default tree renders category leaves (catNodeInto), not the recursive 999-node walk."""
        self.assertIn("function catNodeInto(", self.SRC, "category-leaf renderer must exist")
        self.assertIn("catNodeInto(b2,c)", self.SRC, "playTree must render category leaves")
        self.assertNotIn("treeNodeInto(b2,c,0)", self.SRC,
                         "playTree must NOT recurse the full tree (that is the 999-node wall)")

    def test_card_shows_c1_rollup_from_index(self):
        """C1: the card reads descendant_profiles + divergent_children from the index (IDX), not recomputed."""
        self.assertIn("const IDX={}", self.SRC, "IDX lookup over the index rows must exist")
        self.assertIn("ix.descendant_profiles", self.SRC, "card must render the C1 diversity line from the index")
        self.assertIn("ix.divergent_children", self.SRC, "card must render the C1 divergent chips from the index")

    def test_built_html_embeds_the_index(self):
        """the shipped app actually carries the index rows (so the runtime rollup/HOT have data)."""
        self.assertIn("descendant_profiles", self.HTML, "built app/index.html must embed the taxonomy index")


class TestE3bSplit(unittest.TestCase):
    """plan-v6.1 E3b/C3 — the archived L2+ tree ships in taxonomy_tree.js, loaded on demand via a
    <script> element (file://-safe), NOT embedded in index.html and NOT via fetch. app/==docs/ parity."""

    SRC = (REPO / "tools" / "build_app.py").read_text(encoding="utf-8")
    APP_HTML = (REPO / "app" / "index.html").read_text(encoding="utf-8")
    APP_ARCHIVE = (REPO / "app" / "taxonomy_tree.js").read_text(encoding="utf-8")

    def test_archive_ships_in_both_dirs_byte_identical(self):
        a, d = REPO / "app" / "taxonomy_tree.js", REPO / "docs" / "taxonomy_tree.js"
        self.assertTrue(a.exists() and d.exists(), "taxonomy_tree.js must ship in app/ AND docs/")
        self.assertEqual(a.read_bytes(), d.read_bytes(), "taxonomy_tree.js must be byte-identical app==docs")

    def test_archive_assigns_global(self):
        self.assertTrue(self.APP_ARCHIVE.startswith("window.__ARCHIVE__="),
                        "archive must assign window.__ARCHIVE__ (script-loaded, not fetched)")

    def test_deep_subs_archived_not_embedded(self):
        """a real L2+ sub must live in taxonomy_tree.js and be ABSENT from the shipped index.html."""
        tree = yaml.safe_load((REPO / "data" / "taxonomy_tree_index.yaml").read_text(encoding="utf-8"))
        deep_ids = sorted(r["id"] for r in tree["rows"] if r["depth"] >= 2)
        self.assertTrue(deep_ids, "expected some L2+ subs")
        sample = deep_ids[0]
        self.assertIn('"' + sample + '"', self.APP_ARCHIVE, f"{sample} must be in the archive")
        self.assertNotIn('"' + sample + '"', self.APP_HTML,
                         f"{sample} (L2+) must NOT be embedded in index.html (default-only ship)")

    def test_lazy_load_uses_script_not_fetch(self):
        self.assertIn("function loadArchive(", self.SRC, "loadArchive must exist")
        self.assertIn("createElement('script')", self.SRC, "archive loads via a <script> element (file://-safe)")
        self.assertIn("loadArchive(()=>", self.SRC, "drilling must load the archive before rendering")
        # the archive must NOT be pulled with fetch/XHR (blocked over file://)
        self.assertNotIn("fetch('taxonomy_tree", self.SRC, "must not fetch the archive (breaks file://)")

    def test_build_embeds_l1_only(self):
        self.assertIn('taxonomy["subcategories"] = l1_subs', self.SRC,
                      "build must embed only L1 subs; deep_subs go to taxonomy_tree.js")


class TestE4aIntelFK(unittest.TestCase):
    """plan-v6.1 E4a — every vendor_intel record carries a nullable vendor_id; non-null FKs resolve
    to a REAL vendors.id (never invented). The app resolves intel by the FK first, name fallback second."""

    _V = {v["id"] for v in yaml.safe_load((REPO / "data" / "vendors.yaml").read_text(encoding="utf-8"))["vendors"]}
    _I = yaml.safe_load((REPO / "data" / "vendor_intel.yaml").read_text(encoding="utf-8"))["vendors"]
    SRC = (REPO / "tools" / "build_app.py").read_text(encoding="utf-8")

    def test_every_record_has_vendor_id_field(self):
        for r in self._I:
            self.assertIn("vendor_id", r, f"{r.get('key')}: missing vendor_id (run migrate_intel_vendor_id.py)")

    def test_nonnull_fk_resolves_to_real_vendor(self):
        """the FK integrity guarantee — no invented slugs (CLAUDE.md: never fabricate)."""
        for r in self._I:
            vid = r.get("vendor_id")
            if vid is not None:
                self.assertIn(vid, self._V, f"{r['key']}: vendor_id '{vid}' is not a real vendors.id")

    def test_coverage_recorded(self):
        n = sum(1 for r in self._I if r.get("vendor_id"))
        self.assertGreaterEqual(n, 250, f"FK coverage fell to {n}/{len(self._I)} — the migration may be broken")

    def test_app_prefers_fk_then_name(self):
        self.assertIn("const VINTEL_BY_ID={}", self.SRC, "app must build the vendor_id FK lookup")
        self.assertIn("VINTEL_BY_ID[vn]||VINTEL[normVendor(vn)]", self.SRC,
                      "vintelOf must try the FK first, then the normalized-name fallback")


if __name__ == "__main__":
    unittest.main(verbosity=1)
