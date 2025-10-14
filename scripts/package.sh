#!/bin/bash

set -euo pipefail

./flexible_grading/ajt_common/package.sh \
	--package "AJT Flexible Grading" \
	--name "AJT Flexible Grading" \
	--root "flexible_grading" \
	"$@"
