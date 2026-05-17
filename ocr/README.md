# OCR

Le POC utilise `backend/app/ocr.py`.

- PDF texte natif: extraction via `pypdf`
- Images: OCR via Tesseract si disponible
- Texte extrait: stocke dans `documents.ocr_text` et indexe dans SQLite FTS5
