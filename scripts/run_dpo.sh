#!/usr/bin/env bash
set -euo pipefail

export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"
shopt -s globstar nullglob

MODEL_NAME_OR_PATH="${MODEL_NAME_OR_PATH:-outputs/merged/qwen25_3b_text2sql_sft_v1}"
TRAIN_FILE_DIR="${TRAIN_FILE_DIR:-project_data/preference/train}"
VALIDATION_FILE_DIR="${VALIDATION_FILE_DIR:-project_data/preference/val}"
OUTPUT_DIR="${OUTPUT_DIR:-outputs/dpo/qwen25_3b_text2sql_dpo_v1}"

EXTRA_EVAL_ARGS=()
VALIDATION_FILES=("$VALIDATION_FILE_DIR"/**/*.jsonl)
if [ ${#VALIDATION_FILES[@]} -gt 0 ]; then
  EXTRA_EVAL_ARGS+=(--validation_file_dir "$VALIDATION_FILE_DIR" --do_eval)
fi

python third_party/MedicalGPT/training/dpo_training.py \
  --model_name_or_path "$MODEL_NAME_OR_PATH" \
  --template_name qwen \
  --train_file_dir "$TRAIN_FILE_DIR" \
  --per_device_train_batch_size 2 \
  --per_device_eval_batch_size 1 \
  --gradient_accumulation_steps 8 \
  --do_train \
  "${EXTRA_EVAL_ARGS[@]}" \
  --use_peft True \
  --max_train_samples -1 \
  --max_eval_samples 200 \
  --max_steps 600 \
  --eval_steps 100 \
  --save_steps 100 \
  --max_source_length 1024 \
  --max_target_length 512 \
  --beta 0.1 \
  --output_dir "$OUTPUT_DIR" \
  --target_modules all \
  --lora_rank 8 \
  --lora_alpha 16 \
  --lora_dropout 0.05 \
  --torch_dtype bfloat16 \
  --bf16 True \
  --fp16 False \
  --report_to tensorboard \
  --remove_unused_columns False \
  --gradient_checkpointing True \
  --cache_dir cache
