import argparse
import csv
import sqlite3
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build SQLite evaluation databases from schema.sql and CSV seeds.")
    parser.add_argument("--seed_root", default="project_data/eval/db_seeds")
    parser.add_argument("--output_root", default="project_data/eval/dbs")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def load_csv_rows(path: Path) -> tuple[list[str], list[list[str]]]:
    with open(path, "r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        rows = list(reader)
    if not rows:
        raise ValueError(f"CSV file is empty: {path}")
    return rows[0], rows[1:]


def build_single_database(seed_dir: Path, output_path: Path, overwrite: bool) -> None:
    schema_path = seed_dir / "schema.sql"
    if not schema_path.exists():
        raise FileNotFoundError(f"Missing schema.sql in {seed_dir}")
    if output_path.exists():
        if overwrite:
            output_path.unlink()
        else:
            return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(output_path) as connection:
        connection.executescript(schema_path.read_text(encoding="utf-8"))
        for csv_path in sorted(seed_dir.glob("*.csv")):
            table_name = csv_path.stem
            header, rows = load_csv_rows(csv_path)
            placeholders = ", ".join(["?"] * len(header))
            quoted_columns = ", ".join(f'"{column}"' for column in header)
            connection.executemany(
                f'INSERT INTO "{table_name}" ({quoted_columns}) VALUES ({placeholders})',
                rows,
            )
        connection.commit()


def main() -> None:
    args = parse_args()
    seed_root = Path(args.seed_root)
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    for seed_dir in sorted(path for path in seed_root.iterdir() if path.is_dir()):
        output_path = output_root / f"{seed_dir.name}.sqlite"
        build_single_database(seed_dir, output_path, overwrite=args.overwrite)
        print(f"Built {output_path}")


if __name__ == "__main__":
    main()
