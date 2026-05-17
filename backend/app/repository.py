from __future__ import annotations

from .database import get_connection, json_dump, json_load
from .schemas import ReferenceIn


def ensure_category(conn, name: str) -> int:
    conn.execute("INSERT OR IGNORE INTO categories(name) VALUES (?)", (name.strip(),))
    row = conn.execute("SELECT id FROM categories WHERE name = ?", (name.strip(),)).fetchone()
    return int(row["id"])


def replace_tags(conn, reference_id: int, tags: list[str]) -> None:
    conn.execute("DELETE FROM reference_tags WHERE reference_id = ?", (reference_id,))
    for tag in clean_list(tags):
        conn.execute("INSERT OR IGNORE INTO tags(name) VALUES (?)", (tag,))
        tag_id = conn.execute("SELECT id FROM tags WHERE name = ?", (tag,)).fetchone()["id"]
        conn.execute(
            "INSERT OR IGNORE INTO reference_tags(reference_id, tag_id) VALUES (?, ?)",
            (reference_id, tag_id),
        )


def replace_associations(conn, reference_id: int, associations: list[str]) -> None:
    conn.execute("DELETE FROM associations WHERE reference_id = ?", (reference_id,))
    conn.executemany(
        "INSERT INTO associations(reference_id, label) VALUES (?, ?)",
        [(reference_id, label) for label in clean_list(associations)],
    )


def clean_list(values: list[str]) -> list[str]:
    return [value.strip() for value in values if value and value.strip()]


def create_reference(payload: ReferenceIn) -> dict:
    with get_connection() as conn:
        category_id = ensure_category(conn, payload.category)
        cursor = conn.execute(
            """
            INSERT INTO "references"(title, category_id, description, numeric_refs, subcategories, notes)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                payload.title.strip(),
                category_id,
                payload.description.strip(),
                payload.numeric_refs.strip(),
                json_dump(clean_list(payload.subcategories)),
                payload.notes.strip(),
            ),
        )
        reference_id = int(cursor.lastrowid)
        replace_tags(conn, reference_id, payload.tags)
        replace_associations(conn, reference_id, payload.associations)
        rebuild_fts(conn, reference_id)
        return get_reference_by_id(reference_id, conn)


def update_reference(reference_id: int, payload: ReferenceIn) -> dict | None:
    with get_connection() as conn:
        if not conn.execute('SELECT id FROM "references" WHERE id = ?', (reference_id,)).fetchone():
            return None
        category_id = ensure_category(conn, payload.category)
        conn.execute(
            """
            UPDATE "references"
            SET title = ?, category_id = ?, description = ?, numeric_refs = ?,
                subcategories = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                payload.title.strip(),
                category_id,
                payload.description.strip(),
                payload.numeric_refs.strip(),
                json_dump(clean_list(payload.subcategories)),
                payload.notes.strip(),
                reference_id,
            ),
        )
        replace_tags(conn, reference_id, payload.tags)
        replace_associations(conn, reference_id, payload.associations)
        rebuild_fts(conn, reference_id)
        return get_reference_by_id(reference_id, conn)


