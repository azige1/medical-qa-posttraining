# 面试笔记

## 一句话讲项目

基于 MedicalGPT 训练脚手架做了一个中文 Text-to-SQL 后训练项目，围绕 `schema_text + question_zh -> SQL` 这个接口，完成了 `SFT + DPO` 主线和 `GRPO` 扩展，并用 `CSpider dev` 与自建 SQLite 评测集验证模型在 valid SQL、execution accuracy 和 schema grounding 上的提升。

## 三分钟讲项目

### 1. 任务定义

- 输入是中文问题和数据库 schema
- 输出是单条 SQLite `SELECT`
- 第一版不做解释、不做 agent、不做多语句

### 2. 数据设计

- 用 `CSpider` 作为中文主训练来源
- 用 `Spider` 补足 SQL 结构多样性
- 自建 4 个 SQLite 小库做任务对齐评测
- 用模型错误 SQL + 规则扰动 SQL 构造 DPO preference pairs

### 3. 训练路线

- baseline：原始 `Qwen/Qwen2.5-3B-Instruct`
- SFT：先学 schema 到 SQL 的基本行为
- DPO：用 chosen/rejected 强化执行正确 SQL
- GRPO：作为扩展实验，用可执行 reward 直接优化 SQL 质量

### 4. 评测闭环

- `CSpider dev` 看公开 benchmark 能力
- 自建 SQLite 评测集看任务对齐能力
- 指标记录 `valid_sql_rate / execution_success_rate / execution_accuracy / schema_grounding_rate`
- 再做错误类型分析，比如 wrong filter、wrong join、schema hallucination

## 高频追问

### 为什么 DPO 是主结果，GRPO 只是扩展？

- DPO 更稳定，数据闭环更容易做
- Text-to-SQL 很适合把“正确 SQL 比错误 SQL 更优”写成 pairwise preference
- GRPO 含金量高，但 reward 设计和训练成本更高，适合作为第二阶段扩展

### 为什么还要自建 SQLite 评测集？

- 官方 benchmark 不一定覆盖你想强调的输出风格和错误类型
- 自建评测更容易把项目目标和模型提升挂钩
- 面试时也能更清楚地解释“我到底优化了什么”

### 为什么不直接做 agent？

- v1 先把核心生成能力和训练闭环做扎实
- `generate_sql(question, schema) -> sql` 和 `execute_sql(db_path, sql) -> result` 两个接口先稳定下来
- 后续要接 agent，只需要在这两个接口外再包工具调用层
