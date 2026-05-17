from __future__ import annotations

from pathlib import Path


def extract_text(path: Path, mime_type: str) -> str:
    suffix = path.suffix.lower()
    if "pdf" in mime_type or suffix == ".pdf":
        return extract_pdf_text(path)
    if mime_type.startswith("image/") or suffix in {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}:
        return extract_image_text(path)
    return ""


def extract_pdf_text(path: Path) -> str:
    try:
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(text.strip() for text in pages if text.strip())
    except Exception as exc:
        return f"OCR PDF indisponible: {exc}"


def extract_image_text(path: Path) -> str:
    try:
        import pytesseract
        from PIL import Image

        with Image.open(path) as image:
            return pytesseract.image_to_string(image, lang="fra+eng").strip()
    except Exception as exc:
        return f"OCR image indisponible: {exc}"
