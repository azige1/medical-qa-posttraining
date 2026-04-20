import argparse
import json
import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.eval.sql_utils import classify_sql_error, compare_results, dump_jsonl, execute_sql, is_safe_select, load_jsonl, normalize_predicted_sql, resolve_path  # noqa: E402


def ratio(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 4) if denominator else 0.0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate Text-to-SQL predictions on SQLite databases.")
    parser.add_argument("--eval_file", required=True)
    parser.add_argument("--prediction_file", required=True)
    parser.add_argument("--report_file", required=True)
    parser.add_argument("--error_file", required=True)
    parser.add_argument("--report_to", default="none")
    parser.add_argument("--run_name", default="")
    return parser.parse_args()


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


def main() -> None:
    args = parse_args()
    wandb_run = maybe_init_wandb(args.report_to, args.run_name)
    eval_samples = load_jsonl(args.eval_file)
    predictions = load_jsonl(args.prediction_file)
    prediction_map = {row.get("id"): row for row in predictions}

    valid_sql = 0
    safe_sql = 0
    execution_success = 0
    execution_accuracy = 0
    schema_grounding = 0
    error_counts: dict[str, int] = {}
    error_rows = []

    for sample in eval_samples:
        sample_id = sample.get("id")
        pred_row = prediction_map.get(sample_id, {})
        raw_output = pred_row.get("raw_output") or pred_row.get("output") or ""
        pred_sql = pred_row.get("pred_sql") or normalize_predicted_sql(raw_output)
        db_path = resolve_path(sample["db_path"], PROJECT_ROOT)
        gold_sql = sample["gold_sql"]

        current_error = None
        if pred_sql:
            valid_sql += 1
        else:
            current_error = "non_sql"

        is_safe, reason = is_safe_select(pred_sql)
        if is_safe:
            safe_sql += 1
        elif current_error is None:
            current_error = "unsafe_sql" if reason != "empty" else "non_sql"

        pred_exec_ok = False
        pred_rows = None
        pred_error = None
        if is_safe:
            pred_exec_ok, pred_rows, pred_error = execute_sql(db_path, pred_sql)
            if pred_exec_ok:
                execution_success += 1
            else:
                current_error = classify_sql_error(pred_error)

        gold_exec_ok, gold_rows, gold_error = execute_sql(db_path, gold_sql)
        if not gold_exec_ok:
            raise RuntimeError(f"Gold SQL failed for sample {sample_id}: {gold_error}")

        if is_safe and (pred_exec_ok or current_error != "schema_hallucination"):
            schema_grounding += 1

        if pred_exec_ok and compare_results(pred_rows, gold_rows):
            execution_accuracy += 1
            current_error = "correct"
        elif pred_exec_ok and current_error is None:
            current_error = "wrong_result"

        error_counts[current_error] = error_counts.get(current_error, 0) + 1
        if current_error != "correct":
            error_rows.append(
                {
                    "id": sample_id,
                    "db_id": sample.get("db_id"),
                    "question_zh": sample.get("question_zh"),
                    "pred_sql": pred_sql,
                    "gold_sql": gold_sql,
                    "error_type": current_error,
                    "exec_error": pred_error,
                    "raw_output": raw_output,
                }
            )

    total = len(eval_samples)
    report = {
        "total_samples": total,
        "valid_sql_rate": ratio(valid_sql, total),
        "safe_sql_rate": ratio(safe_sql, total),
        "execution_success_rate": ratio(execution_success, total),
        "execution_accuracy": ratio(execution_accuracy, total),
        "schema_grounding_rate": ratio(schema_grounding, total),
        "error_breakdown": error_counts,
    }

    report_path = Path(args.report_file)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)

    dump_jsonl(args.error_file, error_rows)
    if wandb_run:
        metrics = {}
        for key, value in report.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    metrics[f"baseline_eval/{key}/{sub_key}"] = sub_value
            else:
                metrics[f"baseline_eval/{key}"] = value
        wandb_run.log(metrics)
        wandb_run.summary["baseline_eval/report_file"] = str(args.report_file)
        wandb_run.summary["baseline_eval/error_file"] = str(args.error_file)
        wandb_run.finish()


if __name__ == "__main__":
    main()
