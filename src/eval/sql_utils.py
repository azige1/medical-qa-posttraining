import json
import re
import sqlite3
from pathlib import Path
from typing import Any, Iterable


DANGEROUS_SQL_PATTERN = re.compile(
    r"\b(insert|update|delete|drop|alter|create|replace|truncate|attach|detach|pragma)\b",
    re.IGNORECASE,
)
SCHEMA_ERROR_PATTERN = re.compile(r"no such table|no such column", re.IGNORECASE)
CODE_BLOCK_PATTERN = re.compile(r"```(?:sql)?\s*(.*?)```", re.IGNORECASE | re.DOTALL)


def load_json(path: str | Path) -> Any:
    with open(path, "r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    rows = []
    with open(path, "r", encoding="utf-8-sig") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def dump_jsonl(path: str | Path, rows: Iterable[dict[str, Any]]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        for row in rows:
            json.dump(row, handle, ensure_ascii=False)
            handle.write("\n")


def load_text(path: str | Path) -> str:
    with open(path, "r", encoding="utf-8-sig") as handle:
        return handle.read().strip()


def resolve_path(path_str: str, base_dir: str | Path | None = None) -> Path:
    candidate = Path(path_str)
    if candidate.is_absolute():
        return candidate
    if base_dir is None:
        return candidate.resolve()
    return (Path(base_dir) / candidate).resolve()


def render_text2sql_prompt(sample: dict[str, Any]) -> str:
    db_id = sample.get("db_id", "")
    schema_text = sample["schema_text"].strip()
    question = sample["question_zh"].strip()
    header = f"Database ID: {db_id}\n" if db_id else ""
    return (
        f"{header}"
        f"Database schema:\n{schema_text}\n\n"
        f"Question:\n{question}\n\n"
        "Output one SQLite SELECT SQL only."
    )


def _remove_code_fences(text: str) -> str:
    match = CODE_BLOCK_PATTERN.search(text)
    if match:
        return match.group(1).strip()
    return text.strip()


def normalize_predicted_sql(text: str | None) -> str:
    if text is None:
        return ""
    cleaned = _remove_code_fences(str(text))
    cleaned = cleaned.replace("\r", "\n").strip()
    if cleaned.lower().startswith("sql:"):
        cleaned = cleaned[4:].strip()
    match = re.search(r"\b(select|with)\b", cleaned, re.IGNORECASE)
    if match:
        cleaned = cleaned[match.start():].strip()
    statements = [part.strip() for part in cleaned.split(";") if part.strip()]
    if not statements:
        return ""
    return statements[0] + ";"


def statement_count(text: str) -> int:
    return len([part.strip() for part in text.split(";") if part.strip()])


def is_safe_select(sql: str) -> tuple[bool, str]:
    sql = normalize_predicted_sql(sql)
    if not sql:
        return False, "empty"
    lowered = sql.strip().lower()
    if statement_count(sql) != 1:
        return False, "multi_statement"
    if not (lowered.startswith("select") or lowered.startswith("with")):
        return False, "non_select"
    if DANGEROUS_SQL_PATTERN.search(sql):
        return False, "unsafe_keyword"
    return True, "ok"


def connect_readonly(db_path: str | Path) -> sqlite3.Connection:
    db_path = Path(db_path).resolve()
    uri = f"file:{db_path.as_posix()}?mode=ro"
    return sqlite3.connect(uri, uri=True)


def _normalize_value(value: Any) -> Any:
    if isinstance(value, float):
        return round(value, 6)
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def normalize_result(rows: Iterable[Iterable[Any]]) -> list[list[Any]]:
    normalized = []
    for row in rows:
        normalized.append([_normalize_value(cell) for cell in row])
    return normalized


def execute_sql(db_path: str | Path, sql: str) -> tuple[bool, list[list[Any]] | None, str | None]:
    try:
        with connect_readonly(db_path) as connection:
            cursor = connection.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
        return True, normalize_result(rows), None
    except Exception as exc:  # noqa: BLE001
        return False, None, str(exc)


def compare_results(pred_rows: list[list[Any]] | None, gold_rows: list[list[Any]] | None) -> bool:
    return pred_rows == gold_rows


def classify_sql_error(error_message: str | None) -> str:
    if not error_message:
        return "unknown"
    lowered = error_message.lower()
    if SCHEMA_ERROR_PATTERN.search(lowered):
        return "schema_hallucination"
    if "syntax error" in lowered:
        return "execution_failure"
    if "readonly" in lowered:
        return "unsafe_sql"
    return "execution_failure"
