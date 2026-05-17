from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[2]
DATABASE_DIR = ROOT_DIR / "database"
UPLOAD_DIR = ROOT_DIR / "uploads"
DB_PATH = DATABASE_DIR / "nutripuncture.db"
SCHEMA_PATH = DATABASE_DIR / "schema.sql"


def ensure_directories() -> None:
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    ensure_directories()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    ensure_directories()
    with get_connection() as conn:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        migrate_db(conn)


def migrate_db(conn: sqlite3.Connection) -> None:
    columns = {row["name"] for row in conn.execute("PRAGMA table_info(documents)").fetchall()}
    if "ocr_status" not in columns:
        conn.execute("ALTER TABLE documents ADD COLUMN ocr_status TEXT NOT NULL DEFAULT 'pending'")
    if "ocr_engine" not in columns:
        conn.execute("ALTER TABLE documents ADD COLUMN ocr_engine TEXT NOT NULL DEFAULT ''")
    conn.execute(
        """
        UPDATE documents
        SET ocr_status = 'ok', ocr_engine = 'existing'
        WHERE ocr_text <> '' AND (ocr_status = 'pending' OR ocr_status = '')
        """
    )
    conn.execute(
        """
        UPDATE documents
        SET ocr_status = 'failed'
        WHERE ocr_text LIKE 'OCR % indisponible:%'
           OR ocr_text LIKE 'OCR PDF scanne indisponible:%'
        """
    )


def json_dump(values: list[str] | None) -> str:
    return json.dumps(values or [], ensure_ascii=False)


def json_load(value: str | None) -> list[str]:
    if not value:
        return []
    try:
        loaded = json.loads(value)
        return loaded if isinstance(loaded, list) else []
    except json.JSONDecodeError:
        return []


def row_to_dict(row: sqlite3.Row | dict[str, Any]) -> dict[str, Any]:
    return dict(row)
