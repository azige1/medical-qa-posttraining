# Preference Dataset Card

## Purpose

用于 DPO 训练，强调：

- 医疗正确性
- 结构化输出规范
- 指令遵循
- 减少幻觉

## Format

```json
{"conversations": [{"from": "human", "value": "..."}], "chosen": "...", "rejected": "..."}
```

## Preference Dimensions

- chosen 是否更准确
- chosen 是否更完整
- chosen 是否更符合 JSON schema
- rejected 是否存在幻觉或危险表述

## Version History

- `v0`: placeholder
