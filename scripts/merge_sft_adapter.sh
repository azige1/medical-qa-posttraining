#!/usr/bin/env bash
set -euo pipefail

BASE_MODEL="${BASE_MODEL:-/root/autodl-tmp/models/Qwen2.5-3B-Instruct}"
TOKENIZER_PATH="${TOKENIZER_PATH:-$BASE_MODEL}"
LORA_MODEL="${LORA_MODEL:-outputs/sft/qwen25_3b_text2sql_sft_v1}"
OUTPUT_DIR="${OUTPUT_DIR:-outputs/merged/qwen25_3b_text2sql_sft_v1}"

python third_party/MedicalGPT/tools/merge_peft_adapter.py \
  --base_model "$BASE_MODEL" \
  --tokenizer_path "$TOKENIZER_PATH" \
  --lora_model "$LORA_MODEL" \
  --output_dir "$OUTPUT_DIR"
