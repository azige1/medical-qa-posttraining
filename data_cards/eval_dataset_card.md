# Eval Dataset Card

## Goal

Text-to-SQL 项目采用双主评测：

- 公开 benchmark：`CSpider` 官方 dev
- 自建评测：`sql_eval_dev_v1` / `sql_eval_report_v1`

## Version

- `sql_eval_dev_v1`：100 条中文问题，用于高频调试
- `sql_eval_report_v1`：200 条中文问题，用于最终汇报

## Self-Built Eval Record Format

```json
{
  "id": "sales-001",
  "db_id": "sales",
  "db_path": "project_data/eval/dbs/sales.sqlite",
  "schema_text": "Table customers(id, name, city) ...",
  "question_zh": "统计上海客户的订单数量",
  "gold_sql": "SELECT COUNT(*) ...",
  "tags": ["count", "filter"]
}
```

## Metrics

- `valid_sql_rate`
- `execution_success_rate`
- `execution_accuracy`
- `safe_sql_rate`
- `schema_grounding_rate`
- 人工错误案例分析

## Split Policy

- 官方 `CSpider dev` 只评测，不回流训练
- `sql_eval_dev_v1` 用于高频迭代
- `sql_eval_report_v1` 用于最终结果展示
- 自建评测与训练 prompt 不重合
