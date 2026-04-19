# Method Comparison

## Core Comparison Table

| Method | Data Format | Need RM | Need Ref Model | Online Sampling | Main Goal |
| --- | --- | --- | --- | --- | --- |
| SFT | `conversations` | No | No | No | 学习目标回答分布 |
| RM | `conversations + chosen/rejected` | - | No | No | 学习偏好打分 |
| PPO / RLOO | prompt-only + online rollout | Yes | Yes | Yes | 在线优化策略 |
| DPO | `conversations + chosen/rejected` | No | Yes | No | 直接优化偏好 |
| ORPO | `conversations + chosen/rejected` | No | No | No | 单模型偏好优化 |
| GRPO | prompt-only + multi-sample rollout | reward function | No value head | Yes | 组内相对优化 |

## Notes

- 正式主结果固定为 `SFT + DPO`
- `RM + RLOO/PPO` 固定为扩展小实验
- `GRPO` 固定为学习重点，不作为项目正式主结果
- 评测固定采用双主评测：
  - `C-Eval` 医学子集
  - 自建结构化医疗评测集
