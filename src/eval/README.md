# Evaluation Utilities

这里放项目自己的 Text-to-SQL 评测代码。

当前规划包含：

- `run_text2sql_inference.py`
  - 跑固定 prompt 模板，生成 SQL 预测文件
- `eval_text2sql_sqlite.py`
  - 在 SQLite 上执行预测 SQL，产出报告和错误案例
- `sql_utils.py`
  - SQL 清洗、安全检查、执行和错误分类工具

公开 `CSpider` benchmark 的正式打分优先仍使用官方评测脚本。
