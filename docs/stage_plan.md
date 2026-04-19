# MedicalGPT 学习与项目计划：先完整学知识，再做项目

## Summary

这版计划固定采用“先学完整后训练知识链路，再做完整项目”的顺序，不按周拆分，而按阶段推进。

固定决策如下：

- 学习顺序：`SFT -> RM -> RLOO/PPO -> DPO -> ORPO -> GRPO -> 统一方法论 -> 面试表达`
- 项目主线：`Qwen/Qwen3.5-2B + SFT + DPO`
- 扩展实验：`RM + RLOO/PPO 小实验`
- 评测主线：`C-Eval 医学子集 + 自建结构化医疗评测集`
- 项目起点：先做评测基线，再开始训练和数据迭代

## 第一阶段：SFT 知识打底

目标：把 SFT 讲到面试级别，彻底打通 MedicalGPT 的监督微调主线。

锚点文件：

- `scripts/run_sft.sh`
- `training/supervised_finetuning.py`

必须掌握：

- 数据流：
  - `jsonl -> conversations -> messages/dialog -> input_ids/labels`
  - `IGNORE_INDEX = -100`
- 原理：
  - pretraining vs SFT
  - instruction tuning / dialogue tuning / response-only SFT
  - causal LM loss
  - teacher forcing
  - 为什么 prompt 进模型但不参与 loss
- 工程：
  - `HfArgumentParser`
  - tokenizer/model loading
  - LoRA / QLoRA
  - Trainer 启动
- 数学：
  - LoRA 的低秩更新
  - QLoRA 的量化与可训练参数分解
  - label mask 的 loss 形式

阶段交付：

- 一份 SFT 数据流图
- 一份 SFT 方法卡
- 一套 SFT 面试问答

## 第二阶段：偏好学习与在线 RL 知识主线

目标：把 RM、在线 RL、离线偏好优化之间的关系完全理清。

固定内容：

- RM：
  - `scripts/run_rm.sh`
  - `training/reward_modeling.py`
  - `chosen/rejected`
  - `sequence classification + num_labels=1`
  - pairwise ranking loss
  - RM vs value head
- 在线 RL：
  - 先 RLOO 最小闭环，再 PPO 完整组件
  - reward model、reference model、policy model、value model
  - rollout、reward、advantage、KL
  - 为什么在线 RL 成本高
- 离线偏好优化：
  - `training/dpo_training.py`
  - `training/orpo_training.py`
  - chosen/rejected 的 log-prob
  - DPO 为什么要 ref model
  - ORPO 为什么不要 ref model
  - DPO / PPO / RM 的关系

阶段交付：

- 一份 RM 方法卡
- 一份 PPO vs RLOO vs DPO vs ORPO 对比表
- 一套“什么时候该用哪条路线”的答法

## 第三阶段：GRPO 与统一方法论收束

目标：把整条后训练谱系收束成可解释、可比较、可面试表达的统一知识体系。

固定内容：

- 锚点文件：
  - `scripts/run_grpo.sh`
  - `training/grpo_training.py`
- 必学原理：
  - GRPO 的设计动机
  - group relative reward
  - 为什么弱化 value model
  - 为什么更适合 reasoning / multi-sample
- 统一方法论：
  - PT / SFT / RM / PPO / RLOO / DPO / ORPO / GRPO
  - 在线偏好优化 vs 离线偏好优化
  - “先学行为，再学偏好，再学策略”的统一图
- 项目表达准备：
  - 1 分钟项目讲法
  - 3 分钟项目讲法
  - 常见追问树

阶段交付：

- 一张完整方法图谱
- 一套 1 分钟 / 3 分钟项目表达
- 一套后训练高频问答

## 第四阶段：项目定义与评测基线

目标：在开始训练之前，把“评什么、拿什么训、怎么比”全部锁死。

固定实施内容：

- 锁定任务：
  - 医疗问答 + 结构化输出
- 锁定模型：
  - `Qwen/Qwen3.5-2B`
  - 不使用 `Qwen3.5-2B-Base` 作为项目主模型
- 锁定双主评测：
  - 公开 benchmark 主评测：C-Eval 医学子集
    - `Basic Medicine`
    - `Clinical Medicine`
    - `Physician`
  - 任务对齐主评测：自建固定医疗结构化评测集
