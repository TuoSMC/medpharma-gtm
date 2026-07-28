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
    "plays", "vendors", "evidence_note", "workload_envelope",
]

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
        self.assertEqual(len(CATS), 58)
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
ENRICH_FIELDS = ["headquarters", "founded", "leadership", "history", "market_position", "sources"]
UNKNOWN = {None, "", "unknown", "not publicly disclosed", "n/a", "not disclosed"}


class TestVendorEnrichment(unittest.TestCase):
    def test_every_vendor_has_enrichment_fields(self):
        for v in _VDOC["vendors"]:
            missing = [f for f in ENRICH_FIELDS if f not in v]
            self.assertFalse(missing, f"vendor {v['id']}: missing enrichment {missing}")

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
            if claims:
                srcs = v.get("sources") or []
                self.assertTrue(isinstance(srcs, list) and any(str(x).strip() for x in srcs),
                                f"{v['id']}: makes claims but has no source (§8 fabrication guard)")

    def test_leadership_shape(self):
        for v in _VDOC["vendors"]:
            ld = v.get("leadership")
            self.assertTrue(ld is None or isinstance(ld, str), f"{v['id']}: leadership not str/null")




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

    def test_default_tab_is_home(self):
        """The guided Home funnel is the landing tab, not the 8-filter grid."""
        self.assertIn('class="tab on" id="tab-home"', self.html,
                      "Home must be the default-active tab (id=tab-home, class 'tab on')")
        # the old filter grid must NOT be the default-on tab
        self.assertNotIn('class="tab on" id="tab-taxonomy"', self.html,
                         "Taxonomy/Explore filter grid must not be the landing tab")

    def test_home_registered_first_in_nav(self):
        self.assertIn("const TABS=[['home',", self.html, "Home must be first in TABS")

    def test_home_surfaces_the_three_plays(self):
        for name in ("Medical Imaging", "Genomics", "GMP Manufacturing"):
            self.assertIn(name, self.html, f"Home must surface play '{name}'")

    def test_home_surfaces_hot_entry_points(self):
        # the guided funnel must expose the HOT lists + a trigger entry
        for marker in ("HOT_customer", "HOT_operator", "tab-triggers"):
            self.assertIn(marker, self.html, f"Home missing guidance entry '{marker}'")

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

    def test_play_tiles_deeplink_to_their_play(self):
        self.assertIn("goTab('hunt',{scrollTo", self.html,
                      "play tiles must deep-link/scroll to their own play section, not generic Hunt")

    def test_hot_cards_prefilter_explore(self):
        self.assertIn("exploreFilter", self.html,
                      "HOT stat cards must prefilter Explore to the buyer + opportunity>=3, not open unfiltered Hunt")

    def test_home_counts_are_dynamic_not_hardcoded(self):
        for lie in ("All 14 triggers", "all 53 categories"):
            self.assertNotIn(lie, self.html, f"Home hardcodes '{lie}' — will drift; use array length")

    def test_trigger_panel_label_is_honest(self):
        """grok P1: the panel is a static urgency-sorted slice, not fired CRM signals."""
        self.assertNotIn("A trigger fired", self.html,
                         "misleading 'trigger fired' label implies CRM state it does not have")
        self.assertIn("Highest-urgency signals", self.html)


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


if __name__ == "__main__":
    unittest.main(verbosity=1)
