# Interview Notes

## 1-Minute Version

我做了一个医疗大模型后训练项目，基于 MedicalGPT 的训练框架，以 `Qwen3.5-2B` 为底座，围绕医疗问答和结构化输出能力做了完整闭环。项目包括原始医疗数据清洗、SFT 数据与 preference 数据构建、SFT 和 DPO 训练、固定评测集验证，以及错误案例分析。重点不是只跑脚本，而是用数据设计、训练方法和评估体系去证明模型能力提升。

## 3-Minute Version

待补充，按下面结构展开：

1. 为什么选 MedicalGPT 和 `Qwen3.5-2B`
2. 为什么先学完整知识链路，再做项目
3. 为什么项目主线是 `SFT + DPO`
4. 为什么 RM + RLOO/PPO 只做小实验
5. 为什么采用双主评测而不是只看一个 benchmark

## High-Frequency Questions

### 为什么先做 SFT 再做 DPO？

待补充：

- SFT 先让模型学会目标回答分布
- DPO 再在已有行为基础上做偏好对齐
- 如果没有 SFT，DPO 的优化基础会不稳定

### DPO 和 PPO 的区别是什么？

待补充：

- DPO 是离线偏好优化
- PPO 是在线策略优化
- DPO 不需要 rollout，PPO 需要 reward model 和在线采样

### 为什么这个项目不把 PPO 作为主结果？

待补充：

- 项目主任务更适合先做完整闭环
- PPO 成本更高、组件更多、迭代更慢
- 所以 PPO 作为扩展实验而不是主交付

### 为什么采用双主评测？

待补充：

- `C-Eval` 负责公开 benchmark 说服力
- 自建结构化医疗评测集负责任务目标对齐
- 两者结合才能同时支撑对外展示和项目真实性
