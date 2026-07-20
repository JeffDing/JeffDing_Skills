#!/usr/bin/env bash
# Run flake8 using the torch-npu project config (max-line-length=120, E501 ignored).
# Default flake8 (79 chars) WILL false-positive E501 — always use this.
#
# Usage:
#   bash check_flake8.sh /path/to/torch-npu-repo file1.py file2.py ...

set -euo pipefail

REPO="${1:?usage: check_flake8.sh <torch-npu-repo-root> <file...>}"
shift

[[ -f "$REPO/.flake8" ]] || { echo "ERROR: $REPO/.flake8 not found" >&2; exit 1; }

echo "Using config: $REPO/.flake8"
echo "Checking: $*"
echo ""

python3 -m flake8 --config="$REPO/.flake8" "$@"
echo "✅ flake8 clean under project config"
