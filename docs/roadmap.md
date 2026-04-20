# 项目路线图

## 当前大方向

项目正式转为：

- 主题：中文 Text-to-SQL 后训练
- 主结果：`SFT + DPO`
- 扩展：`GRPO`
- 补充：`RM + RLOO/PPO mini`

## 阶段 A：任务和评测锁定

- 锁定输入输出接口：`schema_text + question_zh -> SQL`
- 锁定主模型：`Qwen/Qwen2.5-3B-Instruct`
- 锁定双主评测：
  - `CSpider dev`
  - `sql_eval_dev_v1 / sql_eval_report_v1`

## 阶段 B：数据底座搭建

- 接入 `CSpider` / `Spider`
- 构建 4 个 SQLite 小库
- 补齐评测模板、构库脚本、执行器

## 阶段 C：Baseline

- 跑 base model
- 固定 prompt 和 generation config
- 记录错误类型分布

## 阶段 D：SFT

- 构造 `sft_train_v1 / sft_val_v1`
- 跑 `Base vs SFT`
- 观察 valid SQL 和 execution accuracy 的变化

## 阶段 E：DPO

- 构造 `dpo_train_v1 / dpo_val_v1`
- 跑 `Base vs SFT vs DPO`
- 重点观察 schema grounding 和 wrong-result 是否下降

## 阶段 F：GRPO

- 基于 SFT checkpoint 做 reward 驱动扩展
- 对比 `SFT vs GRPO`
- 观察 reward 指标是否和 execution accuracy 同向改善

## 阶段 G：收束与包装

- 完成 README 结果区
- 完成错误案例分析
- 整理简历项目描述和面试答题模板
