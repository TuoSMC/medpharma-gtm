#!/usr/bin/env python3
"""Shared data loader (plan-v6.1 E5 / B-Load bridge).

Plain YAML load with a clear error — NO cache, NO MD5 layer. For a one-person static map a
re-read is cheap, and a silently-stale cache is the real liability (brain #4: silent success and
silent death look identical). So: load, and fail loudly if the file is missing.

Relative names resolve under /data; absolute paths pass through.
"""
from pathlib import Path

import yaml

DATA = Path(__file__).resolve().parent.parent.parent / "data"


def load_yaml(path):
    p = Path(path)
    if not p.is_absolute():
        p = DATA / p
    if not p.exists():
        raise FileNotFoundError(f"data file not found: {p}  (relative names resolve under {DATA})")
    return yaml.safe_load(p.read_text(encoding="utf-8"))
