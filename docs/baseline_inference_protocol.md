# Baseline 推理协议

## 1. 目标

在任何训练开始前，先对 base model 跑一版统一 baseline，作为后续 `SFT / DPO / GRPO` 的对照基线。

第一版 baseline 分两条评测线：

- 自建 `sql_eval_dev_v1`
- 官方 `CSpider dev`

## 2. Baseline 定义

- 模型固定：`Qwen/Qwen2.5-3B-Instruct`
- 不使用 base-only checkpoint 作为主 baseline
- 所有后续模型都必须沿用同一套 prompt 与 decoding 配置做主结果对比

## 3. 固定输入

### 3.1 自建评测

- eval set：`project_data/eval/sql_eval_dev_v1.jsonl`
- system prompt：`configs/eval/text2sql_system_prompt.txt`
- generation config：`configs/eval/text2sql_generation.json`

### 3.2 官方 benchmark

- `CSpider` 官方 dev
- 评测优先使用官方脚本，不通过 `lm-evaluation-harness`

## 4. 固定 decoding 参数

- `temperature = 0.2`
- `top_p = 0.9`
- `max_new_tokens = 256`
- `repetition_penalty = 1.0`
- `eval_batch_size = 4`

这些参数一旦用于主结果，就不能和后续模型结果混用不同配置。

## 5. 输出要求

- 只输出 SQL
- 不输出解释
- 不输出 Markdown 代码块
- 所有模型必须在同一批样本上评测

## 6. 建议命名

- predictions:
  - `results/predictions/base_qwen25_3b_sql_eval_dev_v1.jsonl`
- report:
  - `results/tables/base_qwen25_3b_sql_eval_dev_v1_report.json`
- errors:
  - `results/case_studies/base_qwen25_3b_sql_eval_dev_v1_errors.jsonl`

## 7. 推荐命令

项目根目录直接运行：

```bash
bash scripts/run_baseline_eval.sh
```

等价命令形态固定为：

```bash
python src/eval/run_text2sql_inference.py \
  --base_model Qwen/Qwen2.5-3B-Instruct \
  --eval_file project_data/eval/sql_eval_dev_v1.jsonl \
  --system_prompt_file configs/eval/text2sql_system_prompt.txt \
  --generation_config_file configs/eval/text2sql_generation.json \
  --output_file results/predictions/base_qwen25_3b_sql_eval_dev_v1.jsonl

python src/eval/eval_text2sql_sqlite.py \
  --eval_file project_data/eval/sql_eval_dev_v1.jsonl \
  --prediction_file results/predictions/base_qwen25_3b_sql_eval_dev_v1.jsonl \
  --report_file results/tables/base_qwen25_3b_sql_eval_dev_v1_report.json \
  --error_file results/case_studies/base_qwen25_3b_sql_eval_dev_v1_errors.jsonl
```

## 8. 结果记录

baseline 跑完后，至少记录：

- 模型版本
- prompt 版本
- decoding 参数
- `valid_sql_rate`
- `safe_sql_rate`
- `execution_success_rate`
- `execution_accuracy`
- `schema_grounding_rate`
- 错误类型分布
