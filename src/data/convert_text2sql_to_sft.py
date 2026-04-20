import argparse
import json
import random
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    with open(path, "r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def dump_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def dump_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        for row in rows:
            json.dump(row, handle, ensure_ascii=False)
            handle.write("\n")


def normalize_sql(sql: str) -> str:
    normalized = " ".join(sql.strip().split())
    if normalized and not normalized.endswith(";"):
        normalized += ";"
    return normalized


def build_schema_index(tables: list[dict[str, Any]]) -> dict[str, str]:
    schema_index = {}
    for db in tables:
        db_id = db["db_id"]
        table_names = db.get("table_names_original") or db.get("table_names") or []
        column_names = db.get("column_names_original") or db.get("column_names") or []
        column_types = db.get("column_types") or []
        primary_keys = set(db.get("primary_keys") or [])
        foreign_keys = db.get("foreign_keys") or []

        columns_by_table: dict[int, list[str]] = {idx: [] for idx in range(len(table_names))}
        for column_idx, column_info in enumerate(column_names):
            table_idx, column_name = column_info
            if table_idx < 0:
                continue
            column_type = column_types[column_idx] if column_idx < len(column_types) else ""
            suffix = []
            if column_type:
                suffix.append(column_type)
            if column_idx in primary_keys:
                suffix.append("primary key")
            rendered_column = column_name
            if suffix:
                rendered_column += f" ({', '.join(suffix)})"
            columns_by_table[table_idx].append(rendered_column)

        table_lines = []
        for table_idx, table_name in enumerate(table_names):
            rendered_columns = ", ".join(columns_by_table.get(table_idx, []))
            table_lines.append(f"TABLE {table_name}({rendered_columns});")

        fk_lines = []
        for source_col_idx, target_col_idx in foreign_keys:
            source_table_idx, source_col_name = column_names[source_col_idx]
            target_table_idx, target_col_name = column_names[target_col_idx]
            source_table = table_names[source_table_idx]
            target_table = table_names[target_table_idx]
            fk_lines.append(f"{source_table}.{source_col_name} = {target_table}.{target_col_name}")

        schema_text = "\n".join(table_lines)
        if fk_lines:
            schema_text += "\nFOREIGN KEYS:\n" + "\n".join(fk_lines)
        schema_index[db_id] = schema_text
    return schema_index


def build_prompt(db_id: str, schema_text: str, question: str) -> str:
    instruction = (
        "Given the database schema and the question, write one executable SQLite SQL query that answers the question. "
        "Only output SQL.\n"
        "根据给定数据库 schema 和问题，生成一条可执行的 SQLite SQL。只输出 SQL，不要解释。"
    )
    return (
        f"{instruction}\n\n"
        f"Database ID: {db_id}\n"
        f"Database schema:\n{schema_text}\n\n"
        f"Question:\n{question.strip()}"
    )


def infer_db_path(raw_dir: Path, db_id: str) -> str:
    sqlite_path = raw_dir / "database" / db_id / f"{db_id}.sqlite"
    return str(sqlite_path.as_posix()) if sqlite_path.exists() else ""


def convert_examples(
    examples: list[dict[str, Any]],
    schema_index: dict[str, str],
    raw_dir: Path,
    source_name: str,
    split_name: str,
) -> tuple[list[dict[str, Any]], int]:
    rows = []
    skipped = 0
    question_language = "zh" if source_name == "cspider" else "en"
    for idx, example in enumerate(examples):
        db_id = example.get("db_id")
        question = example.get("question") or example.get("question_zh")
        query = example.get("query")
        if not db_id or not question or not query:
            skipped += 1
            continue
        schema_text = schema_index.get(db_id)
        if not schema_text:
            skipped += 1
            continue
        gold_sql = normalize_sql(query)
        prompt = build_prompt(db_id, schema_text, question)
        rows.append(
            {
                "id": f"{source_name}_{split_name}_{idx}",
                "db_id": db_id,
                "db_path": infer_db_path(raw_dir, db_id),
                "schema_text": schema_text,
                "source_dataset": source_name,
                "source_split": split_name,
                "question_language": question_language,
                "original_question": question,
                "gold_sql": gold_sql,
                "conversations": [
                    {"from": "human", "value": prompt},
                    {"from": "gpt", "value": gold_sql},
                ],
            }
        )
    return rows, skipped


def maybe_limit_rows(rows: list[dict[str, Any]], limit: int, seed: int) -> list[dict[str, Any]]:
    if limit <= 0 or len(rows) <= limit:
        return rows
    rng = random.Random(seed)
    sampled = rows[:]
    rng.shuffle(sampled)
    return sampled[:limit]


def ensure_exists(path: Path, description: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Missing {description}: {path}")


def build_source_config(source_name: str, raw_dir: Path) -> dict[str, Any]:
    if source_name == "cspider":
        return {
            "tables_path": raw_dir / "tables.json",
            "train_files": [raw_dir / "train.json"],
            "val_files": [raw_dir / "dev.json"],
        }
    if source_name == "spider":
        return {
            "tables_path": raw_dir / "tables.json",
            "train_files": [raw_dir / "train_spider.json", raw_dir / "train_others.json"],
            "val_files": [raw_dir / "dev.json"],
        }
    raise ValueError(f"Unsupported source: {source_name}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert CSpider/Spider raw data into ShareGPT SFT jsonl.")
    parser.add_argument("--cspider_dir", type=str, default="project_data/raw/cspider")
    parser.add_argument("--spider_dir", type=str, default="project_data/raw/spider")
    parser.add_argument("--output_root", type=str, default="project_data/sft")
    parser.add_argument("--report_file", type=str, default="project_data/intermediate/sft_build_report_v1.json")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--spider_train_limit", type=int, default=5000)
    parser.add_argument("--spider_val_limit", type=int, default=1000)
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

    report: dict[str, Any] = {"seed": args.seed, "sources": {}}

    source_specs = []
    if not args.skip_cspider:
        source_specs.append(("cspider", Path(args.cspider_dir)))
    if not args.skip_spider:
        source_specs.append(("spider", Path(args.spider_dir)))

    if not source_specs:
        raise ValueError("At least one source must be enabled.")

    for source_name, raw_dir in source_specs:
        source_report: dict[str, Any] = {"raw_dir": str(raw_dir)}
        config = build_source_config(source_name, raw_dir)
        ensure_exists(config["tables_path"], f"{source_name} tables.json")
        tables = load_json(config["tables_path"])
        schema_index = build_schema_index(tables)

        train_examples = []
        for path in config["train_files"]:
            ensure_exists(path, f"{source_name} train split")
            train_examples.extend(load_json(path))
        val_examples = []
        for path in config["val_files"]:
            ensure_exists(path, f"{source_name} validation split")
            val_examples.extend(load_json(path))

        train_rows, train_skipped = convert_examples(train_examples, schema_index, raw_dir, source_name, "train")
        val_rows, val_skipped = convert_examples(val_examples, schema_index, raw_dir, source_name, "dev")

        if source_name == "spider":
            train_rows = maybe_limit_rows(train_rows, args.spider_train_limit, args.seed)
            val_rows = maybe_limit_rows(val_rows, args.spider_val_limit, args.seed)

        train_output = train_dir / f"{source_name}_train_sft_v1.jsonl"
        val_output = val_dir / f"{source_name}_dev_sft_v1.jsonl"
        dump_jsonl(train_output, train_rows)
        dump_jsonl(val_output, val_rows)

        source_report["schema_count"] = len(schema_index)
        source_report["train_examples_raw"] = len(train_examples)
        source_report["train_examples_written"] = len(train_rows)
        source_report["train_examples_skipped"] = train_skipped
        source_report["val_examples_raw"] = len(val_examples)
        source_report["val_examples_written"] = len(val_rows)
        source_report["val_examples_skipped"] = val_skipped
        source_report["train_output"] = str(train_output.as_posix())
        source_report["val_output"] = str(val_output.as_posix())
        report["sources"][source_name] = source_report

    dump_json(Path(args.report_file), report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
