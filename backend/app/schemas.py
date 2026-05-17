from __future__ import annotations

from pydantic import BaseModel, Field


class ReferenceIn(BaseModel):
    title: str = Field(min_length=1)
    category: str = Field(min_length=1)
    description: str = ""
    numeric_refs: str = ""
    subcategories: list[str] = []
    tags: list[str] = []
    associations: list[str] = []
    notes: str = ""


class ReferenceOut(ReferenceIn):
    id: int
    documents: list[dict] = []


class UploadResponse(BaseModel):
    document_id: int
    filename: str
    stored_path: str
    ocr_text: str
