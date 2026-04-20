#!/usr/bin/env bash
set -euo pipefail

MODE="${MODE:-dual}"
BASE_MODEL="${BASE_MODEL:-/root/autodl-tmp/models/Qwen2.5-3B-Instruct}"
LORA_MODEL="${LORA_MODEL:-}"
MODEL_TAG="${MODEL_TAG:-base_qwen25_3b}"
REPORT_TO="${REPORT_TO:-wandb}"
WANDB_PROJECT="${WANDB_PROJECT:-text2sql-posttraining}"
HF_ENDPOINT="${HF_ENDPOINT:-https://hf-mirror.com}"
HF_HOME="${HF_HOME:-/root/autodl-tmp/hf-home}"
HUGGINGFACE_HUB_CACHE="${HUGGINGFACE_HUB_CACHE:-/root/autodl-tmp/hf-cache}"
TRANSFORMERS_CACHE="${TRANSFORMERS_CACHE:-/root/autodl-tmp/transformers-cache}"
OMP_NUM_THREADS="${OMP_NUM_THREADS:-8}"
MKL_NUM_THREADS="${MKL_NUM_THREADS:-8}"

echo "[baseline_all] MODE=$MODE"
echo "[baseline_all] BASE_MODEL=$BASE_MODEL"
echo "[baseline_all] LORA_MODEL=${LORA_MODEL:-<none>}"
echo "[baseline_all] MODEL_TAG=$MODEL_TAG"
echo "[baseline_all] REPORT_TO=$REPORT_TO"

mkdir -p logs cache
mkdir -p "$HF_HOME" "$HUGGINGFACE_HUB_CACHE" "$TRANSFORMERS_CACHE"

export HF_ENDPOINT
export HF_HUB_ENABLE_HF_TRANSFER=0
export HF_HUB_DISABLE_TELEMETRY=1
export HF_HUB_DISABLE_XET=1
export HF_HOME
export HUGGINGFACE_HUB_CACHE
export TRANSFORMERS_CACHE
export OMP_NUM_THREADS
export MKL_NUM_THREADS

run_self_eval() {
  REPORT_TO="$REPORT_TO" \
  WANDB_PROJECT="$WANDB_PROJECT" \
  MODEL_TAG="$MODEL_TAG" \
  LORA_MODEL="$LORA_MODEL" \
  RUN_NAME="${RUN_NAME_SELF:-qwen25_3b_sql_eval_dev_v1}" \
  BASE_MODEL="$BASE_MODEL" \
  bash scripts/run_baseline_eval.sh | tee "logs/${RUN_NAME_SELF:-qwen25_3b_sql_eval_dev_v1}.log"
}

run_cspider_eval() {
  REPORT_TO="$REPORT_TO" \
  WANDB_PROJECT="$WANDB_PROJECT" \
  MODEL_TAG="$MODEL_TAG" \
  LORA_MODEL="$LORA_MODEL" \
  RUN_NAME="${RUN_NAME_CSPIDER:-qwen25_3b_cspider_dev_exec_v1}" \
  BASE_MODEL="$BASE_MODEL" \
  bash scripts/run_cspider_baseline_eval.sh | tee "logs/${RUN_NAME_CSPIDER:-qwen25_3b_cspider_dev_exec_v1}.log"
}

case "$MODE" in
  self)
    run_self_eval
    ;;
  cspider)
    run_cspider_eval
    ;;
  dual)
    run_cspider_eval
    run_self_eval
    ;;
  *)
    echo "Unsupported MODE: $MODE"
    echo "Use one of: self, cspider, dual"
    exit 1
    ;;
esac
