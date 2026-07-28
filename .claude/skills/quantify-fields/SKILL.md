---
name: quantify-fields
description: >-
  Fill (or refill) the per-category `workload_envelope` — the typical hardware
  demand a medical/pharma software category implies — into data/taxonomy.yaml.
  Use when adding the workload layer, or when a NEW category was added and needs
  its envelope. Derived bands come from a deterministic helper; judgment bands
  and sourced facts are authored per category under §8 (source-or-null, never
  fabricate). Produced by the design-next-step workflow; owner-reviewed and
  adversarially re-verified (survives=True).
---

# quantify-fields — per-category workload envelope

Bridges each software category to concrete SMCI sizing by adding a
`workload_envelope` block (12 keys) to every category in `data/taxonomy.yaml`.
The design + adversarial review that produced this spec are frozen in
[`reference/workload-envelope-spec.json`](reference/workload-envelope-spec.json)
— read it before changing any invariant.

## The one rule that makes it §8-clean

Provenance is **fixed by field identity**, so nothing can be mislabelled:

| class | fields | citation | how it's filled |
|---|---|---|---|
| **derived** | `gpu_role` `capacity_band` `availability_class` `latency_class` | none | `tools/workload_ceiling.py` — a PURE function of tags. `value == derive_bands(tags)` exactly. To raise a value, fix the TAGS, not the envelope. |
| **framework-judgment** | `data_growth` `io_pattern` `concurrency` | none | expert ordinal, same class as `hardware_opportunity(1-4)`. Authored per category with a one-line rationale. `sources=[]`. The helper does NOT compute these. |
| **sourced** | `retention_horizon` `per_unit_data_size` | **required when non-null** | asserts an external fact → real citation in `sources` (A/B for retention, A/B/C for per_unit). `null` wherever no category-wide fact exists — never guess. |

Plus `scaling_driver` (framework prose, the SE discovery question, no digits),
`sources` (citation list), `notes` (prose, no digits).

## Fill recipe (per category)

1. **Read tags**: hardware_profile, hardware_profile_sizing, data_modality, deployment, role, hardware_opportunity, infrastructure_notes.
2. **Derived** = `workload_ceiling.derive_for_category(cat)` — copy the 4 bands verbatim. Deterministic, total (gpu-server ⇒ never `none`).
3. **Judgment** (data_growth, io_pattern, concurrency) = assign the honest enum ordinal for the category's *typical* deployment; one-line rationale in the commit, `sources=[]`.
4. **scaling_driver**: ~12 categories can lift the phrase from an infrastructure_notes `sized by …` clause (delete it from the prose in the same edit); the other ~38 need a freshly authored metric phrase. No digit characters.
5. **retention_horizon**: set a band ONLY where a category-wide legal/standard window genuinely exists (imaging retention statute, GxP/Part 11, HIM chart law) + add an A/B citation to `sources`; else `null`.
6. **per_unit_data_size**: add `{value_low, value_high, unit, confidence:A|B|C, source}` with a REAL citation added to `sources` only where a characteristic citable unit exists (whole-slide image, CT/MR study, NGS run, cryo-EM movie, waveform stream); else `null`.
7. **SaaS-light** (hardware_profile == []): degenerate template — gpu_role `none`, capacity `none`, data_growth `static|low`, availability `best-effort|standard`, per_unit `null`; concurrency assigned honestly (a multi-tenant SaaS-light category may be `massive`).

## Invariants (enforced by tools/tests/test_chain_integrity.py :: TestWorkloadEnvelope)

INV-1..INV-18 — see the spec's `test_invariants`. The load-bearing ones:
`INV-14` (derived == helper exactly; helper is pure over tags; judgment/sourced never mislabelled),
`INV-4/4b` (sourced non-null ⇒ real non-placeholder citation at required confidence),
`INV-15` (no cut scalar keys; `scaling_driver`/`notes` carry no digit character),
`INV-5` GPU crown, `INV-16` flagship non-degenerate.

## Build order (RED → GREEN)

1. enums `workload_*` + `workload_envelope` in REQUIRED_CATEGORY_FIELDS.
2. `tools/workload_ceiling.py` (the shared helper — one source of truth, imported by fill AND test).
3. `TestWorkloadEnvelope` (INV-1..18) → RED.
4. Auto-fill derived + assign judgment for all 58 → structural INVs GREEN.
5. scaling_driver (promote 12 / author 38) → INV-13/15.
6. SaaS-light template → INV-12.
7. Hand-add sourced retention/per_unit + citations → INV-4/4b/14.
8. Bump taxonomy `version: 7` + cosmetic version-string display ONLY — the tool gates already pass (`rollup.py <6`, `drilldown.py <4`); rebuild app + hunting guide; TestToolsSmoke green.
9. CHANGELOG.

## Reusability

Re-running on a newly-added category (#59+) auto-fills its derived bands via the
helper and scaffolds the judgment/sourced keys — so a new category gets an
envelope for the cost of authoring 3 ordinals + any sourced facts.

## Tools

- `tools/workload_ceiling.py` — `derive_bands(*, hardware_profile, hardware_profile_sizing, data_modality, role)` and `derive_for_category(cat)`. Pure, keyword-only, tag-only. Run it standalone to print the derived bands for all categories.
