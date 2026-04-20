# Eval Assets

这里存放项目固定评测集及相关模板。

## 建议文件

- `sql_eval_dev_v1.jsonl`
  - 高频调试集，规模建议 `100`
- `sql_eval_report_v1.jsonl`
  - 最终汇报集，规模建议 `200`
- `sql_eval_dev_v1.template.jsonl`
  - 开发集模板
- `sql_eval_report_v1.template.jsonl`
  - 汇报集模板
- `db_seeds/`
  - 四个自建数据库的 schema.sql 和 CSV seed
- `dbs/`
  - 根据 seed 生成的 SQLite 数据库

## 单条样本字段

- `id`
- `db_id`
- `db_path`
- `question_zh`
- `schema_text`
- `gold_sql`
- `difficulty`
- `tags`

## 约束

- 只用于评测，不用于训练数据召回
- 评测集中的 `db_id` 和 prompt 不应直接回流 DPO pair 构造
- 所有模型必须复用同一版本评测集做主结果对比
