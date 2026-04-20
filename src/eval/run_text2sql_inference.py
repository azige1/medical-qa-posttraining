import argparse
import os
import sys
import time
from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, GenerationConfig


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
MEDICALGPT_ROOT = PROJECT_ROOT / "third_party" / "MedicalGPT"
if str(MEDICALGPT_ROOT) not in sys.path:
    sys.path.insert(0, str(MEDICALGPT_ROOT))

from demo.inference import batch_generate_answer  # noqa: E402
from src.eval.sql_utils import dump_jsonl, load_json, load_jsonl, load_text, normalize_predicted_sql, render_text2sql_prompt  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Text-to-SQL inference on a fixed evaluation set.")
    parser.add_argument("--base_model", required=True)
    parser.add_argument("--eval_file", required=True)
    parser.add_argument("--output_file", required=True)
    parser.add_argument("--lora_model", default="")
    parser.add_argument("--tokenizer_path", default=None)
    parser.add_argument("--system_prompt_file", default=None)
    parser.add_argument("--system_prompt", default="")
    parser.add_argument("--generation_config_file", default=None)
    parser.add_argument("--max_new_tokens", type=int, default=None)
    parser.add_argument("--temperature", type=float, default=None)
    parser.add_argument("--top_p", type=float, default=None)
    parser.add_argument("--repetition_penalty", type=float, default=None)
    parser.add_argument("--eval_batch_size", type=int, default=None)
    parser.add_argument("--load_in_4bit", action="store_true")
    parser.add_argument("--load_in_8bit", action="store_true")
    parser.add_argument("--report_to", default="none")
    parser.add_argument("--run_name", default="")
    parser.add_argument("--wandb_log_steps", type=int, default=1)
    return parser.parse_args()


def load_generation_overrides(args: argparse.Namespace) -> dict[str, float | int]:
    config = {}
    if args.generation_config_file:
        config = load_json(args.generation_config_file)
    overrides = {
        "max_new_tokens": args.max_new_tokens,
        "temperature": args.temperature,
        "top_p": args.top_p,
        "repetition_penalty": args.repetition_penalty,
        "eval_batch_size": args.eval_batch_size,
    }
    for key, value in overrides.items():
        if value is not None:
            config[key] = value
    config.setdefault("max_new_tokens", 256)
    config.setdefault("temperature", 0.2)
    config.setdefault("top_p", 0.9)
    config.setdefault("repetition_penalty", 1.0)
    config.setdefault("eval_batch_size", 4)
    return config


def maybe_init_wandb(report_to: str, run_name: str):
    if report_to not in {"wandb", "all"}:
        return None
    import wandb

    return wandb.init(
        project=os.environ.get("WANDB_PROJECT", "text2sql-posttraining"),
        name=os.environ.get("WANDB_NAME") or run_name or None,
        id=os.environ.get("WANDB_RUN_ID") or None,
        resume="allow",
    )


def build_model_kwargs(args: argparse.Namespace) -> dict[str, object]:
    model_kwargs: dict[str, object] = {
        "trust_remote_code": True,
        "low_cpu_mem_usage": True,
        "device_map": "auto",
        "torch_dtype": torch.bfloat16 if torch.cuda.is_available() else "auto",
    }
    if torch.cuda.is_available():
        try:
            import flash_attn  # noqa: F401

            model_kwargs["attn_implementation"] = "flash_attention_2"
            print("[INFO] flash_attn detected, using flash_attention_2")
        except Exception:
            print("[INFO] flash_attn not available, using default attention implementation")
    if args.load_in_8bit:
        model_kwargs["quantization_config"] = BitsAndBytesConfig(load_in_8bit=True)
    elif args.load_in_4bit:
        model_kwargs["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
        )
    return model_kwargs


def main() -> None:
    args = parse_args()
    generation_cfg = load_generation_overrides(args)
    wandb_run = maybe_init_wandb(args.report_to, args.run_name)

    tokenizer_path = args.tokenizer_path or args.base_model
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, trust_remote_code=True, padding_side="left")

    model_kwargs = build_model_kwargs(args)

    base_model = AutoModelForCausalLM.from_pretrained(args.base_model, **model_kwargs)
    try:
        base_model.generation_config = GenerationConfig.from_pretrained(args.base_model, trust_remote_code=True)
    except OSError:
        pass
    model = (
        PeftModel.from_pretrained(base_model, args.lora_model, torch_dtype="auto", device_map="auto")
        if args.lora_model
        else base_model
    )
    model.eval()

    system_prompt = args.system_prompt
    if args.system_prompt_file:
        system_prompt = load_text(args.system_prompt_file)

    samples = load_jsonl(args.eval_file)
    prompts = [render_text2sql_prompt(sample) for sample in samples]
    results = []
    batch_size = int(generation_cfg["eval_batch_size"])
    total_samples = len(prompts)
    infer_start = time.perf_counter()

    for batch_index, start in enumerate(range(0, len(prompts), batch_size), start=1):
        batch_samples = samples[start:start + batch_size]
        batch_prompts = prompts[start:start + batch_size]
        outputs = batch_generate_answer(
            batch_prompts,
            model,
            tokenizer,
            system_prompt,
            model.device,
            max_new_tokens=int(generation_cfg["max_new_tokens"]),
            temperature=float(generation_cfg["temperature"]),
            top_p=float(generation_cfg["top_p"]),
            repetition_penalty=float(generation_cfg["repetition_penalty"]),
            stop_str="</s>",
        )
        for sample, raw_output in zip(batch_samples, outputs):
            results.append(
                {
                    "id": sample.get("id"),
                    "db_id": sample.get("db_id"),
                    "question_zh": sample.get("question_zh"),
                    "raw_output": raw_output,
                    "pred_sql": normalize_predicted_sql(raw_output),
                }
            )

        if wandb_run and batch_index % max(args.wandb_log_steps, 1) == 0:
            completed = len(results)
            elapsed = max(time.perf_counter() - infer_start, 1e-6)
            wandb_run.log(
                {
                    "baseline_inference/completed_samples": completed,
                    "baseline_inference/total_samples": total_samples,
                    "baseline_inference/progress": completed / total_samples if total_samples else 0.0,
                    "baseline_inference/batch_index": batch_index,
                    "baseline_inference/samples_per_second": completed / elapsed,
                },
                step=completed,
            )

    dump_jsonl(args.output_file, results)
    if wandb_run:
        elapsed = max(time.perf_counter() - infer_start, 1e-6)
        wandb_run.summary["baseline_inference/output_file"] = str(args.output_file)
        wandb_run.summary["baseline_inference/total_samples"] = total_samples
        wandb_run.summary["baseline_inference/samples_per_second"] = total_samples / elapsed
        wandb_run.finish()


if __name__ == "__main__":
    main()
