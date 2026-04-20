#!/usr/bin/env bash
set -euo pipefail

python src/data/build_preference_data.py \
  --cspider_dir "${CSPIDER_DIR:-project_data/raw/cspider}" \
  --spider_dir "${SPIDER_DIR:-project_data/raw/spider}" \
  --output_root "${OUTPUT_ROOT:-project_data/preference}" \
  --report_file "${REPORT_FILE:-project_data/intermediate/preference_build_report_v1.json}" \
  --seed "${SEED:-42}" \
  --validation_ratio "${VALIDATION_RATIO:-0.02}" \
  --cspider_train_limit "${CSPIDER_TRAIN_LIMIT:-5000}" \
  --spider_train_limit "${SPIDER_TRAIN_LIMIT:-2000}"
