import argparse
import json
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


def infer_db_path(raw_dir: Path, db_id: str) -> str:
    sqlite_path = raw_dir / "database" / db_id / f"{db_id}.sqlite"
    return str(sqlite_path.as_posix())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build execution-based eval jsonl from the official CSpider dev split.")
    parser.add_argument("--cspider_dir", type=str, default="project_data/raw/cspider")
    parser.add_argument("--output_file", type=str, default="project_data/eval/cspider_dev_exec_v1.jsonl")
    parser.add_argument("--report_file", type=str, default="project_data/intermediate/cspider_dev_exec_build_report_v1.json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    raw_dir = Path(args.cspider_dir)
    tables_path = raw_dir / "tables.json"
    dev_path = raw_dir / "dev.json"
    if not tables_path.exists():
        raise FileNotFoundError(f"Missing CSpider tables.json: {tables_path}")
    if not dev_path.exists():
        raise FileNotFoundError(f"Missing CSpider dev.json: {dev_path}")

    tables = load_json(tables_path)
    dev_rows = load_json(dev_path)
    schema_index = build_schema_index(tables)

    output_rows = []
    skipped = 0
    for idx, row in enumerate(dev_rows):
        db_id = row.get("db_id")
        question_zh = row.get("question")
        gold_sql = row.get("query")
        if not db_id or not question_zh or not gold_sql:
            skipped += 1
            continue
        schema_text = schema_index.get(db_id)
        if not schema_text:
            skipped += 1
            continue
        output_rows.append(
            {
                "id": f"cspider_dev_{idx}",
                "db_id": db_id,
                "db_path": infer_db_path(raw_dir, db_id),
                "question_zh": question_zh.strip(),
                "schema_text": schema_text,
                "gold_sql": normalize_sql(gold_sql),
                "source_dataset": "cspider",
                "source_split": "dev",
                "difficulty": "official_dev",
                "tags": [],
            }
        )

    dump_jsonl(Path(args.output_file), output_rows)
    report = {
        "raw_dir": str(raw_dir.as_posix()),
        "tables_path": str(tables_path.as_posix()),
        "dev_path": str(dev_path.as_posix()),
        "schema_count": len(schema_index),
        "dev_examples_raw": len(dev_rows),
        "dev_examples_written": len(output_rows),
        "dev_examples_skipped": skipped,
        "output_file": args.output_file,
    }
    dump_json(Path(args.report_file), report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
