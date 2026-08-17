#!/usr/bin/env bash
# One build — regenerate every derived artifact in dependency order, then prove it (plan-v6.1 #6).
# Routine build from committed data. (Adding vendors is a separate authoring step:
# tools/build_vendors_provisional.py from private/vendor-drafts-ready.yaml.)
set -euo pipefail
cd "$(dirname "$0")"
echo "==> build_index"          && python3 tools/build_index.py
echo "==> build_sub_vendor_fk"  && python3 tools/build_sub_vendor_fk.py
echo "==> migrate_intel"        && python3 tools/migrate_intel_vendor_id.py
echo "==> build_app"            && python3 tools/build_app.py >/dev/null
cmp app/index.html docs/index.html && echo "==> app==docs OK"
if [ "${1:-}" = "--test" ]; then echo "==> pytest" && python3 -m pytest tools/tests/test_chain_integrity.py -q; fi
echo "BUILD OK"
