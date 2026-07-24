# Full Account Card (score ≥ 70 only)

Extends lite card. Additional YAML sections:

## `business` — workflow + KPI + pain
- `workflow`: the business workflow the software serves
- `kpi`: what the customer measures
- `pain_point`: current bottleneck

## `workload` — quantified profile (all §3 fields)
| Key | Unit |
|---|---|
| `data_per_day` | GB/TB per day |
| `total_capacity` | TB/PB |
| `growth_pct` | % per year |
| `retention` | years + policy |
| `gpu_type_qty` | model + count |
| `train_vs_inference` | ratio or dominant mode |
| `iops` | required IOPS |
| `throughput` | GB/s |
| `latency` | ms target |
| `concurrency` | concurrent users/jobs |
| `rto_rpo` | hours / minutes |
| `platform` | bare-metal / VM / K8s / HPC |

`hw_pull_rollup`: 1-4 summary rating (legacy v1 rollup only)

## `regulatory` — cross-cutting flags
`phi` / `gxp` / `part11` / `samd` — booleans + notes.
If regulated: note doc deliverables needed (controlled BOM, firmware matrix, change notification, lifecycle statement, hardening guide).

## `buying_committee` — 6 roles
Business Owner · Application Owner · Infrastructure Owner · Data/AI Owner · Risk Approver · Economic Buyer
Each: name/title, entry point, stance, sales-cycle note.

## `hypothesis`
- `hardware`: proposed BOM sketch
- `reference_architecture`: link or description
- `competitive_position`: incumbents + our angle
- `estimated_value`: $ range
- `poc_success_criteria`: measurable exit criteria
