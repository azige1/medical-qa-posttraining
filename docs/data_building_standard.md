# 数据构建标准

## 1. 数据层级

项目数据分三层：

1. 原始训练池
   - `CSpider`
   - `Spider`
2. 项目训练数据
   - `sft_train_v1 / sft_val_v1`
   - `dpo_train_v1 / dpo_val_v1`
   - `grpo_train_v1`
3. 固定评测数据
   - `sql_eval_dev_v1`
   - `sql_eval_report_v1`

## 2. SFT 数据标准

SFT 样本统一转成 ShareGPT 格式：

```json
{
  "conversations": [
    {"from": "human", "value": "...prompt..."},
    {"from": "gpt", "value": "SELECT ...;"}
  ]
}
```

要求：

- `human` 侧包含 schema_text 和中文问题
- `gpt` 侧只包含 SQL
- gold SQL 必须能在对应数据库或官方环境中执行

## 3. DPO 数据标准

DPO 样本统一格式：

```json
{
  "conversations": [{"from": "human", "value": "...prompt..."}],
  "chosen": "SELECT ...;",
  "rejected": "SELECT ...;",
  "error_type": "wrong_filter"
}
```

要求：

- `chosen` 执行正确
- `rejected` 的错误原因必须可解释
- preference pair 不与固定评测集重合

## 4. GRPO 数据标准

GRPO 使用 prompt-only 数据，建议字段：

- `id`
- `db_id`
- `db_path`
- `question`
- `answer`

其中：

- `question` 是已经渲染好的完整 prompt
- `answer` 是 gold SQL

这样可以直接适配项目版 GRPO 训练脚本。

## 5. 数据清洗要求

- 删除空 SQL、不可执行 SQL、显然错误的 schema 标注
- 删除多语句样本
- 删除方言差异过大的样本
- 对 SQL 进行基本 canonicalize，减少无意义格式差异

## 6. 泄漏控制

- `CSpider dev` 不回流训练
- `sql_eval_dev_v1 / report_v1` 不参与 SFT / DPO / GRPO 数据构造
- 不允许用最终报告集去“反向召回”训练样本
