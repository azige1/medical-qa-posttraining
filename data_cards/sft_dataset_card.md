# SFT Dataset Card

## Purpose

用于训练：

- 中文问题 + schema -> 纯 SQL

第一版只优化 SQL 生成，不输出解释，不做 JSON 混合输出。

## Format

```json
{"conversations": [{"from": "human", "value": "根据给定 schema 生成 SQL ..."}, {"from": "gpt", "value": "SELECT ..."}]}
```

## Data Construction Notes

- 原始来源：
  - `CSpider`
  - `Spider`
- 清洗规则：
  - 移除非 SQLite 兼容 SQL
  - 统一大小写和空白格式
  - 去掉明显不可执行或损坏样本
- 重写策略：
  - 把 question 与 schema 拼成统一 prompt
  - assistant 只输出 SQL
- 输出模板：
  - 纯 SQL
  - 只允许 `SELECT`

## Scope

优先保留：

- 单表查询
- 多表 join
- group by / aggregation
- order by / limit
- nested query

优先删除：

- 需要多语句 SQL 的样本
- SQLite 方言难以兼容的样本
- 解析明显异常的 SQL

## Version History

- `v1`: `CSpider + Spider` 的第一版 ShareGPT SQL 训练集
