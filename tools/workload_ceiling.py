#!/usr/bin/env python3
"""Coherence-ceiling helper — the SINGLE source of truth for the DERIVED fields of
a category's workload_envelope (CLAUDE.md taxonomy v7).

derive_bands() is a PURE function of a category's already-approved TAGS
(hardware_profile, hardware_profile_sizing, data_modality, deployment, role).
It NEVER reads the workload_envelope itself — that is what lets the test assert
`derived value == derive_bands(tags)` as a positive equality without the check
going vacuous (a derived band cannot be laundered above what the tags imply).

Only the four DERIVED fields live here:
    gpu_role, capacity_band, availability_class, latency_class
The framework-judgment fields (data_growth, io_pattern, concurrency) and the
sourced fields (retention_horizon, per_unit_data_size) are NOT computed here —
they are authored per category and governed by other invariants (see
tools/tests/test_chain_integrity.py :: TestWorkloadEnvelope).

Same epistemic class as the existing unsourced hardware_opportunity(1-4) and the
node|rack|cluster sizing tiers: these bands restate design tags, they do not
assert new external market facts, so they carry no citation (§8-clean).
"""
from __future__ import annotations

# The exact tag fields this helper is allowed to see. A test asserts the
# signature never widens to include 'workload_envelope' or any envelope field.
TAG_PARAMS = ("hardware_profile", "hardware_profile_sizing", "data_modality", "role")

_STORAGE = ("nvme-performance-storage", "capacity-archive-storage")


def _gpu_role(profile, sizing, modality, role):
    if "gpu-server" not in profile:
        return "none"
    ai = ("analytics-artificial-intelligence" in role) or ("infrastructure-platform" in role)
    # pure visualisation: a GPU pulled only to render/display images, with no
    # AI-compute role and no model modality (surgical video, TPS/OIS, 3D viz).
    if ("images" in modality) and not ai and ("artificial-intelligence-models" not in modality):
        return "visualization"
    # AI compute: cluster-scale GPU = a train+infer development platform (mixed);
    # node/rack GPU = a serving / accelerated-inference deployment.
    if sizing.get("gpu-server") == "cluster":
        return "mixed"
    return "inference"


def _capacity_band(profile, sizing, modality, role):
    storage = [s for s in _STORAGE if s in profile]
    if not storage:
        return "none"
    tiers = {sizing.get(s) for s in storage}
    if "cluster" in tiers:
        return "petabyte-plus"
    if "rack" in tiers:
        return "hundreds-of-terabytes"
    # all storage sized 'node'
    if "capacity-archive-storage" in storage:
        return "tens-of-terabytes"
    return "terabyte"


def _availability_class(profile, sizing, modality, role):
    ha = "high-availability-redundant" in profile
    dr = "disaster-recovery-backup" in profile
    if ha and dr:
        return "mission-critical"
    if ha or dr:
        return "high-availability"
    # no dedicated HA/DR iron: SaaS-light (no owned profile) is best-effort from
    # the customer-iron view; a category that owns iron but no HA/DR pair is standard.
    if not profile:
        return "best-effort"
    return "standard"


def _latency_class(profile, sizing, modality, role):
    # deployment is intentionally NOT in the helper's signature (kept minimal);
    # edge-deployment latency is captured via the edge-industrial profile
    # component, which every edge category carries.
    edge_ind = "edge-industrial" in profile
    if edge_ind and "time-series" in modality:
        return "deterministic-real-time"  # OT / control-loop
    if edge_ind or ("time-series" in modality):
        return "real-time"
    if ("transactional" in modality) or ("documents" in modality):
        return "interactive"
    if ("images" in modality) and (("workflow" in role) or ("system-of-record" in role)):
        return "interactive"  # image *viewing* workflow (PACS, pathology, 3D viz)
    return "batch"  # omics / simulation / model compute with no user-facing txn


def derive_bands(*, hardware_profile, hardware_profile_sizing, data_modality, role):
    """Pure map: category tags -> the four DERIVED workload_envelope bands.

    Keyword-only and deliberately narrow: it accepts ONLY tag fields, never the
    envelope. Returns a dict with keys gpu_role, capacity_band,
    availability_class, latency_class — every value a member of its enum, TOTAL
    over all 58 categories (no None, no KeyError).
    """
    profile = list(hardware_profile or [])
    sizing = dict(hardware_profile_sizing or {})
    modality = list(data_modality or [])
    role = list(role or [])
    return {
        "gpu_role": _gpu_role(profile, sizing, modality, role),
        "capacity_band": _capacity_band(profile, sizing, modality, role),
        "availability_class": _availability_class(profile, sizing, modality, role),
        "latency_class": _latency_class(profile, sizing, modality, role),
    }


def derive_for_category(cat):
    """Convenience: pull the tag fields off a category dict and derive. Still pure
    w.r.t. the envelope — it reads only tag keys, never cat['workload_envelope']."""
    return derive_bands(
        hardware_profile=cat.get("hardware_profile"),
        hardware_profile_sizing=cat.get("hardware_profile_sizing"),
        data_modality=cat.get("data_modality"),
        role=cat.get("role"),
    )


if __name__ == "__main__":
    import sys
    from pathlib import Path

    import yaml

    tax = yaml.safe_load(open(Path(__file__).resolve().parents[1] / "data" / "taxonomy.yaml", encoding="utf-8"))
    for c in tax["categories"]:
        b = derive_for_category(c)
        print(f"{c['id']:38s} gpu={b['gpu_role']:13s} cap={b['capacity_band']:20s} "
              f"avail={b['availability_class']:16s} lat={b['latency_class']}")
    sys.exit(0)
