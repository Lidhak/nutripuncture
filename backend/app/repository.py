from __future__ import annotations

import re
import unicodedata

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


def normalize_search_text(value: str) -> str:
    value = value.replace("œ", "oe").replace("Œ", "OE").replace("æ", "ae").replace("Æ", "AE")
    without_accents = "".join(
        char for char in unicodedata.normalize("NFKD", value.lower())
        if not unicodedata.combining(char)
    )
    normalized = re.sub(r"[^a-z0-9]+", " ", without_accents)
    return re.sub(r"\s+", " ", normalized).strip()


def compact_digits(value: str) -> str:
    return re.sub(r"\D+", "", value)


def searchable_blob(item: dict) -> str:
    document_text = " ".join(doc.get("ocr_text", "") for doc in item.get("documents", []))
    values = [
        item.get("title", ""),
        item.get("category", ""),
        item.get("description", ""),
        item.get("numeric_refs", ""),
        " ".join(item.get("subcategories", [])),
        " ".join(item.get("tags", [])),
        " ".join(item.get("associations", [])),
        item.get("notes", ""),
        document_text,
    ]
    return " ".join(values)


def score_reference(item: dict, query: str) -> int:
    normalized_query = normalize_search_text(query)
    if not normalized_query:
        return 1

    document_blob = " ".join(doc.get("ocr_text", "") for doc in item.get("documents", []))
    normalized_blob = normalize_search_text(searchable_blob(item))
    normalized_title = normalize_search_text(item.get("title", ""))
    normalized_category = normalize_search_text(item.get("category", ""))
    normalized_tags = normalize_search_text(" ".join(item.get("tags", [])))
    normalized_subcategories = normalize_search_text(" ".join(item.get("subcategories", [])))
    normalized_associations = normalize_search_text(" ".join(item.get("associations", [])))
    normalized_primary_codes = normalize_search_text(item.get("numeric_refs", ""))
    normalized_notes = normalize_search_text(item.get("notes", ""))
    normalized_documents = normalize_search_text(document_blob)
    compact_query = compact_digits(query)
    compact_primary_codes = compact_digits(item.get("numeric_refs", ""))
    compact_notes = compact_digits(item.get("notes", ""))
    compact_documents = compact_digits(document_blob)
    tokens = normalized_query.split()
    words = normalized_blob.split()
    title_words = normalized_title.split()
    score = 0

    if normalized_title == normalized_query:
        score += 700
    if normalized_title.startswith(normalized_query):
        score += 500
    if normalized_query in normalized_title:
        score += 350
    if tokens and all(any(word.startswith(token) for word in title_words) for token in tokens):
        score += 620
    if normalized_query in normalized_category:
        score += 220
    if normalized_query in normalized_tags:
        score += 260
    if normalized_query in normalized_subcategories:
        score += 240
    if normalized_query in normalized_associations:
        score += 200
    for normalized_field, field_boost in (
        (normalized_tags, 280),
        (normalized_subcategories, 260),
        (normalized_associations, 220),
    ):
        field_words = normalized_field.split()
        if tokens and all(any(word.startswith(token) for word in field_words) for token in tokens):
            score += field_boost
    if any(token.isdigit() for token in tokens):
        if normalized_query in normalized_primary_codes:
            score += 1100
        elif normalized_query in normalized_notes:
            score += 520
        elif normalized_query in normalized_documents:
            score += 160
    if compact_query and len(compact_query) >= 2:
        if compact_primary_codes.startswith(compact_query):
            score += 1200
        elif compact_query in compact_primary_codes:
            score += 850
        elif compact_query in compact_notes:
            score += 420
        elif compact_query in compact_documents:
            score += 130
    if normalized_query in normalized_blob:
        score += 180

    matched_tokens = 0
    for token in tokens:
        if any(word.startswith(token) for word in words):
            matched_tokens += 1
            score += 35
    if tokens and matched_tokens == len(tokens):
        score += 160
    elif tokens and matched_tokens:
        score += matched_tokens * 10

    return score