- 锁定数据源：
  - SFT 主池：`shibing624/medical`
  - 医疗对话补充：`HuatuoGPT-sft-data-v1`
  - 少量通用补充：高质量中文 ShareGPT 数据
  - preference 主数据：自己构造
- 锁定自建评测集 schema：
  - `instruction`
  - `reference_answer`
  - `reference_key_points`
  - `question_type`
  - `triage_level`
  - `must_include`
  - `forbidden`
- 锁定 baseline：
  - 原始 `Qwen3.5-2B`
  - 统一 system prompt
  - 统一 decoding 设置
  - 同一批题上评测

阶段交付：

- 原始数据源清单
- `medical_eval_v1`
- C-Eval 医学子集评测方案
- baseline 实验卡与结果

## 第五阶段：SFT 数据构建与 SFT 正式实验

目标：做出第一版领域模型，并在双主评测下得到第一轮可解释提升。

固定实施内容：

- 数据构建：
  - 从医疗主池中筛出与任务强相关的样本
  - 不直接用最终 `C-Eval` 题目召回训练数据
  - 如需目标导向召回，只能用独立 `seed set` 或 `retrieval-dev set`
  - 全部改造成统一结构化输出风格
- 数据策略：
  - 先做高质量中小规模版本
  - 不追求一开始就堆海量样本
- 训练：
  - LoRA / QLoRA
  - 固定超参版本
  - 训练命令、模型版本、数据版本全部记录到实验卡
- 评测：
  - baseline vs SFT
  - 必须同时跑双主评测
  - 保存错误样例

阶段交付：

- `SFT dataset v1`
- `exp-001-sft-v1`
- baseline vs SFT 对比表
- 第一版错误分析

## 第六阶段：DPO 主结果 + RM/RLOO/PPO 小实验 + 项目收束

目标：完成完整项目闭环，而不是只停留在 SFT。

固定实施内容：

- preference 数据构造：
  - 以同一问题构造 `chosen/rejected`
  - 偏好维度固定为：
    - 医疗正确性
    - 完整性
    - 结构化输出规范性
    - 安全提示质量
    - 幻觉控制
- DPO：
  - 作为正式主结果
  - 与 baseline / SFT 保持同一评测体系
- RM + RLOO/PPO 小实验：
  - 不追求大规模完整 RLHF
  - 只做一版小规模闭环，用来证明你理解 reward model 和在线优化链路
  - 结果定位为扩展实验，不压过 DPO 主结果
- 项目收束：
  - 双主评测总表
  - 错误案例归类
  - 方法对比图
  - 简历项目描述
  - 面试答题模板

阶段交付：

- `preference dataset v1`
- `exp-002-dpo-v1`
- `exp-003-rm-rloo-or-ppo-mini`
- 最终 README 结果区
- 最终项目讲稿和简历版描述

## 第七阶段：结果包装与面试表达

目标：把知识和项目结果统一收束成能投递、能面试、能追问的表达体系。

固定实施内容：

- README 结果区整理
- 方法选择理由整理：
  - 为什么主线是 `SFT + DPO`
  - 为什么 PPO 只做小实验
  - 为什么双主评测更合理
- 实验表格与案例整理
- 简历项目描述：
  - 精简版
  - 进阶版
- 面试追问树：
  - 从项目追到数据
  - 从数据追到 SFT / DPO / RM / PPO
  - 从 PPO 追到 GRPO / RLHF

阶段交付：

- README 可展示版本
- 简历项目描述两版
- 面试问答模板
- 方法选型答法模板

## 验收标准

### 学习阶段验收

每个知识阶段结束都必须通过三类检查：

- 概念题：能定义核心对象、目标函数、设计动机
- 对比题：能比较相邻方法的差异与适用条件
- 项目题：能结合 MedicalGPT 真实文件讲出实现思路

完成标准：

- 能独立讲出该方法的 1 分钟解释
- 能回答 3 到 5 个追问
- 能把知识点落回 MedicalGPT 的文件锚点

### 项目阶段验收

项目验收必须同时满足：

- baseline / SFT / DPO 都在双主评测上有结果
- RM + RLOO/PPO 小实验至少形成一版可解释记录
- C-Eval 医学子集结果可复现
- 自建结构化评测集结果可复现
- 至少 20 条错误案例完成归类
- 最终 README、实验卡、结果表、面试讲稿保持一致
