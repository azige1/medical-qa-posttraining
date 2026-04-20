#!/usr/bin/env bash
set -euo pipefail

BASE_MODEL="${BASE_MODEL:-Qwen/Qwen2.5-3B-Instruct}"
EVAL_FILE="${EVAL_FILE:-project_data/eval/sql_eval_dev_v1.jsonl}"
TEMPLATE_EVAL_FILE="project_data/eval/sql_eval_dev_v1.template.jsonl"
SYSTEM_PROMPT_FILE="${SYSTEM_PROMPT_FILE:-configs/eval/text2sql_system_prompt.txt}"
GENERATION_CONFIG_FILE="${GENERATION_CONFIG_FILE:-configs/eval/text2sql_generation.json}"
PREDICTION_FILE="${PREDICTION_FILE:-results/predictions/base_qwen25_3b_sql_eval_dev_v1.jsonl}"
REPORT_FILE="${REPORT_FILE:-results/tables/base_qwen25_3b_sql_eval_dev_v1_report.json}"
ERROR_FILE="${ERROR_FILE:-results/case_studies/base_qwen25_3b_sql_eval_dev_v1_errors.jsonl}"

python src/data/build_sqlite_eval_db.py --overwrite

if [ ! -f "$EVAL_FILE" ] && [ -f "$TEMPLATE_EVAL_FILE" ]; then
  EVAL_FILE="$TEMPLATE_EVAL_FILE"
fi

python src/eval/run_text2sql_inference.py \
  --base_model "$BASE_MODEL" \
  --eval_file "$EVAL_FILE" \
  --system_prompt_file "$SYSTEM_PROMPT_FILE" \
  --generation_config_file "$GENERATION_CONFIG_FILE" \
  --output_file "$PREDICTION_FILE"

python src/eval/eval_text2sql_sqlite.py \
  --eval_file "$EVAL_FILE" \
  --prediction_file "$PREDICTION_FILE" \
  --report_file "$REPORT_FILE" \
  --error_file "$ERROR_FILE"
