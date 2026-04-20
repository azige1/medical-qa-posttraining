#!/usr/bin/env bash
set -euo pipefail

MODE="${MODE:-dual}"
BASE_MODEL="${BASE_MODEL:-/root/autodl-tmp/models/Qwen2.5-3B-Instruct}"
LORA_MODEL="${LORA_MODEL:-outputs/sft/qwen25_3b_text2sql_sft_v1}"
MODEL_TAG="${MODEL_TAG:-sft_qwen25_3b}"
REPORT_TO="${REPORT_TO:-wandb}"
WANDB_PROJECT="${WANDB_PROJECT:-text2sql-posttraining}"

RUN_NAME_SELF="${RUN_NAME_SELF:-${MODEL_TAG}_sql_eval_dev_v1}"
RUN_NAME_CSPIDER="${RUN_NAME_CSPIDER:-${MODEL_TAG}_cspider_dev_exec_v1}"

MODE="$MODE" \
BASE_MODEL="$BASE_MODEL" \
LORA_MODEL="$LORA_MODEL" \
MODEL_TAG="$MODEL_TAG" \
REPORT_TO="$REPORT_TO" \
WANDB_PROJECT="$WANDB_PROJECT" \
RUN_NAME_SELF="$RUN_NAME_SELF" \
RUN_NAME_CSPIDER="$RUN_NAME_CSPIDER" \
bash scripts/run_baseline_all.sh
