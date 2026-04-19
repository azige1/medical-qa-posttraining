import argparse
import json
from pathlib import Path

import torch
from peft import PeftModel
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, GenerationConfig

from demo.inference import batch_generate_answer


def load_jsonl(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_text(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def main():
    parser = argparse.ArgumentParser(description="Run project inference on a fixed evaluation set.")
    parser.add_argument("--base_model", type=str, required=True)
    parser.add_argument("--eval_file", type=str, required=True)
    parser.add_argument("--output_file", type=str, required=True)
    parser.add_argument("--lora_model", type=str, default="")
    parser.add_argument("--tokenizer_path", type=str, default=None)
    parser.add_argument("--system_prompt_file", type=str, default=None)
    parser.add_argument("--system_prompt", type=str, default="")
    parser.add_argument("--max_new_tokens", type=int, default=512)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--repetition_penalty", type=float, default=1.0)
    parser.add_argument("--eval_batch_size", type=int, default=4)
    parser.add_argument("--load_in_4bit", action="store_true")
    parser.add_argument("--load_in_8bit", action="store_true")
    args = parser.parse_args()

    tokenizer_path = args.tokenizer_path or args.base_model
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, trust_remote_code=True, padding_side="left")

    config_kwargs = {
        "trust_remote_code": True,
        "torch_dtype": "auto",
        "low_cpu_mem_usage": True,
        "device_map": "auto",
    }
    if args.load_in_8bit:
        config_kwargs["quantization_config"] = BitsAndBytesConfig(load_in_8bit=True)
    elif args.load_in_4bit:
        config_kwargs["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
        )

    base_model = AutoModelForCausalLM.from_pretrained(args.base_model, **config_kwargs)
    try:
        base_model.generation_config = GenerationConfig.from_pretrained(args.base_model, trust_remote_code=True)
    except OSError:
        pass

    if args.lora_model:
        model = PeftModel.from_pretrained(base_model, args.lora_model, torch_dtype="auto", device_map="auto")
    else:
        model = base_model
    model.eval()

    system_prompt = args.system_prompt
    if args.system_prompt_file:
        system_prompt = load_text(args.system_prompt_file)

    samples = load_jsonl(args.eval_file)
    prompts = [sample["instruction"] for sample in samples]
    output_path = Path(args.output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        output_path.unlink()

    for start in tqdm(range(0, len(prompts), args.eval_batch_size), desc="Running inference"):
        batch_samples = samples[start:start + args.eval_batch_size]
        batch_prompts = prompts[start:start + args.eval_batch_size]
        outputs = batch_generate_answer(
            batch_prompts,
            model,
            tokenizer,
            system_prompt,
            model.device,
            max_new_tokens=args.max_new_tokens,
            temperature=args.temperature,
            repetition_penalty=args.repetition_penalty,
            stop_str="</s>",
        )
        with open(output_path, "a", encoding="utf-8") as f:
            for sample, output in zip(batch_samples, outputs):
                record = {
                    "id": sample.get("id"),
                    "instruction": sample["instruction"],
                    "output": output,
                }
                json.dump(record, f, ensure_ascii=False)
                f.write("\n")


if __name__ == "__main__":
    main()
