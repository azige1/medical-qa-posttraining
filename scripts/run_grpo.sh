#!/usr/bin/env bash
set -euo pipefail

export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"
shopt -s globstar nullglob

MODEL_NAME_OR_PATH="${MODEL_NAME_OR_PATH:-outputs/merged/qwen25_3b_text2sql_sft_v1}"
TRAIN_FILE_DIR="${TRAIN_FILE_DIR:-project_data/grpo/train}"
VALIDATION_FILE_DIR="${VALIDATION_FILE_DIR:-project_data/grpo/val}"
OUTPUT_DIR="${OUTPUT_DIR:-outputs/grpo/qwen25_3b_text2sql_grpo_v1}"
REPORT_TO="${REPORT_TO:-tensorboard}"
RUN_NAME="${RUN_NAME:-qwen25_3b_text2sql_grpo_v1}"

if [ "$REPORT_TO" = "wandb" ] || [ "$REPORT_TO" = "all" ]; then
  export WANDB_PROJECT="${WANDB_PROJECT:-text2sql-posttraining}"
  export WANDB_NAME="${WANDB_NAME:-$RUN_NAME}"
fi

EXTRA_VAL_ARGS=()
VALIDATION_FILES=("$VALIDATION_FILE_DIR"/**/*.jsonl)
if [ ${#VALIDATION_FILES[@]} -gt 0 ]; then
  EXTRA_VAL_ARGS+=(--validation_file_dir "$VALIDATION_FILE_DIR")
fi

python src/train/grpo_text2sql.py \
  --model_name_or_path "$MODEL_NAME_OR_PATH" \
  --train_file_dir "$TRAIN_FILE_DIR" \
  "${EXTRA_VAL_ARGS[@]}" \
  --reward_config_file configs/eval/grpo_reward_weights.json \
  --system_prompt_file configs/eval/text2sql_system_prompt.txt \
  --output_dir "$OUTPUT_DIR" \
  --bf16 True \
  --use_peft True \
  --lora_target_modules all \
  --lora_r 16 \
  --lora_alpha 32 \
  --lora_dropout 0.05 \
  --learning_rate 5e-7 \
  --lr_scheduler_type cosine \
  --warmup_ratio 0.03 \
  --per_device_train_batch_size 2 \
  --gradient_accumulation_steps 1 \
  --num_generations 4 \
  --max_completion_length 256 \
  --logging_steps 10 \
  --save_steps 50 \
  --save_strategy steps \
  --save_total_limit 3 \
  --report_to "$REPORT_TO" \
  --run_name "$RUN_NAME"