def delete_reference(reference_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.execute('DELETE FROM "references" WHERE id = ?', (reference_id,))
        conn.execute("DELETE FROM references_fts WHERE rowid = ?", (reference_id,))
        return cursor.rowcount > 0


def list_references() -> list[dict]:
    with get_connection() as conn:
        ids = conn.execute('SELECT id FROM "references" ORDER BY updated_at DESC, title ASC').fetchall()
        return [get_reference_by_id(int(row["id"]), conn) for row in ids]


def get_reference(reference_id: int) -> dict | None:
    with get_connection() as conn:
        return get_reference_by_id(reference_id, conn)


def get_reference_by_id(reference_id: int, conn) -> dict | None:
    row = conn.execute(
        """
        SELECT r.id, r.title, c.name AS category, r.description, r.numeric_refs,
               r.subcategories, r.notes
        FROM "references" r
        LEFT JOIN categories c ON c.id = r.category_id
        WHERE r.id = ?
        """,
        (reference_id,),
    ).fetchone()
    if not row:
        return None
    tags = [item["name"] for item in conn.execute(
        """
        SELECT t.name FROM tags t
        JOIN reference_tags rt ON rt.tag_id = t.id
        WHERE rt.reference_id = ?
        ORDER BY t.name
        """,
        (reference_id,),
    ).fetchall()]
    associations = [item["label"] for item in conn.execute(
        "SELECT label FROM associations WHERE reference_id = ? ORDER BY id",
        (reference_id,),
    ).fetchall()]
    documents = [dict(item) for item in conn.execute(
        "SELECT id, filename, stored_path, mime_type, ocr_text, created_at FROM documents WHERE reference_id = ? ORDER BY created_at DESC",
        (reference_id,),
    ).fetchall()]
    return {
        "id": int(row["id"]),
        "title": row["title"],
        "category": row["category"] or "",
        "description": row["description"],
        "numeric_refs": row["numeric_refs"],
        "subcategories": json_load(row["subcategories"]),
        "tags": tags,
        "associations": associations,
        "notes": row["notes"],
        "documents": documents,
    }


def rebuild_fts(conn, reference_id: int) -> None:
    ref = get_reference_by_id(reference_id, conn)
    if not ref:
        return
    ocr_text = "\n".join(doc.get("ocr_text", "") for doc in ref["documents"])
    conn.execute("DELETE FROM references_fts WHERE rowid = ?", (reference_id,))
    conn.execute(
        """
        INSERT INTO references_fts(
          rowid, title, category, description, numeric_refs, subcategories,
          tags, associations, notes, ocr_text
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            reference_id,
            ref["title"],
            ref["category"],
            ref["description"],
            ref["numeric_refs"],
            " ".join(ref["subcategories"]),
            " ".join(ref["tags"]),
            " ".join(ref["associations"]),
            ref["notes"],
            ocr_text,
        ),
    )


def search_references(query: str) -> list[dict]:
    q = query.strip()
    if not q:
        return list_references()
    tokens = [token.replace('"', "") for token in q.split() if token.strip()]
    fts_query = " OR ".join(f'"{token}"*' for token in tokens)
    with get_connection() as conn:
        try:
            rows = conn.execute(
                """
                SELECT rowid, bm25(references_fts, 9.0, 8.0, 4.0, 7.0, 5.0, 8.0, 2.0, 1.0, 1.0) AS score
                FROM references_fts
                WHERE references_fts MATCH ?
                ORDER BY score
                LIMIT 50
                """,
                (fts_query,),
            ).fetchall()
        except Exception:
            like = f"%{q}%"
            rows = conn.execute(
                """
                SELECT DISTINCT r.id AS rowid
                FROM "references" r
                LEFT JOIN categories c ON c.id = r.category_id
                LEFT JOIN reference_tags rt ON rt.reference_id = r.id
                LEFT JOIN tags t ON t.id = rt.tag_id
                LEFT JOIN associations a ON a.reference_id = r.id
                WHERE r.title LIKE ? OR c.name LIKE ? OR r.numeric_refs LIKE ?
                   OR r.description LIKE ? OR r.subcategories LIKE ? OR t.name LIKE ? OR a.label LIKE ?
                LIMIT 50
                """,
                (like, like, like, like, like, like, like),
            ).fetchall()
        return [get_reference_by_id(int(row["rowid"]), conn) for row in rows]


def attach_document(reference_id: int | None, filename: str, stored_path: str, mime_type: str, ocr_text: str) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO documents(reference_id, filename, stored_path, mime_type, ocr_text)
            VALUES (?, ?, ?, ?, ?)
            """,
            (reference_id, filename, stored_path, mime_type, ocr_text),
        )
        if reference_id:
            rebuild_fts(conn, reference_id)
        return int(cursor.lastrowid)
