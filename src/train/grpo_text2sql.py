import glob
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import torch
from datasets import load_dataset
from peft import LoraConfig, TaskType, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from transformers.integrations import is_deepspeed_zero3_enabled
from transformers.trainer_utils import get_last_checkpoint
from trl import GRPOConfig, GRPOTrainer, ModelConfig, TrlParser


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.eval.sql_utils import (  # noqa: E402
    classify_sql_error,
    compare_results,
    execute_sql,
    is_safe_select,
    load_json,
    load_text,
    normalize_predicted_sql,
    render_text2sql_prompt,
    resolve_path,
)


os.environ["TOKENIZERS_PARALLELISM"] = "FALSE"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

REWARD_CFG: dict = {}
EXEC_CACHE: dict[tuple[str, str], tuple[bool, list | None, str | None]] = {}


@dataclass
class ScriptArguments:
    tokenizer_name_or_path: Optional[str] = field(default=None)
    train_file_dir: Optional[str] = field(default=None)
    validation_file_dir: Optional[str] = field(default=None)
    reward_config_file: Optional[str] = field(default="configs/eval/grpo_reward_weights.json")
    system_prompt_file: Optional[str] = field(default="configs/eval/text2sql_system_prompt.txt")
    max_train_samples: Optional[int] = field(default=-1)
    preprocessing_num_workers: Optional[int] = field(default=4)
    eval_split_ratio: Optional[float] = field(default=0.1)


def find_all_linear_names(peft_model, int4: bool = False, int8: bool = False) -> list[str]:
    cls = torch.nn.Linear
    if int4 or int8:
        import bitsandbytes as bnb

        cls = bnb.nn.Linear4bit if int4 else bnb.nn.Linear8bitLt
    module_names = set()
    for name, module in peft_model.named_modules():
        if isinstance(module, cls) and "lm_head" not in name and "output_layer" not in name:
            parts = name.split(".")
            module_names.add(parts[0] if len(parts) == 1 else parts[-1])
    return sorted(module_names)


def get_checkpoint(training_args: GRPOConfig) -> Optional[str]:
    if os.path.isdir(training_args.output_dir):
        return get_last_checkpoint(training_args.output_dir)
    return None


def _get_weight(name: str) -> float:
    return float(REWARD_CFG.get(name, 0.0))


def _get_penalty(name: str) -> float:
    return float(REWARD_CFG.get("penalty", {}).get(name, 0.0))


def _completion_to_sql(completion) -> str:
    return normalize_predicted_sql(completion[0]["content"])


def _execute_cached(db_path: str, sql: str):
    key = (db_path, sql)
    if key not in EXEC_CACHE:
        EXEC_CACHE[key] = execute_sql(db_path, sql)
    return EXEC_CACHE[key]


def parseable_sql_reward(completions, **kwargs):
    return [_get_weight("parseable_sql") if _completion_to_sql(item) else 0.0 for item in completions]


def safe_select_reward(completions, **kwargs):
    rewards = []
    for item in completions:
        sql = _completion_to_sql(item)
        ok, reason = is_safe_select(sql)
        if ok:
            rewards.append(_get_weight("safe_select_only"))
        elif reason == "multi_statement":
            rewards.append(_get_penalty("multi_statement"))
        elif reason in {"non_select", "unsafe_keyword"}:
            rewards.append(_get_penalty("non_select"))
        else:
            rewards.append(0.0)
    return rewards


def schema_grounding_reward(completions, db_path, **kwargs):
    rewards = []
    for item, path_str in zip(completions, db_path):
        sql = _completion_to_sql(item)
        ok, _ = is_safe_select(sql)
        if not ok:
            rewards.append(0.0)
            continue
        resolved_path = str(resolve_path(path_str, PROJECT_ROOT))
        exec_ok, _, exec_error = _execute_cached(resolved_path, sql)
        if exec_ok:
            rewards.append(_get_weight("schema_grounding"))
        elif classify_sql_error(exec_error) == "schema_hallucination":
            rewards.append(_get_penalty("schema_violation"))
        else:
            rewards.append(0.0)
    return rewards


def execution_success_reward(completions, db_path, **kwargs):
    rewards = []
    for item, path_str in zip(completions, db_path):
        sql = _completion_to_sql(item)
        ok, _ = is_safe_select(sql)
        if not ok:
            rewards.append(0.0)
            continue
        resolved_path = str(resolve_path(path_str, PROJECT_ROOT))
        exec_ok, _, _ = _execute_cached(resolved_path, sql)
        rewards.append(_get_weight("execution_success") if exec_ok else 0.0)
    return rewards


def execution_match_reward(completions, db_path, gold_sql, **kwargs):
    rewards = []
    for item, path_str, gold in zip(completions, db_path, gold_sql):
        sql = _completion_to_sql(item)
        ok, _ = is_safe_select(sql)
        if not ok:
            rewards.append(0.0)
            continue
        resolved_path = str(resolve_path(path_str, PROJECT_ROOT))
        pred_ok, pred_rows, _ = _execute_cached(resolved_path, sql)
        gold_ok, gold_rows, gold_error = _execute_cached(resolved_path, gold)
        if not gold_ok:
            raise RuntimeError(f"Gold SQL failed in reward function: {gold_error}")
        rewards.append(_get_weight("execution_match") if pred_ok and compare_results(pred_rows, gold_rows) else 0.0)
    return rewards


