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
    "plays", "vendors", "evidence_note",
]

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
        self.assertEqual(len(CATS), 53)
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


if __name__ == "__main__":
    unittest.main(verbosity=1)
