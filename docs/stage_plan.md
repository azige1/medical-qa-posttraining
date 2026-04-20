# 项目阶段计划

## 当前共识

- 训练主线：`Qwen/Qwen2.5-3B-Instruct + SFT + DPO`
- 项目定位：中文 Text-to-SQL / 数据分析问答后训练
- 公开 benchmark：`CSpider dev`
- 自建评测：`sql_eval_dev_v1 + sql_eval_report_v1`
- 扩展路线：`GRPO`
- 可选补充：`RM + RLOO/PPO mini`

## 第一阶段：知识链路打通

学习顺序固定为：

1. `SFT`
2. `RM`
3. `RLOO / PPO`
4. `DPO`
5. `ORPO`
6. `GRPO`
7. 统一方法图谱
8. 面试表达

目标不是抠完所有源码，而是能把目标函数、数据流、方法差异和项目实现说清楚。

## 第二阶段：任务与评测锁定

- 固定任务接口：`schema_text + question_zh -> SQL`
- 固定输出约束：单条 SQLite `SELECT`
- 固定 baseline 协议
- 固定数据构建标准
- 固定 preference 判优标准
- 固定 GRPO reward 权重

## 第三阶段：数据与评测底座

### 3.1 训练数据

- 接入 `CSpider` 训练集
- 接入 `Spider` 训练集
- 生成 `sft_train_v1 / sft_val_v1`

### 3.2 preference 数据

- 选择训练池 prompt
- 生成 `chosen / rejected`
- 产出 `dpo_train_v1 / dpo_val_v1`

### 3.3 GRPO 数据

- 从训练 prompt 中抽取 `grpo_train_v1`
- 每条样本包含可执行环境需要的 `db_id / db_path / schema_text / question_zh / gold_sql`

### 3.4 评测底座

- 构建 `sales / hr / education / ecommerce` 四个 SQLite 小库
- 标注 `sql_eval_dev_v1`
- 标注 `sql_eval_report_v1`

## 第四阶段：baseline 与 SFT

- 跑 `Qwen/Qwen2.5-3B-Instruct` baseline
- 跑第一版 SFT
- 输出 `Base vs SFT`
- 记录错误类型变化

## 第五阶段：DPO 主结果

- 构造 DPO 数据
- 跑第一版 DPO
- 输出 `Base vs SFT vs DPO`
- 重点检查是否降低 wrong filter / wrong join / schema hallucination

## 第六阶段：GRPO 扩展

- 以 SFT checkpoint 为起点
- 用 SQLite 执行 reward 做一版 GRPO
- 输出 `SFT vs GRPO`
- 视资源情况决定是否加 `DPO vs GRPO`

## 第七阶段：收束与包装

- 统一 README 结果区
- 整理实验卡
- 完成错误案例分析
- 输出简历项目描述与面试问答模板
