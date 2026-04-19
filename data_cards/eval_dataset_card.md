# Eval Dataset Card

## Goal

评测采用双主评测设计：

- 公开 benchmark 主评测：`C-Eval` 医学子集
- 任务对齐主评测：固定的结构化医疗评测集

后者用于比较：

- base model
- SFT
- DPO
- RM + RLOO/PPO 小实验

## Metrics

- `structure_pass_rate`
- `must_include_hit_rate`
- `forbidden_violation_rate`
- `triage_match_rate`
- 人工案例分析

补充说明：

- `C-Eval` 主要看医学相关子集准确率
- 自建评测集主要看结构化输出质量和任务目标对齐

## Split Policy

- 固定小规模 eval set
- 不参与训练
- 每轮实验都复用同一批样本
- 不直接用最终 `C-Eval` 题目做训练数据召回
