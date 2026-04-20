import argparse
import json
import random
import re
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data.convert_text2sql_to_sft import (  # noqa: E402
    build_prompt,
    build_source_config,
    build_schema_index,
    dump_json,
    dump_jsonl,
    ensure_exists,
    load_json,
    maybe_limit_rows,
    normalize_sql,
)
from src.eval.sql_utils import classify_sql_error, compare_results, execute_sql, is_safe_select  # noqa: E402


SQL_KEYWORD_PATTERN = re.compile(
    r"\b(select|from|where|group|by|order|limit|join|left|right|inner|outer|on|as|and|or|count|sum|avg|min|max|distinct)\b",
    re.IGNORECASE,
)
WHERE_PATTERN = re.compile(
    r"\bWHERE\b(.*?)(?=\bGROUP\s+BY\b|\bORDER\s+BY\b|\bLIMIT\b|$)",
    re.IGNORECASE | re.DOTALL,
)
LIMIT_PATTERN = re.compile(r"\bLIMIT\s+(\d+)\b", re.IGNORECASE)
ORDER_BY_PATTERN = re.compile(r"\bORDER\s+BY\b", re.IGNORECASE)
AGG_PATTERN = re.compile(r"\b(COUNT|SUM|AVG|MIN|MAX)\s*\(", re.IGNORECASE)
ORDER_BY_CLAUSE_PATTERN = re.compile(
    r"(\bORDER\s+BY\b\s+.+?)(?=\bLIMIT\b|;|$)",
    re.IGNORECASE | re.DOTALL,
)
COMPARATOR_PATTERNS = (
    (re.compile(r">="), "<="),
    (re.compile(r"<="), ">="),
    (re.compile(r"!="), "="),
    (re.compile(r"<>"), "="),
    (re.compile(r"(?<![<>!])=(?!=)"), "!="),
    (re.compile(r">"), "<"),
    (re.compile(r"<"), ">"),
)
IDENTIFIER_PATTERN = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")


