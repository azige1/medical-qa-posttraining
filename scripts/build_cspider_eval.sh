#!/usr/bin/env bash
set -euo pipefail

python src/data/build_cspider_exec_eval.py \
  --cspider_dir project_data/raw/cspider \
  --output_file project_data/eval/cspider_dev_exec_v1.jsonl \
  --report_file project_data/intermediate/cspider_dev_exec_build_report_v1.json
