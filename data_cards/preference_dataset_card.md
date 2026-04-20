# Preference Dataset Card

## Purpose

用于 `DPO` 训练，强调：

- execution correctness
- schema grounding
- SQL validity
- safe read-only behavior
- 更简洁可复用的 SQL

## Format

```json
{"conversations": [{"from": "human", "value": "根据给定 schema 生成 SQL ..."}], "chosen": "SELECT ...", "rejected": "SELECT ..."}
```

## Build Command

```bash
bash scripts/build_preference_data.sh
```

默认输出：

- `project_data/preference/train/cspider_train_dpo_v1.jsonl`
- `project_data/preference/train/spider_train_dpo_v1.jsonl`
- `project_data/preference/val/cspider_val_dpo_v1.jsonl`
- `project_data/preference/val/spider_val_dpo_v1.jsonl`
- `project_data/intermediate/preference_build_report_v1.json`

## Preference Dimensions

`chosen/rejected` 的判优顺序固定为：

1. 执行结果是否正确
2. schema grounding 是否正确
3. SQL 是否可执行
4. 是否为安全只读查询
5. SQL 是否更简洁可复用

## Rejected Sources

- `Base / SFT` 模型生成但执行错误的 SQL
- 规则扰动 SQL：
  - 错表
  - 错列
  - 错过滤条件
  - 错聚合
  - 错排序 / LIMIT
  - 错 JOIN
- 部分正确但结果不等价的 SQL

## Current V1 Builder

当前 `v1` 先用 rule-based rejected，覆盖以下错误类型：

- `wrong_limit`
- `wrong_order`
- `wrong_filter`
- `missing_filter`
- `wrong_aggregation`
- `distinct_change`
- `wrong_column`
- `wrong_table`
- `schema_hallucination`
- `execution_failure`

## Version History

- `v1`: 主结果 DPO 偏好数据
