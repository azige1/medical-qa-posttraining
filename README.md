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
- Workflow: 先完整学知识，再做项目

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

## Stage Plan

当前执行顺序固定为：

1. 先学完整后训练知识链路
2. 再锁项目定义和双主评测基线
3. 再做 SFT 与 DPO 正式实验
4. 最后补 RM + RLOO/PPO 小实验与项目包装

完整阶段计划见：

- [`docs/stage_plan.md`](docs/stage_plan.md)
- [`docs/roadmap.md`](docs/roadmap.md)

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
  third_party/
```

## Included Framework Code

为了先把项目做起来，当前仓库内已经包含一份 MedicalGPT 框架代码镜像，位置在：

- [third_party/MedicalGPT](E:/MedicalGPT/MedicalGPT/medical-qa-posttraining/third_party/MedicalGPT)

这样做的目的很直接：

- 先保证训练代码、脚本和数据格式工具都在同一个仓库里
- 方便后续直接修改和记录项目过程
- 等项目跑通后，再决定是否精简为“项目代码 + 外部框架依赖”的形态

当前约定：

- `third_party/MedicalGPT/`：框架源码和原始脚本
- 仓库根目录的 `docs/`、`data_cards/`、`experiments/`、`results/`：你的项目过程、实验结果和表达材料

## Current Status

- [ ] 完成第一阶段：SFT 知识打底
- [ ] 完成第二阶段：偏好学习与在线 RL 知识主线
- [ ] 完成第三阶段：GRPO 与统一方法论收束
- [ ] 完成第四阶段：项目定义与评测基线
- [ ] 完成第五阶段：SFT 数据构建与 SFT 正式实验
- [ ] 完成第六阶段：DPO 主结果 + RM/RLOO/PPO 小实验
- [ ] 完成第七阶段：结果包装与面试表达

## Planned Metrics

第一版重点记录以下指标：

- `structure_pass_rate`
- `instruction_follow_rate`
- `must_include_hit_rate`
- `forbidden_violation_rate`
- `triage_match_rate`
- 人工误差分析结论

当前固定采用双主评测：

- 公开 benchmark 主评测：`C-Eval` 医学子集
- 任务对齐主评测：自建结构化医疗评测集

如果后续接入 `lm-evaluation-harness`，再补标准 benchmark 运行链路。

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
- 基于 `Qwen3.5-2B` 完成 SFT 与 DPO 训练，并建立双主评测体系进行对比
- 使用通用评估与领域评估结合的方法验证模型提升，并完成误差分析

## Next Step

1. 完成第一阶段：SFT 知识打底
2. 输出 SFT 数据流图、方法卡和面试答题卡
3. 进入 RM / RLOO / PPO / DPO / ORPO 学习阶段
