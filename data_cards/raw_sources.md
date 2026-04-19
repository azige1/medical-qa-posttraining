# Raw Sources

记录原始数据来源、许可证、用途和筛选理由。

| Source | Type | License | Intended Use | Notes |
| --- | --- | --- | --- | --- |
| `shibing624/medical` | medical QA / medical corpus | research only, check upstream | SFT 主池 | 第一版最核心的医疗数据来源 |
| `FreedomIntelligence/HuatuoGPT-sft-data-v1` | medical dialogue | check upstream | SFT 补充 | 用于补医疗问答表达和对话风格 |
| high-quality Chinese ShareGPT data | general dialogue | check upstream | 通用补充 | 只做小比例补充，不冲淡医疗分布 |
| self-built preference pairs | chosen/rejected | project-owned | DPO / RM | 围绕医疗正确性、完整性、结构化和安全性构造 |
| `C-Eval` medical subsets | public benchmark | upstream benchmark license | 评测 | 只用于评测，不直接用于训练数据召回 |

## Selection Policy

- 第一版数据以医疗主数据为核心，不做大而杂的全量堆料
- 若采用目标导向召回，只能使用独立 `seed set` 或 `retrieval-dev set`
- 不直接用最终 `C-Eval` 题目反向筛选训练数据
