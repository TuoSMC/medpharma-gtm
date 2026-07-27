#!/usr/bin/env python3
"""Generate docs/glossary.md from the canonical glossary block in taxonomy.yaml.

Single source of truth (CLAUDE.md §8): the acronym expansions live in
taxonomy.yaml `glossary:`; this renders the human-facing EN/繁中 table so the two
can never drift. Deterministic — regenerate, don't hand-edit.

Run: python3 tools/glossary_md.py
"""
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
TAX = REPO / "data" / "taxonomy.yaml"
OUT = REPO / "docs" / "glossary.md"


def main():
    gl = yaml.safe_load(TAX.read_text(encoding="utf-8"))["glossary"]
    rows = sorted(gl.items(), key=lambda kv: kv[1]["full_en"].lower())
    L = ["# Glossary — EN / 繁體中文（術語表）", ""]
    L.append(f"> Generated from `data/taxonomy.yaml` `glossary:` block ({len(gl)} terms). "
             "Single source of truth — do not hand-edit; regenerate with `python3 tools/glossary_md.py`.")
    L.append("> Working language: English for data, Traditional Chinese for docs.")
    L.append("")
    L.append("| Acronym / key | English | 繁體中文 |")
    L.append("|---|---|---|")
    for key, v in rows:
        L.append(f"| `{key}` | {v['full_en']} | {v['full_zh']} |")
    L.append("")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"OK: wrote {OUT} ({len(gl)} terms)")


if __name__ == "__main__":
    main()
