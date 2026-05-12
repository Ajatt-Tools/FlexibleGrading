#!/bin/bash

set -euo pipefail

readonly ROOT_DIR=$(git rev-parse --show-toplevel)

"$ROOT_DIR/flexible_grading/ajt_common/format.sh" \
	--include flexible_grading \
	--include tests \
	--exclude flexible_grading/ajt_common
