# 方法对比

| 方法 | 数据输入 | 依赖模型 | 训练信号 | 在 Text-to-SQL 里的作用 | 主要风险 |
| --- | --- | --- | --- | --- | --- |
| SFT | `conversations` | policy | gold SQL token loss | 先学会根据 schema 写 SQL | 学到数据噪声和表面模式 |
| DPO | `conversations + chosen + rejected` | policy + reference | chosen/rejected 对比偏好 | 压低错 SQL，强化执行正确 SQL | pair 质量决定上限 |
| GRPO | prompt-only + reward | policy + reward function | 多采样相对奖励 | 直接拉 execution-aware reward | reward 设计和采样成本敏感 |
| RM | `conversations + chosen + rejected` | reward model | pairwise ranking | 给在线 RL 提供可学习偏好打分 | reward 与最终策略之间有 gap |
| PPO/RLOO | rollout prompt | policy + ref + RM (+ value for PPO) | online RL reward | 证明完整 RLHF 链路理解 | 训练贵且稳定性差 |

## 推荐主线

第一版项目推荐顺序固定为：

1. `SFT`
2. `DPO`
3. `GRPO`
4. `RM + PPO/RLOO mini`

原因：

- `SFT` 是所有后续方法的行为底座
- `DPO` 最适合做主结果，因为它最容易把“正确 SQL 优于错误 SQL”写成稳定训练信号
- `GRPO` 含金量高，但 reward 设计和训练稳定性要求更高，更适合作为扩展实验
- `PPO/RLOO` 在 Text-to-SQL 上并不是第一版性价比最高的主结果路线
