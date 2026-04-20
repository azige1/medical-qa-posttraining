#!/usr/bin/env bash
set -euo pipefail

python src/data/convert_text2sql_to_sft.py \
  --cspider_dir project_data/raw/cspider \
  --spider_dir project_data/raw/spider \
  --output_root project_data/sft \
  --report_file project_data/intermediate/sft_build_report_v1.json \
  --spider_train_limit 5000 \
  --spider_val_limit 1000
