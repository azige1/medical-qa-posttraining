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

## Version History

- `v1`: 主结果 DPO 偏好数据
