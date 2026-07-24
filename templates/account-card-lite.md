# Lite Account Card (screening — 10 fields)

> File as `data/accounts/<company>-<facility>.yaml`. Score with `python3 tools/score.py <file>`.
> Full card only at score ≥ 70.

| # | Field | YAML key | Notes |
|---|---|---|---|
| 1 | Company | `company` | Legal/common name |
| 2 | Facility | `facility` | Facility-level, not corporate (§5.2) |
| 3 | Segment | `segment` | One of 8: Hospital/Health System · Diagnostic/Reference Lab · AMC · MedTech/IVD · Biotech/Pharma · CRO · CDMO · Payer |
| 4 | Software domain + vendor | `software` | domain + vendor_ref (id from vendors.yaml) |
| 5 | Deployment model | `deployment` | on-prem / private / hybrid / public / SaaS / managed / OEM / edge |
| 6 | Operator | `operator` | customer-operated / SaaS / CRO-CDMO-run / embedded-in-device → drives GTM motion |
| 7 | Trigger + timing | `trigger` | trigger id from triggers.yaml + window |
| 8 | Infra control | `infra_control` | Y / N / partial — **gate question** |
| 9 | Evidence + confidence | `evidence` | Every claim: source + A/B/C/D |
| 10 | Next step | `next_step` | One concrete action + date |

Plus `scoring:` block — 8 items, 0-5 each (keys in `data/scoring.yaml`).
