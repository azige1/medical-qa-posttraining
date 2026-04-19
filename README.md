# Medical QA Post-Training

一个基于 MedicalGPT 训练链路搭建的医疗大模型后训练项目，用于展示完整的：

- 数据构建
- SFT / DPO 训练
- 通用评估与领域评估
- 实验记录与误差分析
- 面试与简历项目包装

当前项目默认路线：

- Base Model: `Qwen/Qwen3.5-2B`
- Hardware: `AutoDL 4090 24G`
- Mainline: `SFT + DPO`
- Target capability: 医疗问答 + 结构化输出

## Why This Repo Exists

这个仓库不是为了维护 MedicalGPT 框架本身，而是为了把基于 MedicalGPT 做的完整项目过程沉淀下来。  
核心目标不是“跑了脚本”，而是形成一个能讲清楚的数据、训练、评估闭环。

项目的训练底座来自：

- [MedicalGPT](https://github.com/shibing624/MedicalGPT)

## Project Goal

围绕“医疗问答 + 结构化输出”能力，构建一个完整的后训练项目：

1. 从原始医疗数据出发，构造 SFT 数据与偏好数据
2. 基于 `Qwen3.5-2B` 完成 SFT 和 DPO 训练
3. 建立固定评测集，对比 baseline / SFT / DPO
4. 记录实验结果、误差案例、方法取舍与面试表达

## Training Pipeline

```text
Raw data
  -> cleaned / normalized data
  -> ShareGPT SFT data
  -> chosen/rejected preference data
  -> SFT
  -> DPO
  -> evaluation
  -> error analysis
  -> resume/interview packaging
```

## Repository Layout

```text
medical-qa-posttraining/
  README.md
  .gitignore
  docs/
  data_cards/
  configs/
  experiments/
  results/
  src/
  references/
```

## Current Status

- [ ] 锁定最终原始数据源
- [ ] 完成第一版 SFT 数据
- [ ] 完成 baseline 固定评测
- [ ] 完成第一版 SFT 训练
- [ ] 完成第一版 DPO 训练
- [ ] 完成标准化评估和领域评估
- [ ] 完成项目结果包装

## Planned Metrics

第一版重点记录以下指标：

- `structure_pass_rate`
- `instruction_follow_rate`
- `must_include_hit_rate`
- `forbidden_violation_rate`
- `triage_match_rate`
- 人工误差分析结论

如果后续接入 `lm-evaluation-harness`，再补：

- 通用 benchmark 结果
- baseline / SFT / DPO 对比表

## Structured Output Schema

第一版回答固定为 JSON：

```json
{
  "question_type": "definition | diagnosis | treatment | medication | examination | prevention | other",
  "answer": "直接回答",
  "key_points": ["关键点1", "关键点2"],
  "triage_level": "low | medium | high",
  "safety_notice": "风险提示与就医建议"
}
```

## Experiment Log

所有实验都应记录在 `experiments/` 下，至少包括：

- 目标
- 数据版本
- 模型版本
- 训练参数
- 运行命令
- 核心指标
- 失败点
- 下一轮改动

## Resume Angle

这个项目最终希望能支持以下表述：

- 基于 MedicalGPT 训练框架，完成医疗问答场景下的大模型后训练项目
- 构建了面向结构化输出的 SFT 数据与 preference 数据
- 基于 `Qwen3.5-2B` 完成 SFT 与 DPO 训练，并建立固定评测集进行对比
- 使用通用评估与领域评估结合的方法验证模型提升，并完成误差分析

## Next Step

1. 确定 raw data 来源和版本
2. 固定评测集
3. 跑 baseline
4. 构造第一版 SFT 数据
5. 开始第一版 SFT 训练