def load_local_datasets(train_dir: str, validation_dir: Optional[str] = None):
    data_files = {}
    train_files = glob.glob(f"{train_dir}/**/*.jsonl", recursive=True)
    if not train_files:
        raise FileNotFoundError(f"No jsonl files found under {train_dir}")
    data_files["train"] = train_files
    if validation_dir and os.path.exists(validation_dir):
        eval_files = glob.glob(f"{validation_dir}/**/*.jsonl", recursive=True)
        if eval_files:
            data_files["validation"] = eval_files
    return load_dataset("json", data_files=data_files)


def train_grpo(model_args: ModelConfig, script_args: ScriptArguments, training_args: GRPOConfig) -> None:
    tokenizer = AutoTokenizer.from_pretrained(
        script_args.tokenizer_name_or_path or model_args.model_name_or_path,
        trust_remote_code=model_args.trust_remote_code,
        revision=model_args.model_revision,
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    raw_datasets = load_local_datasets(script_args.train_file_dir, script_args.validation_file_dir)
    train_dataset = raw_datasets["train"]
    if script_args.max_train_samples and script_args.max_train_samples > 0:
        train_dataset = train_dataset.select(range(min(len(train_dataset), script_args.max_train_samples)))

    eval_dataset = raw_datasets.get("validation")
    if eval_dataset is None and training_args.eval_strategy != "no":
        split = train_dataset.train_test_split(test_size=script_args.eval_split_ratio)
        train_dataset = split["train"]
        eval_dataset = split["test"]

    system_prompt = load_text(resolve_path(script_args.system_prompt_file, PROJECT_ROOT))

    def format_row(row):
        question = row.get("question")
        if not question:
            question = render_text2sql_prompt(row)
        return {
            "prompt": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question},
            ],
            "db_path": row["db_path"],
            "gold_sql": row.get("answer") or row.get("gold_sql"),
        }

    train_dataset = train_dataset.map(
        format_row,
        num_proc=script_args.preprocessing_num_workers,
        desc="Formatting GRPO train dataset",
    )
    if eval_dataset is not None:
        eval_dataset = eval_dataset.map(
            format_row,
            num_proc=script_args.preprocessing_num_workers,
            desc="Formatting GRPO eval dataset",
        )

    torch_dtype = model_args.dtype if model_args.dtype in ["auto", None] else getattr(torch, model_args.dtype)
    quantization_config = None
    if model_args.load_in_4bit or model_args.load_in_8bit:
        if is_deepspeed_zero3_enabled():
            raise ValueError("DeepSpeed ZeRO-3 is incompatible with quantization for this GRPO setup.")
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=model_args.load_in_4bit,
            load_in_8bit=model_args.load_in_8bit,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch_dtype if torch_dtype != "auto" else torch.bfloat16,
        )

    model = AutoModelForCausalLM.from_pretrained(
        model_args.model_name_or_path,
        revision=model_args.model_revision,
        trust_remote_code=model_args.trust_remote_code,
        attn_implementation=model_args.attn_implementation,
        torch_dtype=torch_dtype if torch_dtype != "auto" else None,
        low_cpu_mem_usage=not is_deepspeed_zero3_enabled(),
        quantization_config=quantization_config,
        device_map="auto",
    )

    if model_args.use_peft:
        target_modules = model_args.lora_target_modules
        if target_modules == "all" or (isinstance(target_modules, list) and "all" in target_modules):
            target_modules = find_all_linear_names(model, model_args.load_in_4bit, model_args.load_in_8bit)
        peft_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            target_modules=target_modules,
            inference_mode=False,
            r=model_args.lora_r,
            lora_alpha=model_args.lora_alpha,
            lora_dropout=model_args.lora_dropout,
        )
        model = get_peft_model(model, peft_config)
        for parameter in filter(lambda p: p.requires_grad, model.parameters()):
            parameter.data = parameter.data.to(torch.float32)
        model.print_trainable_parameters()

    trainer = GRPOTrainer(
        model=model,
        processing_class=tokenizer,
        reward_funcs=[
            parseable_sql_reward,
            safe_select_reward,
            schema_grounding_reward,
            execution_success_reward,
            execution_match_reward,
        ],
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset if training_args.eval_strategy != "no" else None,
    )

    last_checkpoint = get_checkpoint(training_args)
    train_result = trainer.train(resume_from_checkpoint=last_checkpoint)
    metrics = train_result.metrics
    metrics["train_samples"] = len(train_dataset)
    trainer.log_metrics("train", metrics)
    trainer.save_metrics("train", metrics)
    trainer.save_state()
    trainer.save_model(training_args.output_dir)
    tokenizer.save_pretrained(training_args.output_dir)


def main() -> None:
    parser = TrlParser((ModelConfig, ScriptArguments, GRPOConfig))
    model_args, script_args, training_args = parser.parse_args_and_config()

    global REWARD_CFG
    REWARD_CFG = load_json(resolve_path(script_args.reward_config_file, PROJECT_ROOT))
    train_grpo(model_args, script_args, training_args)


if __name__ == "__main__":
    main()
