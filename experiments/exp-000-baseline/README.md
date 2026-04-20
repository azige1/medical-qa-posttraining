# exp-000-baseline

## Goal

建立 base model 在 `CSpider dev` 和自建 SQLite 评测集上的基线表现。

## Base Model

- `Qwen/Qwen2.5-3B-Instruct`

## Data

- eval set 1: `CSpider dev`
- eval set 2: `sql_eval_dev_v1`

## Inference Setup

- temperature: `0.2`
- top_p: `0.9`
- repetition_penalty: `1.05`
- max_new_tokens: `512`
- system prompt version: `configs/eval/text2sql_system_prompt.txt`
- eval protocol: `CSpider dev + sql_eval_dev_v1`

## Command

```bash
# fill actual command here
```

## Results

- cspider_dev_execution_accuracy:
- cspider_dev_valid_sql_rate:
- sql_eval_dev_execution_accuracy:
- sql_eval_dev_execution_success_rate:
- sql_eval_dev_safe_sql_rate:

## Observations

- 

## Next Change

- 
