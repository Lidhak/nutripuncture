from __future__ import annotations

import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .database import ROOT_DIR, UPLOAD_DIR, init_db
from .ocr import extract_text
from .repository import (
    attach_document,
    create_reference,
    delete_reference,
    get_reference,
    list_references,
    search_references,
    update_reference,
)
from .schemas import ReferenceIn, ReferenceOut, UploadResponse
from .seed import seed

app = FastAPI(title="Nutripuncture Desk API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173", "tauri://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    seed()
    app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "database": str(ROOT_DIR / "database" / "nutripuncture.db")}


@app.get("/references", response_model=list[ReferenceOut])
def references() -> list[dict]:
    return list_references()


@app.get("/references/{reference_id}", response_model=ReferenceOut)
def reference(reference_id: int) -> dict:
    item = get_reference(reference_id)
    if not item:
        raise HTTPException(status_code=404, detail="Reference introuvable")
    return item


@app.get("/search", response_model=list[ReferenceOut])
def search(q: str = "") -> list[dict]:
    return search_references(q)


@app.post("/references", response_model=ReferenceOut)
def create(payload: ReferenceIn) -> dict:
    return create_reference(payload)


@app.put("/references/{reference_id}", response_model=ReferenceOut)
def update(reference_id: int, payload: ReferenceIn) -> dict:
    item = update_reference(reference_id, payload)
    if not item:
        raise HTTPException(status_code=404, detail="Reference introuvable")
    return item


@app.delete("/references/{reference_id}")
def delete(reference_id: int) -> dict:
    if not delete_reference(reference_id):
        raise HTTPException(status_code=404, detail="Reference introuvable")
    return {"deleted": True}


@app.post("/documents/upload", response_model=UploadResponse)
def upload_document(
    file: UploadFile = File(...),
    reference_id: int | None = Form(default=None),
) -> dict:
    init_db()
    suffix = Path(file.filename or "document").suffix
    stored_name = f"{uuid4().hex}{suffix}"
    stored_path = UPLOAD_DIR / stored_name
    with stored_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    ocr_text = extract_text(stored_path, file.content_type or "")
    doc_id = attach_document(
        reference_id=reference_id,
        filename=file.filename or stored_name,
        stored_path=f"/uploads/{stored_name}",
        mime_type=file.content_type or "",
        ocr_text=ocr_text,
    )
    return {
        "document_id": doc_id,
        "filename": file.filename or stored_name,
        "stored_path": f"/uploads/{stored_name}",
        "ocr_text": ocr_text,
    }
