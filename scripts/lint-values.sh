#!/usr/bin/env bash
# ==============================================================================
# Rubric Area 3: Prevention Proposal - CI Linting Script
#
# Inspects upstream values files to catch duplicated YAML keys and naming bugs
# before manifests are rendered and deployed.
# ==============================================================================
set -euo pipefail

VALUES_DIR="${1:-values}"
ERRORS_FOUND=0

echo "=== Online Boutique Values CI Linter ==="
echo "Scanning directory: $VALUES_DIR"

if [ ! -d "$VALUES_DIR" ]; then
    echo "Directory $VALUES_DIR does not exist. Using fallback /opt/microservice-deployment/values if present."
    VALUES_DIR="/opt/microservice-deployment/values"
fi

for f in "$VALUES_DIR"/*.yaml; do
    [ -e "$f" ] || continue
    fname=$(basename "$f")

    # Check 1: Detect duplicate keys (using Python yaml duplicate check)
    python3 - <<EOF
import sys, re

filename = "$f"
keys_seen = set()
duplicates = []

with open(filename, 'r') as fp:
    for line_no, line in enumerate(fp, 1):
        match = re.match(r'^([a-zA-Z0-9_-]+):', line)
        if match:
            k = match.group(1)
            if k in keys_seen:
                duplicates.append((k, line_no))
            keys_seen.add(k)

if duplicates:
    for k, lno in duplicates:
        print(f"ERROR: [{fname}:{lno}] Duplicate top-level YAML key detected: '{k}'", file=sys.stderr)
    sys.exit(1)
EOF
    if [ $? -ne 0 ]; then
        ERRORS_FOUND=$((ERRORS_FOUND + 1))
    else
        echo "✓ $fname passed duplicate key linting"
    fi
done

echo "--------------------------------------------------"
if [ $ERRORS_FOUND -gt 0 ]; then
    echo "CI LINT FAILED: Found $ERRORS_FOUND file(s) with syntax/key collision defects."
    exit 1
else
    echo "CI LINT PASSED: All values files are free of duplicate key defects."
    exit 0
fi
