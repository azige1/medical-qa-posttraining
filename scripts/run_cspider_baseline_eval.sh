#!/usr/bin/env bash
set -euo pipefail

BASE_MODEL="${BASE_MODEL:-Qwen/Qwen2.5-3B-Instruct}"
LORA_MODEL="${LORA_MODEL:-}"
MODEL_TAG="${MODEL_TAG:-base_qwen25_3b}"
EVAL_FILE="${EVAL_FILE:-project_data/eval/cspider_dev_exec_v1.jsonl}"
SYSTEM_PROMPT_FILE="${SYSTEM_PROMPT_FILE:-configs/eval/text2sql_system_prompt.txt}"
GENERATION_CONFIG_FILE="${GENERATION_CONFIG_FILE:-configs/eval/text2sql_generation.json}"
PREDICTION_FILE="${PREDICTION_FILE:-results/predictions/${MODEL_TAG}_cspider_dev_exec_v1.jsonl}"
REPORT_FILE="${REPORT_FILE:-results/tables/${MODEL_TAG}_cspider_dev_exec_v1_report.json}"
ERROR_FILE="${ERROR_FILE:-results/case_studies/${MODEL_TAG}_cspider_dev_exec_v1_errors.jsonl}"
REPORT_TO="${REPORT_TO:-none}"
RUN_NAME="${RUN_NAME:-${MODEL_TAG}_cspider_dev_exec_v1}"

if [ "$REPORT_TO" = "wandb" ] || [ "$REPORT_TO" = "all" ]; then
  export WANDB_PROJECT="${WANDB_PROJECT:-text2sql-posttraining}"
  export WANDB_NAME="${WANDB_NAME:-$RUN_NAME}"
  export WANDB_RUN_ID="${WANDB_RUN_ID:-eval_${RUN_NAME}_$(date +%s)_$RANDOM}"
fi

python src/data/build_cspider_exec_eval.py \
  --cspider_dir project_data/raw/cspider \
  --output_file "$EVAL_FILE" \
  --report_file project_data/intermediate/cspider_dev_exec_build_report_v1.json

EXTRA_MODEL_ARGS=()
if [ -n "$LORA_MODEL" ]; then
  EXTRA_MODEL_ARGS+=(--lora_model "$LORA_MODEL")
fi

python src/eval/run_text2sql_inference.py \
  --base_model "$BASE_MODEL" \
  "${EXTRA_MODEL_ARGS[@]}" \
  --eval_file "$EVAL_FILE" \
  --system_prompt_file "$SYSTEM_PROMPT_FILE" \
  --generation_config_file "$GENERATION_CONFIG_FILE" \
  --output_file "$PREDICTION_FILE" \
  --report_to "$REPORT_TO" \
  --run_name "$RUN_NAME"

python src/eval/eval_text2sql_sqlite.py \
  --eval_file "$EVAL_FILE" \
  --prediction_file "$PREDICTION_FILE" \
  --report_file "$REPORT_FILE" \
  --error_file "$ERROR_FILE" \
  --report_to "$REPORT_TO" \
  --run_name "$RUN_NAME"
