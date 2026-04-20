#!/usr/bin/env bash
set -euo pipefail

MODEL_NAME_OR_PATH="${MODEL_NAME_OR_PATH:-/root/medical-qa-posttraining/outputs/merged/qwen25_3b_text2sql_sft_v1}"
REPORT_TO="${REPORT_TO:-wandb}"
WANDB_PROJECT="${WANDB_PROJECT:-text2sql-posttraining}"
RUN_NAME="${RUN_NAME:-qwen25_3b_grpo_v1}"
HF_ENDPOINT="${HF_ENDPOINT:-https://hf-mirror.com}"
HF_HOME="${HF_HOME:-/root/autodl-tmp/hf-home}"
HUGGINGFACE_HUB_CACHE="${HUGGINGFACE_HUB_CACHE:-/root/autodl-tmp/hf-cache}"
TRANSFORMERS_CACHE="${TRANSFORMERS_CACHE:-/root/autodl-tmp/transformers-cache}"
OMP_NUM_THREADS="${OMP_NUM_THREADS:-8}"
MKL_NUM_THREADS="${MKL_NUM_THREADS:-8}"
LOG_FILE="${LOG_FILE:-logs/${RUN_NAME}.log}"

mkdir -p logs cache
mkdir -p "$HF_HOME" "$HUGGINGFACE_HUB_CACHE" "$TRANSFORMERS_CACHE"

export MODEL_NAME_OR_PATH
export REPORT_TO
export WANDB_PROJECT
export RUN_NAME
export HF_ENDPOINT
export HF_HUB_ENABLE_HF_TRANSFER=0
export HF_HUB_DISABLE_TELEMETRY=1
export HF_HUB_DISABLE_XET=1
export HF_HOME
export HUGGINGFACE_HUB_CACHE
export TRANSFORMERS_CACHE
export OMP_NUM_THREADS
export MKL_NUM_THREADS

bash scripts/run_grpo.sh 2>&1 | tee "$LOG_FILE"
