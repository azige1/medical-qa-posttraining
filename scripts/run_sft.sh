#!/usr/bin/env bash
set -euo pipefail

export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"
shopt -s globstar nullglob

BASE_MODEL="${BASE_MODEL:-Qwen/Qwen2.5-3B-Instruct}"
TRAIN_FILE_DIR="${TRAIN_FILE_DIR:-project_data/sft/train}"
VALIDATION_FILE_DIR="${VALIDATION_FILE_DIR:-project_data/sft/val}"
OUTPUT_DIR="${OUTPUT_DIR:-outputs/sft/qwen25_3b_text2sql_sft_v1}"
REPORT_TO="${REPORT_TO:-tensorboard}"
RUN_NAME="${RUN_NAME:-qwen25_3b_text2sql_sft_v1}"

if [ "$REPORT_TO" = "wandb" ] || [ "$REPORT_TO" = "all" ]; then
  export WANDB_PROJECT="${WANDB_PROJECT:-text2sql-posttraining}"
  export WANDB_NAME="${WANDB_NAME:-$RUN_NAME}"
fi

EXTRA_EVAL_ARGS=()
VALIDATION_FILES=("$VALIDATION_FILE_DIR"/**/*.jsonl)
if [ ${#VALIDATION_FILES[@]} -gt 0 ]; then
  EXTRA_EVAL_ARGS+=(--validation_file_dir "$VALIDATION_FILE_DIR" --do_eval)
fi

python third_party/MedicalGPT/training/supervised_finetuning.py \
  --model_name_or_path "$BASE_MODEL" \
  --template_name qwen \
  --train_file_dir "$TRAIN_FILE_DIR" \
  --per_device_train_batch_size 4 \
  --per_device_eval_batch_size 1 \
  --gradient_accumulation_steps 8 \
  --do_train \
  "${EXTRA_EVAL_ARGS[@]}" \
  --use_peft True \
  --max_train_samples -1 \
  --max_eval_samples 200 \
  --model_max_length 1024 \
  --num_train_epochs 2 \
  --learning_rate 2e-5 \
  --warmup_ratio 0.03 \
  --weight_decay 0.05 \
  --logging_strategy steps \
  --logging_steps 10 \
  --eval_steps 100 \
  --eval_strategy steps \
  --save_steps 200 \
  --save_strategy steps \
  --save_total_limit 3 \
  --preprocessing_num_workers 4 \
  --output_dir "$OUTPUT_DIR" \
  --target_modules all \
  --lora_rank 8 \
  --lora_alpha 16 \
  --lora_dropout 0.05 \
  --torch_dtype bfloat16 \
  --bf16 \
  --report_to "$REPORT_TO" \
  --run_name "$RUN_NAME" \
  --gradient_checkpointing True \
  --cache_dir cache \
  --flash_attn True
