# Data Utilities

这里放项目自己的 Text-to-SQL 数据处理代码。

当前规划包含：

- `build_sqlite_eval_db.py`
  - 从 `schema.sql + CSV seed` 生成 SQLite 小库
- `convert_text2sql_to_sft.py`
  - 把 `CSpider / Spider` 原始数据转成 ShareGPT SFT 格式
- `build_text2sql_preference.py`
  - 后续构造 `chosen / rejected`

这部分代码只负责项目数据闭环，不改 `third_party/MedicalGPT` 的通用训练逻辑。
