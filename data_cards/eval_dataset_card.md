# Eval Dataset Card

## Goal

固定一批评测样本，用于比较：

- base model
- SFT
- DPO

## Metrics

- `structure_pass_rate`
- `must_include_hit_rate`
- `forbidden_violation_rate`
- `triage_match_rate`
- 人工案例分析

## Split Policy

- 固定小规模 eval set
- 不参与训练
- 每轮实验都复用同一批样本
