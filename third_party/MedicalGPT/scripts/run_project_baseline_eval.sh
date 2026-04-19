python tools/run_project_inference.py \
  --base_model Qwen/Qwen3.5-2B \
  --eval_file project_data/eval/medical_eval_sample.jsonl \
  --system_prompt_file project_data/eval/structured_output_system_prompt.txt \
  --output_file results/baseline/qwen35_2b_predictions.jsonl \
  --eval_batch_size 4 \
  --max_new_tokens 384

python tools/eval_medical_project.py \
  --eval_file project_data/eval/medical_eval_sample.jsonl \
  --prediction_file results/baseline/qwen35_2b_predictions.jsonl \
  --report_file results/baseline/qwen35_2b_report.json \
  --error_file results/baseline/qwen35_2b_errors.jsonl
