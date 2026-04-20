# Project Data

这里存放项目自己的数据，不和 `third_party/MedicalGPT/data/` 混在一起。

## 目录说明

- `raw/`
  - 原始下载数据
  - 例如 `CSpider`、`Spider`、自建 seed CSV
- `intermediate/`
  - 清洗、去重、标准化后的中间产物
  - 例如 SQL canonicalize 结果、去噪后的 prompt 池
- `sft/`
  - 最终 ShareGPT 格式的 SFT 数据
- `preference/`
  - 最终 DPO / RM 数据
- `grpo/`
  - 供 GRPO 使用的 prompt-only 数据
- `eval/`
  - 自建评测集、SQLite seeds、生成后的数据库文件

## 约定

- 所有训练集、验证集、测试集都要带版本号
- 官方 benchmark 的 dev/test 不回流训练
- `eval/` 下的固定评测集只用于评测，不参与训练数据召回