def build_match_context(item: dict, query: str) -> str:
    normalized_query = normalize_search_text(query)
    compact_query = compact_digits(query)
    tokens = normalized_query.split()
    candidates = []
    candidates.extend(item.get("subcategories", []))
    candidates.extend(item.get("associations", []))
    candidates.append(item.get("numeric_refs", ""))
    candidates.extend((item.get("notes", "") or "").splitlines())
    for doc in item.get("documents", []):
        candidates.extend((doc.get("ocr_text", "") or "").splitlines())

    best = ""
    best_score = 0
    for line in candidates:
        clean = " ".join(line.split())
        if not clean:
            continue
        normalized_line = normalize_search_text(clean)
        compact_line = compact_digits(clean)
        line_score = 0
        if normalized_query and normalized_query in normalized_line:
            line_score += 20
        if compact_query and compact_query in compact_line:
            line_score += 18
        line_score += sum(1 for token in tokens if any(word.startswith(token) for word in normalized_line.split()))
        if line_score > best_score:
            best = clean
            best_score = line_score
    return best[:260]


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


def upsert_reference(payload: ReferenceIn) -> dict:
    with get_connection() as conn:
        row = conn.execute(
            'SELECT id FROM "references" WHERE lower(title) = lower(?)',
            (payload.title.strip(),),
        ).fetchone()
    if row:
        item = update_reference(int(row["id"]), payload)
        if item:
            return item
    return create_reference(payload)


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


def get_reference_by_title(title: str) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            'SELECT id FROM "references" WHERE lower(title) = lower(?)',
            (title.strip(),),
        ).fetchone()
        if not row:
            return None
        return get_reference_by_id(int(row["id"]), conn)


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
        all_ids = conn.execute('SELECT id FROM "references"').fetchall()
        all_items = [get_reference_by_id(int(row["id"]), conn) for row in all_ids]
        scored_items = []
        for item in all_items:
            if not item:
                continue
            score = score_reference(item, q)
            if score > 0:
                item["match_context"] = build_match_context(item, q)
                scored_items.append((score, item["title"], item))
        if scored_items:
            scored_items.sort(key=lambda row: (-row[0], row[1]))
            return [item for _, _, item in scored_items[:50]]

        try:
            rows = conn.execute(
                """
                SELECT
                  rowid,
                  bm25(references_fts, 9.0, 8.0, 4.0, 7.0, 5.0, 8.0, 2.0, 1.0, 1.0) AS score,
                  (
                    title || ' ' || category || ' ' || description || ' ' || numeric_refs || ' ' ||
                    subcategories || ' ' || tags || ' ' || associations || ' ' || notes || ' ' || ocr_text
                  ) LIKE ? AS exact_match
                FROM references_fts
                WHERE references_fts MATCH ?
                ORDER BY exact_match DESC, score
                LIMIT 50
                """,
                (f"%{q}%", fts_query),
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


def attach_document_once(reference_id: int | None, filename: str, stored_path: str, mime_type: str, ocr_text: str) -> int:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT id FROM documents
            WHERE reference_id IS ? AND filename = ?
            """,
            (reference_id, filename),
        ).fetchone()
        if row:
            doc_id = int(row["id"])
            conn.execute(
                """
                UPDATE documents
                SET stored_path = ?, mime_type = ?, ocr_text = ?
                WHERE id = ?
                """,
                (stored_path, mime_type, ocr_text, doc_id),
            )
        else:
            cursor = conn.execute(
                """
                INSERT INTO documents(reference_id, filename, stored_path, mime_type, ocr_text)
                VALUES (?, ?, ?, ?, ?)
                """,
                (reference_id, filename, stored_path, mime_type, ocr_text),
            )
            doc_id = int(cursor.lastrowid)
        if reference_id:
            rebuild_fts(conn, reference_id)
        return doc_id
