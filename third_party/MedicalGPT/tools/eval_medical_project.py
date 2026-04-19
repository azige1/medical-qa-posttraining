import argparse
import json
from pathlib import Path


REQUIRED_KEYS = ["question_type", "answer", "key_points", "triage_level", "safety_notice"]


def load_jsonl(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def normalize_text(text):
    if text is None:
        return ""
    if isinstance(text, list):
        return " ".join(str(x) for x in text)
    return str(text)


def parse_structured_output(output: str):
    try:
        parsed = json.loads(output)
    except Exception:
        return None
    if not isinstance(parsed, dict):
        return None
    for key in REQUIRED_KEYS:
        if key not in parsed:
            return None
    if not isinstance(parsed.get("key_points"), list):
        return None
    return parsed


def ratio(numerator, denominator):
    return round(numerator / denominator, 4) if denominator else 0.0


def main():
    parser = argparse.ArgumentParser(description="Lightweight evaluator for the medical QA project.")
    parser.add_argument("--eval_file", type=str, required=True)
    parser.add_argument("--prediction_file", type=str, required=True)
    parser.add_argument("--report_file", type=str, required=True)
    parser.add_argument("--error_file", type=str, required=True)
    args = parser.parse_args()

    eval_samples = load_jsonl(args.eval_file)
    predictions = load_jsonl(args.prediction_file)
    prediction_map = {}
    for row in predictions:
        key = row.get("id") or row.get("instruction") or row.get("Input")
        prediction_map[key] = row

    total = len(eval_samples)
    structure_pass = 0
    question_type_match = 0
    triage_match = 0
    must_include_hits = 0
    must_include_total = 0
    forbidden_violations = 0
    key_point_hits = 0
    key_point_total = 0
    errors = []

    for sample in eval_samples:
        key = sample.get("id") or sample["instruction"]
        pred_row = prediction_map.get(key, {})
        output = pred_row.get("output") or pred_row.get("Output") or ""
        structured = parse_structured_output(output)
        raw_text = normalize_text(output)

        if structured is not None:
            structure_pass += 1
            if structured.get("question_type") == sample.get("question_type"):
                question_type_match += 1
            if structured.get("triage_level") == sample.get("triage_level"):
                triage_match += 1
            answer_zone = " ".join(
                [
                    normalize_text(structured.get("answer")),
                    normalize_text(structured.get("key_points")),
                    normalize_text(structured.get("safety_notice")),
                ]
            )
        else:
            answer_zone = raw_text

        for phrase in sample.get("must_include", []):
            must_include_total += 1
            if phrase in answer_zone:
                must_include_hits += 1

        for phrase in sample.get("forbidden", []):
            if phrase in answer_zone:
                forbidden_violations += 1

        for point in sample.get("reference_key_points", []):
            key_point_total += 1
            if point in answer_zone:
                key_point_hits += 1

        if structured is None or any(
            phrase in answer_zone for phrase in sample.get("forbidden", [])
        ):
            errors.append(
                {
                    "id": sample.get("id"),
                    "instruction": sample.get("instruction"),
                    "output": output,
                    "structure_pass": structured is not None,
                    "forbidden_hit": [p for p in sample.get("forbidden", []) if p in answer_zone],
                }
            )

    report = {
        "total_samples": total,
        "structure_pass_rate": ratio(structure_pass, total),
        "question_type_match_rate": ratio(question_type_match, total),
        "triage_match_rate": ratio(triage_match, total),
        "must_include_hit_rate": ratio(must_include_hits, must_include_total),
        "reference_key_point_hit_rate": ratio(key_point_hits, key_point_total),
        "forbidden_violation_rate": ratio(forbidden_violations, total),
    }

    report_path = Path(args.report_file)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    error_path = Path(args.error_file)
    error_path.parent.mkdir(parents=True, exist_ok=True)
    with open(error_path, "w", encoding="utf-8") as f:
        for row in errors:
            json.dump(row, f, ensure_ascii=False)
            f.write("\n")


if __name__ == "__main__":
    main()
