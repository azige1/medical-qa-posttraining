# Raw Text-to-SQL Data Layout

这里存放未加工的官方 Text-to-SQL 原始数据，不提交大文件本体。

## 预期目录结构

```text
project_data/raw/
  cspider/
    train.json
    dev.json
    tables.json
    database/
      <db_id>/
        <db_id>.sqlite
  spider/
    train_spider.json
    train_others.json
    dev.json
    tables.json
    database/
      <db_id>/
        <db_id>.sqlite
```

## 用途

- `cspider/`
  - 中文主训练来源
  - `dev.json` 同时也是公开 benchmark 候选，但不要回流训练
- `spider/`
  - 英文结构增强来源
  - 默认只抽一小部分 train 样本，避免英文主导分布

## 下一步脚本

原始数据放好后，运行：

```bash
bash scripts/build_sft_data.sh
```

它会读取上面的目录，产出：

- `project_data/sft/train/*.jsonl`
- `project_data/sft/val/*.jsonl`
- `project_data/intermediate/sft_build_report_v1.json`
