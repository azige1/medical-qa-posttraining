# Roadmap

## Phase 1: Learn SFT Thoroughly

- 读透 `scripts/run_sft.sh` 和 `training/supervised_finetuning.py`
- 讲清 SFT 数据流、参数传递、LoRA / QLoRA、Trainer 启动
- 讲透 `causal LM loss`、`teacher forcing`、`response-only SFT`

## Phase 2: Learn Preference Learning and Online RL

- 读透 `reward_modeling.py`
- 先讲清 RLOO / PPO 最小闭环，再讲完整 PPO
- 再讲 DPO / ORPO 的离线偏好优化逻辑

## Phase 3: Learn GRPO and Build the Unified Map

- 讲清 GRPO 的设计动机和 group relative reward
- 统一 PT / SFT / RM / PPO / RLOO / DPO / ORPO / GRPO 的关系
- 准备 1 分钟 / 3 分钟项目表达

## Phase 4: Lock Project Definition and Baseline Evaluation

- 锁定任务：医疗问答 + 结构化输出
- 锁定模型：`Qwen/Qwen3.5-2B`
- 锁定双主评测：
  - C-Eval 医学子集
  - 自建结构化医疗评测集
- 跑 baseline 并建立第一张实验卡

## Phase 5: Build SFT Data and Run SFT

- 从医疗主池中筛出高相关样本
- 不直接用最终 `C-Eval` 题目召回训练数据
- 训练第一版 SFT 模型
- 记录 baseline vs SFT 结果和错误案例

## Phase 6: Run DPO and Add RM/RLOO/PPO Mini Experiment

- 构造第一版 `chosen/rejected` 偏好数据
- 训练 DPO 作为正式主结果
- 补一版 RM + RLOO/PPO 小实验
- 汇总双主评测结果

## Phase 7: Package Results for Resume and Interviews

- 整理结果表、案例和方法选择理由
- 产出简历项目描述
- 产出面试答题模板和追问树