def build_schema_meta(tables: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    meta_index: dict[str, dict[str, Any]] = {}
    for db in tables:
        db_id = db["db_id"]
        table_names = db.get("table_names_original") or db.get("table_names") or []
        column_names = db.get("column_names_original") or db.get("column_names") or []

        table_to_columns: dict[str, list[str]] = {name: [] for name in table_names}
        all_columns: list[str] = []
        for table_idx, column_name in column_names:
            if table_idx < 0:
                continue
            table_name = table_names[table_idx]
            if column_name not in table_to_columns[table_name]:
                table_to_columns[table_name].append(column_name)
            if column_name not in all_columns:
                all_columns.append(column_name)

        meta_index[db_id] = {
            "tables": table_names,
            "table_to_columns": table_to_columns,
            "all_columns": all_columns,
        }
    return meta_index


def replace_first(pattern: re.Pattern[str], text: str, replacement: str) -> str | None:
    match = pattern.search(text)
    if not match:
        return None
    start, end = match.span(1 if match.lastindex else 0)
    return text[:start] + replacement + text[end:]


def perturb_limit(sql: str, _: dict[str, Any], rng: random.Random) -> str | None:
    match = LIMIT_PATTERN.search(sql)
    if not match:
        return None
    current = int(match.group(1))
    candidate = max(1, current + rng.choice([-2, -1, 1, 2, 3]))
    if candidate == current:
        candidate = current + 1
    return LIMIT_PATTERN.sub(f"LIMIT {candidate}", sql, count=1)


def perturb_order(sql: str, _: dict[str, Any], __: random.Random) -> str | None:
    if " DESC" in sql.upper():
        return re.sub(r"\bDESC\b", "ASC", sql, count=1, flags=re.IGNORECASE)
    if " ASC" in sql.upper():
        return re.sub(r"\bASC\b", "DESC", sql, count=1, flags=re.IGNORECASE)
    clause_match = ORDER_BY_CLAUSE_PATTERN.search(sql)
    if not clause_match:
        return None
    insert_pos = clause_match.end(1)
    return sql[:insert_pos] + " DESC" + sql[insert_pos:]


def perturb_where_operator(sql: str, _: dict[str, Any], __: random.Random) -> str | None:
    where_match = WHERE_PATTERN.search(sql)
    if not where_match:
        return None
    where_body = where_match.group(1)
    for pattern, replacement in COMPARATOR_PATTERNS:
        match = pattern.search(where_body)
        if match:
            start = where_match.start(1) + match.start()
            end = where_match.start(1) + match.end()
            return sql[:start] + replacement + sql[end:]
    return None


def perturb_drop_where(sql: str, _: dict[str, Any], __: random.Random) -> str | None:
    if " WHERE " not in sql.upper():
        return None
    return WHERE_PATTERN.sub("", sql, count=1)


def perturb_aggregate(sql: str, _: dict[str, Any], rng: random.Random) -> str | None:
    match = AGG_PATTERN.search(sql)
    if not match:
        return None
    current = match.group(1).upper()
    candidates = [name for name in ["COUNT", "SUM", "AVG", "MIN", "MAX"] if name != current]
    replacement = rng.choice(candidates)
    start, end = match.span(1)
    return sql[:start] + replacement + sql[end:]


def perturb_distinct(sql: str, _: dict[str, Any], __: random.Random) -> str | None:
    if re.search(r"\bDISTINCT\b", sql, flags=re.IGNORECASE):
        return re.sub(r"\bDISTINCT\b\s*", "", sql, count=1, flags=re.IGNORECASE)
    select_match = re.search(r"\bSELECT\b", sql, flags=re.IGNORECASE)
    if not select_match:
        return None
    insert_pos = select_match.end()
    return sql[:insert_pos] + " DISTINCT" + sql[insert_pos:]


def perturb_table(sql: str, schema_meta: dict[str, Any], rng: random.Random) -> str | None:
    tables = schema_meta["tables"]
    if len(tables) < 2:
        return None
    candidates = re.findall(r"\b(?:FROM|JOIN)\s+([A-Za-z_][A-Za-z0-9_]*)", sql, flags=re.IGNORECASE)
    if not candidates:
        return None
    current = candidates[0]
    replacements = [table for table in tables if table.lower() != current.lower()]
    if not replacements:
        return None
    replacement = rng.choice(replacements)
    return re.sub(
        rf"\b(FROM|JOIN)\s+{re.escape(current)}\b",
        lambda m: f"{m.group(1)} {replacement}",
        sql,
        count=1,
        flags=re.IGNORECASE,
    )


def perturb_column(sql: str, schema_meta: dict[str, Any], rng: random.Random) -> str | None:
    all_columns = schema_meta["all_columns"]
    if len(all_columns) < 2:
        return None

    identifier_matches = list(IDENTIFIER_PATTERN.finditer(sql))
    for match in identifier_matches:
        token = match.group(0)
        if SQL_KEYWORD_PATTERN.fullmatch(token):
            continue
        replacement_candidates = [name for name in all_columns if name.lower() != token.lower()]
        if token not in all_columns and not any(name.lower() == token.lower() for name in all_columns):
            continue
        if not replacement_candidates:
            continue
        replacement = rng.choice(replacement_candidates)
        start, end = match.span()
        return sql[:start] + replacement + sql[end:]
    return None


PERTURBERS: list[tuple[str, Any]] = [
    ("wrong_limit", perturb_limit),
    ("wrong_order", perturb_order),
    ("wrong_filter", perturb_where_operator),
    ("missing_filter", perturb_drop_where),
    ("wrong_aggregation", perturb_aggregate),
    ("distinct_change", perturb_distinct),
    ("wrong_column", perturb_column),
    ("wrong_table", perturb_table),
]


def choose_rejected_sql(
    gold_sql: str,
    db_path: str,
    schema_meta: dict[str, Any],
    rng: random.Random,
) -> tuple[str | None, str | None, str | None]:
    transform_order = PERTURBERS[:]
    rng.shuffle(transform_order)

    gold_exec_ok, gold_rows, gold_error = execute_sql(db_path, gold_sql)
    if not gold_exec_ok:
        return None, None, f"gold_sql_failed: {gold_error}"

    fallback_candidate = None
    fallback_error_type = None

    for transform_name, transform_fn in transform_order:
        candidate = transform_fn(gold_sql, schema_meta, rng)
        if not candidate:
            continue
        candidate = normalize_sql(candidate)
        if not candidate or candidate == gold_sql:
            continue
        is_safe, _ = is_safe_select(candidate)
        if not is_safe:
            continue

        exec_ok, candidate_rows, exec_error = execute_sql(db_path, candidate)
        if exec_ok and not compare_results(candidate_rows, gold_rows):
            return candidate, transform_name, None
        if not exec_ok:
            classified = classify_sql_error(exec_error)
            if classified in {"schema_hallucination", "execution_failure"} and fallback_candidate is None:
                fallback_candidate = candidate
                fallback_error_type = classified if transform_name in {"wrong_table", "wrong_column"} else transform_name

    if fallback_candidate:
        return fallback_candidate, fallback_error_type, None
    return None, None, "no_valid_rejected"


def build_rows_for_source(
    source_name: str,
    raw_dir: Path,
    seed: int,
    train_limit: int,
    validation_ratio: float,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    config = build_source_config(source_name, raw_dir)
    ensure_exists(config["tables_path"], f"{source_name} tables.json")
    tables = load_json(config["tables_path"])
    schema_index = build_schema_index(tables)
    schema_meta_index = build_schema_meta(tables)

    train_examples = []
    for path in config["train_files"]:
        ensure_exists(path, f"{source_name} train split")
        train_examples.extend(load_json(path))

    train_examples = maybe_limit_rows(train_examples, train_limit, seed)
    rng = random.Random(seed)
    rows = []
    skipped_missing = 0
    skipped_rejected = 0
    error_type_counts: dict[str, int] = {}

    for idx, example in enumerate(train_examples):
        db_id = example.get("db_id")
        question = example.get("question") or example.get("question_zh")
        query = example.get("query")
        if not db_id or not question or not query:
            skipped_missing += 1
            continue

        schema_text = schema_index.get(db_id)
        schema_meta = schema_meta_index.get(db_id)
        if not schema_text or not schema_meta:
            skipped_missing += 1
            continue

        gold_sql = normalize_sql(query)
        db_path = raw_dir / "database" / db_id / f"{db_id}.sqlite"
        if not db_path.exists():
            skipped_missing += 1
            continue

        rejected_sql, error_type, error_message = choose_rejected_sql(
            gold_sql=gold_sql,
            db_path=str(db_path),
            schema_meta=schema_meta,
            rng=rng,
        )
        if not rejected_sql or not error_type:
            skipped_rejected += 1
            continue

        prompt = build_prompt(db_id, schema_text, question)
        row = {
            "id": f"{source_name}_train_{idx}",
            "db_id": db_id,
            "db_path": str(db_path.as_posix()),
            "schema_text": schema_text,
            "source_dataset": source_name,
            "source_split": "train",
            "original_question": question,
            "gold_sql": gold_sql,
            "conversations": [{"from": "human", "value": prompt}],
            "chosen": gold_sql,
            "rejected": rejected_sql,
            "error_type": error_type,
            "rejected_source": "rule_based",
        }
        if error_message:
            row["note"] = error_message
        rows.append(row)
        error_type_counts[error_type] = error_type_counts.get(error_type, 0) + 1

    rng.shuffle(rows)
    validation_size = int(len(rows) * validation_ratio)
    validation_rows = rows[:validation_size]
    train_rows = rows[validation_size:]

    report = {
        "raw_dir": str(raw_dir.as_posix()),
        "train_examples_raw": len(train_examples),
        "rows_written": len(rows),
        "train_rows_written": len(train_rows),
        "val_rows_written": len(validation_rows),
        "skipped_missing_fields_or_schema": skipped_missing,
        "skipped_no_valid_rejected": skipped_rejected,
        "error_type_breakdown": error_type_counts,
    }
    return train_rows, validation_rows, report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Text-to-SQL preference data for DPO training.")
    parser.add_argument("--cspider_dir", type=str, default="project_data/raw/cspider")
    parser.add_argument("--spider_dir", type=str, default="project_data/raw/spider")
    parser.add_argument("--output_root", type=str, default="project_data/preference")
    parser.add_argument("--report_file", type=str, default="project_data/intermediate/preference_build_report_v1.json")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--validation_ratio", type=float, default=0.02)
    parser.add_argument("--cspider_train_limit", type=int, default=5000)
    parser.add_argument("--spider_train_limit", type=int, default=2000)
    parser.add_argument("--skip_cspider", action="store_true")
    parser.add_argument("--skip_spider", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_root = Path(args.output_root)
    train_dir = output_root / "train"
    val_dir = output_root / "val"
    train_dir.mkdir(parents=True, exist_ok=True)
    val_dir.mkdir(parents=True, exist_ok=True)

    source_specs = []
    if not args.skip_cspider:
        source_specs.append(("cspider", Path(args.cspider_dir), args.cspider_train_limit))
    if not args.skip_spider:
        source_specs.append(("spider", Path(args.spider_dir), args.spider_train_limit))
    if not source_specs:
        raise ValueError("At least one source must be enabled.")

    report: dict[str, Any] = {
        "seed": args.seed,
        "validation_ratio": args.validation_ratio,
        "sources": {},
    }

    for source_name, raw_dir, train_limit in source_specs:
        train_rows, validation_rows, source_report = build_rows_for_source(
            source_name=source_name,
            raw_dir=raw_dir,
            seed=args.seed,
            train_limit=train_limit,
            validation_ratio=args.validation_ratio,
        )

        train_output = train_dir / f"{source_name}_train_dpo_v1.jsonl"
        val_output = val_dir / f"{source_name}_val_dpo_v1.jsonl"
        dump_jsonl(train_output, train_rows)
        dump_jsonl(val_output, validation_rows)

        source_report["train_output"] = str(train_output.as_posix())
        source_report["val_output"] = str(val_output.as_posix())
        report["sources"][source_name] = source_report

    dump_json(Path(args.report_file), report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
