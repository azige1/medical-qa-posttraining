# Chinese Text-to-SQL Post-Training

一个基于 MedicalGPT 训练脚手架搭建的中文 Text-to-SQL / 数据分析问答后训练项目，用于展示完整的：

- 数据构建
- SFT / DPO / GRPO 训练
- 公开 benchmark 与自建评测
- 实验记录与错误分析
- 简历与面试项目包装

当前项目默认路线：

- Base Model: `Qwen/Qwen2.5-3B-Instruct`
- Hardware: `AutoDL 4090 24G`
- Mainline: `SFT + DPO`
- Expansion: `GRPO`
- Stretch: `RM + RLOO/PPO mini`
- Target capability: 中文问题 + 数据库 schema -> 纯 SQL

## Why This Repo Exists

这个仓库不是为了维护 MedicalGPT 框架本身，而是为了把一个**可执行、可评测、可写进简历**的 Text-to-SQL 后训练项目沉淀下来。  
框架只负责训练入口，项目真正的核心在于：

- 任务定义
- 数据构造
- DPO / GRPO 设计
- benchmark 与自建评测闭环

训练底座来自：

- [MedicalGPT](https://github.com/shibing624/MedicalGPT)

## Project Goal

围绕“中文问题 + schema -> 纯 SQL”能力，构建一个完整后训练项目：

1. 从公开 Text-to-SQL 数据和自建 SQLite 小库出发，构造 SFT / DPO / GRPO 数据
2. 基于 `Qwen/Qwen2.5-3B-Instruct` 完成 SFT 和 DPO 主线训练
3. 用 `GRPO` 做可执行 reward 驱动的扩展实验
4. 对比 `Base / SFT / DPO / GRPO` 的 SQL 质量和执行结果
5. 最终为 agent / tool-use 扩展预留接口，但 v1 不直接做 agent demo

## Task Definition

第一版任务固定为：

- 输入：`schema_text + question_zh`
- 输出：一条 **SQLite SELECT SQL**

硬约束：

- 只输出 SQL，不输出解释
- 不输出 Markdown 代码块
- 禁止 DDL / DML / 多语句
- 只面向 SQLite 方言

详细任务规格见：

- [`docs/project_task_spec.md`](docs/project_task_spec.md)
- [`docs/sql_output_spec.md`](docs/sql_output_spec.md)
- [`docs/preference_judging_standard.md`](docs/preference_judging_standard.md)

## Stage Plan

当前执行顺序固定为：

1. 先学完整后训练知识链路
2. 再锁 Text-to-SQL 任务、数据源和评测基线
3. 再做 `SFT -> DPO`
4. 最后补 `GRPO` 和 `PPO mini`

完整计划见：

- [`docs/stage_plan.md`](docs/stage_plan.md)
- [`docs/roadmap.md`](docs/roadmap.md)

## Training Pipeline

```text
Raw text-to-SQL data
  -> normalized SQL data
  -> ShareGPT SFT data
  -> chosen/rejected DPO data
  -> prompt-only GRPO data
  -> SFT
  -> DPO
  -> GRPO
  -> evaluation
  -> error analysis
  -> resume/interview packaging
```

## Repository Layout

```text
medical-qa-posttraining/
  README.md
  docs/
  data_cards/
  configs/
  scripts/
  project_data/
  experiments/
  results/
  src/
  references/
  third_party/
```

## Included Framework Code

当前仓库内已经包含一份 MedicalGPT 代码镜像，位置在：

- [third_party/MedicalGPT](third_party/MedicalGPT)

约定如下：

- `third_party/MedicalGPT/`：训练框架和原始 stage 入口
- 仓库根目录的 `docs/`、`data_cards/`、`project_data/`、`src/`、`experiments/`、`results/`：本项目自己的数据、评测和实验过程

## Current Status

- [x] 完成第一阶段：SFT 知识打底
- [x] 完成第二阶段：偏好学习与在线 RL 知识主线
- [x] 完成第三阶段：GRPO 与统一方法论收束
- [ ] 完成第四阶段：Text-to-SQL 项目定义与评测基线
- [ ] 完成第五阶段：SFT 数据构建与 SFT 正式实验
- [ ] 完成第六阶段：DPO 主结果 + GRPO 扩展实验
- [ ] 完成第七阶段：PPO mini + 结果包装

## Planned Metrics

第一版重点记录以下指标：

- `valid_sql_rate`
- `execution_success_rate`
- `execution_accuracy`
- `safe_sql_rate`
- `schema_grounding_rate`
- 人工错误分析结论

评测固定采用双主线：

- 公开 benchmark：`CSpider` 官方 dev
- 任务对齐评测：自建 `sql_eval_dev_v1` / `sql_eval_report_v1`

## Key Data Sources

- `CSpider` train/dev
- `Spider` train
- 自建 SQLite 小库：`sales`, `hr`, `education`, `ecommerce`

详细数据源说明见：

- [`data_cards/raw_sources.md`](data_cards/raw_sources.md)

## Configs and Protocols

- 基线推理协议：[`docs/baseline_inference_protocol.md`](docs/baseline_inference_protocol.md)
- 数据构建规范：[`docs/data_building_standard.md`](docs/data_building_standard.md)
- 自建评测标注规范：[`docs/sql_eval_annotation_guideline.md`](docs/sql_eval_annotation_guideline.md)
- SQL 生成 prompt：[`configs/eval/text2sql_system_prompt.txt`](configs/eval/text2sql_system_prompt.txt)
- GRPO reward：[`configs/eval/grpo_reward_weights.json`](configs/eval/grpo_reward_weights.json)

## Runbook

项目根目录提供了四个直接入口：

- baseline：
  - `bash scripts/run_baseline_eval.sh`
- SFT：
  - `bash scripts/run_sft.sh`
- DPO：
  - `bash scripts/run_dpo.sh`
- GRPO：
  - `bash scripts/run_grpo.sh`

其中：

- `run_baseline_eval.sh` 会先根据 `project_data/eval/db_seeds/` 生成 SQLite 小库
- `run_sft.sh / run_dpo.sh / run_grpo.sh` 默认读取 `project_data/` 下的项目数据目录
- 训练真正调用的是 `third_party/MedicalGPT/` 里的底层训练代码

## Experiment Log

所有实验都记录在 `experiments/` 下，至少包括：

- 目标
- 数据版本
- 模型版本
- 训练参数
- 运行命令
- 核心指标
- 失败点
- 下一轮改动

## Resume Angle

这个项目最终希望能支持如下表述：

- 基于 MedicalGPT 训练框架完成中文 Text-to-SQL 后训练项目
- 构建了 `SFT / DPO / GRPO` 三阶段数据与评测闭环
- 使用 `CSpider` 和自建 SQLite 评测集验证 SQL 生成与执行正确率
- 以 `DPO` 作为主结果，以 `GRPO` 作为 reward 驱动扩展，并为后续 agent / tool-use 扩展预留接口

## Next Step

1. 接入 `CSpider / Spider` 数据并生成 `sft_train_v1`
2. 构建 4 个 SQLite 小库与 `sql_eval_dev_v1`
3. 跑 `Qwen/Qwen2.5-3B-Instruct` baseline
