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
                   "software-as-a-service", "vendor-managed", "original-equipment-manufacturer", "edge"},
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
               "data-analytics-payer-platforms"},
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


if __name__ == "__main__":
    unittest.main(verbosity=1)
