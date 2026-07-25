# Six-Layer Chain Refinement Plan

> Pipeline: layer-by-layer refinement of
> `segment → software category → hardware_buyer → hardware_opportunity → hardware_profile → play`
> driven by three disciplines (test-driven-development · grill-me · superpowers) and two
> external reviewers (codex on this repository · grok on a dedicated worktree).
> Refinement agents run on opus / high reasoning effort.

## Cross-cutting requirements (from Tuo, 2026-07-24)
1. **No abbreviations anywhere** — every abbreviated field name and enum value gets written out in full. (Scope for category ids: pending grill decision D1.)
2. **Everything classifiable gets classified** — cluster headers are currently comments, must become a real `domain` field; triggers/scoring/plays audited for missing classification.
3. **Better models for refinement** — all refinement/verify agents run opus, high effort minimum.

## Method per layer
1. **RED** — failing test in `tools/tests/` encoding the layer's invariants
2. **Refine** — opus agents fix data until invariants hold
3. **GREEN** — tests pass, checkpoint commit
4. **External review** — codex (this repo) + grok (worktree `../medical-software-review`)
5. **Action findings** — accepted fixes re-enter at step 1

## Layer inventory and known weak points
| # | Layer | Known weak points to interrogate |
|---|---|---|
| 1 | segments (8) | payer thin (3 categories); no per-category primary segment |
| 2 | software category (53) | domain only in comments; evidence_note all null; vendors empty |
| 3 | hardware_buyer | icu oem-primary is a domain call; operator tags from single workflow pass |
| 4 | hardware_opportunity (per buyer) | headline < per-buyer max in 10 categories (kept intentionally?) |
| 5 | hardware_profile | high-memory only 2 uses; 8 empty profiles; no per-component sizing |
| 6 | plays (3) | 28 categories carry no play; play scope fixed by §5.1 |

## Test suite skeleton (tools/tests/test_chain_integrity.py)
- schema: every category carries every required field; enums closed
- naming: no abbreviated enum values (per D1 scope); field names full words
- classification: every category has `domain` from a closed domain enum
- layer 3: primary_buyer ∈ hardware_buyer; supermicro_reachable consistency
- layer 4: hardware_opportunity_by_buyer keys == non-hyperscaler buyers; headline == max(per-buyer) OR explicitly waived
- layer 5: hardware_profile ⊆ component enum; flagship (4) categories non-empty profile
- layer 6: plays ⊆ {play-a, play-b, play-c}; play targets consistent with segments

## Decisions log
- **D1 (locked, Tuo 2026-07-24): ids stay compact; every category gains a `name_full` field carrying the complete, zero-abbreviation full name; enum values and field names expand.**
  - Expansion rule for enum values: expand lazy abbreviations (cro, cdmo, RWD, infra, on-prem, SaaS, oem, dr, ha, SaMD…); keep only universally-recognized spec/product acronyms that are themselves professional vocabulary (GPU, CPU, NVMe) — and even those get written out in a canonical `glossary` block (enum value → full English + Traditional Chinese) inside taxonomy.yaml, so every acronym is expanded somewhere authoritative.
- D2 (derived): headline `hardware_opportunity` must equal max(hardware_opportunity_by_buyer) — the 10 categories where headline < per-buyer max are stale rollups to fix.
- D3 (derived): the seven cluster comment headers become a required `domain` field with a closed enum.
