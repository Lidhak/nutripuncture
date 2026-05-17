from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile


@dataclass(frozen=True)
class OcrResult:
    text: str
    status: str
    engine: str


def extract_text(path: Path, mime_type: str) -> OcrResult:
    suffix = path.suffix.lower()
    if "pdf" in mime_type or suffix == ".pdf":
        return extract_pdf_text(path)
    if mime_type.startswith("image/") or suffix in {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}:
        return extract_image_text(path)
    return OcrResult("", "unsupported", "none")


def extract_pdf_text(path: Path) -> OcrResult:
    native_text = ""
    try:
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages]
        native_text = "\n".join(text.strip() for text in pages if text.strip()).strip()
        if len(native_text) >= 80:
            return OcrResult(native_text, "ok", "pypdf")
    except Exception as exc:
        native_text = f"Extraction PDF native indisponible: {exc}"

    rendered = extract_scanned_pdf_text(path)
    if rendered.text:
        return rendered
    if native_text and not native_text.startswith("Extraction PDF native indisponible"):
        return OcrResult(native_text, "partial", "pypdf")
    return OcrResult(rendered.text or native_text, "failed", rendered.engine or "pypdf")


def extract_scanned_pdf_text(path: Path) -> OcrResult:
    try:
        import fitz
        from PIL import Image

        doc = fitz.open(str(path))
        page_texts = []
        for page_index, page in enumerate(doc):
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            text = run_tesseract(preprocess_image(image)).strip()
            if text:
                page_texts.append(f"[Page {page_index + 1}]\n{text}")
        text = "\n\n".join(page_texts).strip()
        return OcrResult(text, "ok" if text else "empty", "pymupdf+tesseract")
    except Exception as exc:
        return OcrResult(f"OCR PDF scanne indisponible: {exc}", "failed", "pymupdf+tesseract")


def extract_image_text(path: Path) -> OcrResult:
    try:
        from PIL import Image

        with Image.open(path) as image:
            text = run_tesseract(preprocess_image(image)).strip()
            return OcrResult(text, "ok" if text else "empty", "tesseract")
    except Exception as exc:
        return OcrResult(f"OCR image indisponible: {exc}", "failed", "tesseract")


def preprocess_image(image):
    from PIL import ImageOps

    normalized = ImageOps.exif_transpose(image)
    normalized = normalized.convert("L")
    normalized = ImageOps.autocontrast(normalized)
    normalized.format = "PNG"
    return normalized


def run_tesseract(image) -> str:
    import pytesseract

    with NamedTemporaryFile(suffix=".png", delete=True) as tmp:
        image.save(tmp.name, format="PNG")
        return pytesseract.image_to_string(tmp.name, lang="fra+eng")
