# SQL 评测集标注规范

## 1. 目标

`sql_eval_dev_v1` 和 `sql_eval_report_v1` 用于衡量模型是否真的更会“看 schema 写 SQL”，而不是只看训练 loss。

## 2. 每条样本字段

每条样本至少包含：

- `id`
- `db_id`
- `db_path`
- `question_zh`
- `schema_text`
- `gold_sql`
- `difficulty`
- `tags`

## 3. 标注原则

### 3.1 问题要明确

- 问题必须能由当前数据库独立回答
- 避免依赖外部常识

### 3.2 SQL 要唯一可解释

- gold SQL 必须稳定执行
- 尽量避免有多种完全不同却都合理的问法

### 3.3 覆盖核心错误类型

题目要尽量覆盖：

- filter
- aggregation
- group by
- order by / limit
- join
- nested query

### 3.4 难度分层

建议：

- `easy`
- `medium`
- `hard`

## 4. 不建议纳入的题

- 依赖模糊时间表达且无法落地
- 题意本身不完整
- 需要数据库外知识
- 需要写入或修改数据库

## 5. 评测时关注什么

除了最终 execution accuracy，还要观察：

- 是否输出非 SQL 文本
- 是否多语句
- 是否 schema hallucination
- 是否 wrong filter / wrong aggregation / wrong join
