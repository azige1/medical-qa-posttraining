# AutoDL Runbook

这份手册只解决一件事：把项目从“本地代码准备”推进到“AutoDL 上可直接开跑”。

当前推荐工作流固定为：

1. 本地维护代码、文档、实验记录
2. AutoDL 维护 raw 数据、训练产物、checkpoint、WandB 日志
3. 无卡模式先做环境准备和数据上传
4. 切到 GPU 模式后再跑 baseline / SFT / DPO / GRPO

## 1. 远端项目根目录

当前服务器上的项目根目录约定为：

```bash
/root/medical-qa-posttraining
```

后续所有命令都默认在这个目录下执行。

## 2. 无卡模式下要完成的事

无卡模式只做准备，不跑训练。

固定顺序：

1. 同步项目代码
2. 上传 raw 数据
3. 检查 raw 数据结构
4. 构建 SFT 数据
5. 登录 WandB
6. 确认 baseline / SFT / DPO 命令能正常启动

## 3. raw 数据上传目标

只需要上传两套官方数据：

- `project_data/raw/cspider/`
- `project_data/raw/spider/`

目标结构必须是：

```text
project_data/raw/
  cspider/
    train.json
    dev.json
    tables.json
    database/<db_id>/<db_id>.sqlite
  spider/
    train_spider.json
    train_others.json
    dev.json
    tables.json
    database/<db_id>/<db_id>.sqlite
```

不要把这两套数据改成别的文件名，也不要先用 Hugging Face 精简版替换官方原始文件。

## 4. 上传后先检查 raw 数据

执行：

```bash
bash scripts/check_raw_data.sh
```

这一步会检查：

- `cspider` 和 `spider` 的关键 json 文件是否存在
- `database/` 目录是否存在
- `.sqlite` 数据库文件数量是否大于 0

如果这一步没过，不要继续构建 SFT 数据。

## 5. 构建 SFT 数据

raw 数据检查通过后执行：

```bash
bash scripts/build_sft_data.sh
```

构建结果默认写到：

```text
project_data/sft/train/
project_data/sft/val/
project_data/intermediate/sft_build_report_v1.json
```

构建完成后，优先检查：

- `project_data/sft/train/cspider_train_sft_v1.jsonl`
- `project_data/sft/train/spider_train_sft_v1.jsonl`
- `project_data/sft/val/cspider_dev_sft_v1.jsonl`
- `project_data/sft/val/spider_dev_sft_v1.jsonl`

## 6. WandB

第一次在训练环境里使用前执行：

```bash
wandb login
```

训练脚本已经支持：

```bash
REPORT_TO=wandb WANDB_PROJECT=text2sql-posttraining RUN_NAME=qwen25_3b_sft_v1 bash scripts/run_sft.sh
REPORT_TO=wandb WANDB_PROJECT=text2sql-posttraining RUN_NAME=qwen25_3b_dpo_v1 bash scripts/run_dpo.sh
REPORT_TO=wandb WANDB_PROJECT=text2sql-posttraining RUN_NAME=qwen25_3b_grpo_v1 bash scripts/run_grpo.sh
```

## 7. 切到 GPU 后的执行顺序

推荐固定顺序：

1. baseline
2. SFT
3. DPO
4. GRPO

对应命令：

```bash
bash scripts/run_baseline_eval.sh
REPORT_TO=wandb WANDB_PROJECT=text2sql-posttraining RUN_NAME=qwen25_3b_sft_v1 bash scripts/run_sft.sh
REPORT_TO=wandb WANDB_PROJECT=text2sql-posttraining RUN_NAME=qwen25_3b_dpo_v1 bash scripts/run_dpo.sh
REPORT_TO=wandb WANDB_PROJECT=text2sql-posttraining RUN_NAME=qwen25_3b_grpo_v1 bash scripts/run_grpo.sh
```

## 8. 当前阶段最重要的判断规则

- raw 数据没上传完整：不要开始构建 SFT 数据
- SFT 数据没构建成功：不要开始训练
- baseline 没跑通：不要直接开长跑 SFT
- SFT 没有稳定结果：不要急着构造 DPO 数据

## 9. 最短路径

如果你想用最短路径推进项目，就按下面走：

```bash
bash scripts/check_raw_data.sh
bash scripts/build_sft_data.sh
bash scripts/run_baseline_eval.sh
REPORT_TO=wandb WANDB_PROJECT=text2sql-posttraining RUN_NAME=qwen25_3b_sft_v1 bash scripts/run_sft.sh
```

## 10. DPO handoff after SFT

After SFT finishes, use this fixed handoff:

```bash
bash scripts/merge_sft_adapter.sh
bash scripts/build_preference_data.sh
bash scripts/run_dpo_all.sh
```

If you want the full one-line sequence with explicit run names:

```bash
RUN_NAME=qwen25_3b_sft_v1 bash scripts/run_sft_all.sh
BASE_MODEL=/root/autodl-tmp/models/Qwen2.5-3B-Instruct LORA_MODEL=outputs/sft/qwen25_3b_text2sql_sft_v1 OUTPUT_DIR=outputs/merged/qwen25_3b_text2sql_sft_v1 bash scripts/merge_sft_adapter.sh
bash scripts/build_preference_data.sh
RUN_NAME=qwen25_3b_dpo_v1 MODEL_NAME_OR_PATH=outputs/merged/qwen25_3b_text2sql_sft_v1 bash scripts/run_dpo_all.sh
```
