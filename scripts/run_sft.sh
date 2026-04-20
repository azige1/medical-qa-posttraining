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
TRAIN_BATCH_SIZE="${TRAIN_BATCH_SIZE:-8}"
EVAL_BATCH_SIZE="${EVAL_BATCH_SIZE:-2}"
GRADIENT_ACCUMULATION_STEPS="${GRADIENT_ACCUMULATION_STEPS:-4}"
MODEL_MAX_LENGTH="${MODEL_MAX_LENGTH:-1024}"
NUM_TRAIN_EPOCHS="${NUM_TRAIN_EPOCHS:-2}"
LEARNING_RATE="${LEARNING_RATE:-2e-5}"
LOGGING_STEPS="${LOGGING_STEPS:-20}"
EVAL_STEPS="${EVAL_STEPS:-200}"
SAVE_STEPS="${SAVE_STEPS:-400}"
PREPROCESSING_NUM_WORKERS="${PREPROCESSING_NUM_WORKERS:-8}"
DATALOADER_NUM_WORKERS="${DATALOADER_NUM_WORKERS:-4}"
GRADIENT_CHECKPOINTING="${GRADIENT_CHECKPOINTING:-True}"

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
  --per_device_train_batch_size "$TRAIN_BATCH_SIZE" \
  --per_device_eval_batch_size "$EVAL_BATCH_SIZE" \
  --gradient_accumulation_steps "$GRADIENT_ACCUMULATION_STEPS" \
  --do_train \
  "${EXTRA_EVAL_ARGS[@]}" \
  --use_peft True \
  --max_train_samples -1 \
  --max_eval_samples 200 \
  --model_max_length "$MODEL_MAX_LENGTH" \
  --num_train_epochs "$NUM_TRAIN_EPOCHS" \
  --learning_rate "$LEARNING_RATE" \
  --warmup_ratio 0.03 \
  --weight_decay 0.05 \
  --logging_strategy steps \
  --logging_steps "$LOGGING_STEPS" \
  --eval_steps "$EVAL_STEPS" \
  --eval_strategy steps \
  --save_steps "$SAVE_STEPS" \
  --save_strategy steps \
  --save_total_limit 3 \
  --preprocessing_num_workers "$PREPROCESSING_NUM_WORKERS" \
  --dataloader_num_workers "$DATALOADER_NUM_WORKERS" \
  --output_dir "$OUTPUT_DIR" \
  --target_modules all \
  --lora_rank 8 \
  --lora_alpha 16 \
  --lora_dropout 0.05 \
  --torch_dtype bfloat16 \
  --bf16 \
  --report_to "$REPORT_TO" \
  --run_name "$RUN_NAME" \
  --gradient_checkpointing "$GRADIENT_CHECKPOINTING" \
  --cache_dir cache \
  --flash_attn True
