#!/usr/bin/env bash
# Apply a test file to all branches, commit (single commit via reset --soft), and push.
#
# Usage:
#   GIT_TOKEN=xxx GIT_USER=m0_66826439 \
#   APPLY_FILE=/tmp/test_xxx.py REL_PATH=test/autograd/test_xxx.py \
#   COMMIT_MSG_FILE=/tmp/commit_msg.txt API_SLUG=xxx \
#   bash apply_to_all_branches.sh
#
# Pre-conditions:
#   - 6 repos cloned at $WORK_ROOT/torch-npu-{v2.7.1,v2.9.0,v2.10.0,v2.11.0,v2.12.0,master}
#     (each unshallowed: `git fetch --unshallow origin <branch>`)
#   - git user.email / user.name configured to gitcode-bound identity
#
# Safety: this script PUSHES to the fork. Confirm before running.

set -euo pipefail

: "${GIT_TOKEN:?GIT_TOKEN required}"
: "${GIT_USER:?GIT_USER required}"
: "${APPLY_FILE:?APPLY_FILE (absolute path to the test file) required}"
: "${REL_PATH:?REL_PATH (repo-relative target path, e.g. test/autograd/test_xxx.py) required}"
: "${COMMIT_MSG_FILE:?COMMIT_MSG_FILE required}"
: "${API_SLUG:?API_SLUG (e.g. autograd-profiler-util-kernel-index) required}"

WORK_ROOT="${WORK_ROOT:-/tmp/opencode}"

# base | remote-prefix | repo-dir-suffix
BRANCHES=(
  "v2.7.1|v2.7.1|271"
  "v2.9.0|v2.9.0|290"
  "v2.10.0|v2.10.0|2100"
  "v2.11.0|v2.11.0|2110"
  "v2.12.0|v2.12.0|2120"
  "master|master|master"
)

REMOTE_URL="https://${GIT_USER}:${GIT_TOKEN}@gitcode.com/${GIT_USER}/pytorch.git"

for entry in "${BRANCHES[@]}"; do
  IFS='|' read -r base prefix suffix <<< "$entry"
  # local feature branch uses version WITHOUT 'v' (e.g. 2.7.1); master as-is
  ver="${base#v}"
  feat="test-${API_SLUG}-${ver}"
  remote="${prefix}-test-${API_SLUG}"
  repo="${WORK_ROOT}/torch-npu-${suffix}"

  echo "================ ${repo} (base=${base}) ================"
  cd "$repo"
  git checkout -B "$feat" "origin/${base}"
  mkdir -p "$(dirname "$REL_PATH")"
  cp "$APPLY_FILE" "$REL_PATH"
  git add "$REL_PATH"
  git reset --soft "origin/${base}"
  git commit -F "$COMMIT_MSG_FILE"
  echo "--- force-push ${feat} -> ${remote} ---"
  git push -f "$REMOTE_URL" "${feat}:${remote}"
  cd - > /dev/null
done

echo ""
echo "All 6 branches pushed. Verify with the torch-npu-pr-review skill."
