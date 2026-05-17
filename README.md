# Nutripuncture Desk

POC desktop offline-first pour un cabinet d'osteopathie utilisant la nutripuncture.

## Stack

- Frontend: React, Vite, TailwindCSS, composants type shadcn/ui
- Backend: FastAPI
- Base locale: SQLite + FTS5
- Desktop: Tauri
- OCR: Tesseract via `pytesseract` si installe, fallback texte pour PDF

## Structure

```text
backend/       API FastAPI, SQLite, OCR, seed
frontend/      Interface React moderne
database/      Schema SQLite
uploads/       Documents importes localement
ocr/           Notes et zone OCR
src-tauri/     Packaging desktop Tauri
scripts/       Lancement local
```

## Lancement rapide

Tout lancer en une commande:

```bash
bash scripts/start_app.sh
```

Puis ouvrir `http://127.0.0.1:5173`.

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.seed
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

La base SQLite est creee automatiquement dans `database/nutripuncture.db`.

### Frontend

Node.js est requis.

```bash
cd frontend
npm install
npm run dev
```

Puis ouvrir `http://127.0.0.1:5173`.

### Tauri

Rust, Node.js et les prerequis systeme Tauri sont requis.

```bash
cd frontend
npm install
npm run tauri:dev
```

Garder le backend lance dans un terminal separe pendant `tauri:dev`.

Construire les paquets desktop Linux:

```bash
cd frontend
npm run tauri:build
```

Les artefacts sont generes dans `src-tauri/target/release/bundle/`.

## OCR

Pour l'OCR image, installer Tesseract localement:

- macOS: `brew install tesseract tesseract-lang`
- Ubuntu/Debian: `sudo apt install tesseract-ocr tesseract-ocr-fra`
- Windows: installer Tesseract puis ajouter l'executable au `PATH`

Sans Tesseract, l'upload fonctionne et le document est indexe avec les metadonnees disponibles. Pour les PDF, le POC extrait le texte natif via `pypdf`.

## API

- `GET /references`
- `GET /search?q=...`
- `GET /references/{id}`
- `POST /references`
- `PUT /references/{id}`
- `DELETE /references/{id}`
- `POST /documents/upload`
- `GET /health`

## Donnees de demo

Le seed integre les fiches:

- TEST PREPROBIO
- CERVEAU ENTERIQUE
- MEMOIRES DU SANG
- SONAR EPIPHYSAIRE
- MOUVEMENTS ARCHETYPAUX
- COLONNE VERTEBRALE

La recherche couvre titre, categorie, references numeriques, sous-categories, associations, tags, notes et texte OCR.
