#!/bin/sh

cd -- "$(git rev-parse --show-toplevel)" &&
	git archive HEAD --format=zip -o flexible_grading.ankiaddon
