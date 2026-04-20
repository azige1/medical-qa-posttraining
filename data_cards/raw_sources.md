# Raw Sources

记录 Text-to-SQL 项目的原始数据来源、许可证、用途和筛选理由。

| Source | Type | License | Intended Use | Notes |
| --- | --- | --- | --- | --- |
| `CSpider` train/dev | Chinese text-to-SQL | check upstream | SFT 主池 / benchmark | 第一版最核心的中文数据来源 |
| `Spider` train | English text-to-SQL | check upstream | SFT 补充 | 只做结构与 SQL 多样性补充，不压过中文主池 |
| self-built SQLite seeds | SQLite schemas + CSV seeds | project-owned | 自建评测 | 生成 `sales/hr/education/ecommerce` 小库 |
| self-built preference pairs | chosen/rejected SQL | project-owned | DPO | 围绕执行正确性、schema grounding、只读安全性构造 |
| self-built prompt-only GRPO set | prompt + gold_sql | project-owned | GRPO | 用于可执行 reward 的采样式训练 |
| `BIRD` | benchmark | check upstream | stretch benchmark | 不作为第一版必交付 |

## Selection Policy

- 第一版以 `CSpider` 为中文主训练来源，不做大而杂的全量堆料
- `Spider` 只做小比例结构增强，不让英文样本主导分布
- benchmark 的官方 dev 不回流训练
- 自建 SQLite 小库只服务于项目评测，不服务于训练数据召回
