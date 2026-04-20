#!/usr/bin/env bash
set -euo pipefail

CSPIDER_DIR="${CSPIDER_DIR:-project_data/raw/cspider}"
SPIDER_DIR="${SPIDER_DIR:-project_data/raw/spider}"

fail() {
  echo "[FAIL] $1" >&2
  exit 1
}

check_file() {
  local path="$1"
  [ -f "$path" ] || fail "missing file: $path"
  echo "[OK] file: $path"
}

check_dir() {
  local path="$1"
  [ -d "$path" ] || fail "missing directory: $path"
  echo "[OK] dir: $path"
}

count_sqlite() {
  local path="$1"
  find "$path" -type f -name '*.sqlite' | wc -l | tr -d ' '
}

echo "[INFO] checking CSpider raw data"
check_dir "$CSPIDER_DIR"
check_file "$CSPIDER_DIR/train.json"
check_file "$CSPIDER_DIR/dev.json"
check_file "$CSPIDER_DIR/tables.json"
check_dir "$CSPIDER_DIR/database"

cspider_sqlite_count="$(count_sqlite "$CSPIDER_DIR/database")"
[ "$cspider_sqlite_count" -gt 0 ] || fail "no sqlite files found under $CSPIDER_DIR/database"
echo "[OK] CSpider sqlite count: $cspider_sqlite_count"

echo "[INFO] checking Spider raw data"
check_dir "$SPIDER_DIR"
check_file "$SPIDER_DIR/train_spider.json"
check_file "$SPIDER_DIR/train_others.json"
check_file "$SPIDER_DIR/dev.json"
check_file "$SPIDER_DIR/tables.json"
check_dir "$SPIDER_DIR/database"

spider_sqlite_count="$(count_sqlite "$SPIDER_DIR/database")"
[ "$spider_sqlite_count" -gt 0 ] || fail "no sqlite files found under $SPIDER_DIR/database"
echo "[OK] Spider sqlite count: $spider_sqlite_count"

echo "[DONE] raw data layout looks valid"
