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

- 第一版项目主线使用 `SFT + DPO`
- RM / PPO / RLOO / GRPO 主要用于学习和面试扩展
- 不把 PPO 作为第一版项目的核心交付
