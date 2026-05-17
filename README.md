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

## Notes projet

- `note_utilisateur_rapide.md` : procédure courte pour lancer et utiliser le POC.
- `synthese_prompt.md` : synthèse du besoin produit et technique.
- `note_de_carage.md` : cadrage plus large du projet et de ses évolutions IA.

## Lancement rapide

Tout lancer en une commande:

```bash
bash scripts/start_app.sh
```

Le navigateur s'ouvre automatiquement sur `http://127.0.0.1:5173`.

Installer un lanceur graphique Linux:

```bash
bash scripts/create_desktop_launcher.sh
```

Le praticien peut ensuite ouvrir `Nutripuncture Desk` depuis le menu des applications, sans saisir de commande.

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

### Installation Mac

Le logiciel cible un Mac en usage cabinet. Pour une livraison praticien, il faudra produire une application `.app` ou un installateur `.dmg`, construit depuis macOS.

Points à prévoir :

- build Tauri sur un Mac avec Xcode Command Line Tools ;
- backend FastAPI empaqueté comme sidecar, par exemple via PyInstaller ou équivalent ;
- Tesseract disponible localement avec les langues `fra` et `eng`, soit embarqué, soit installé via Homebrew ;
- stockage de `nutripuncture.db` et `uploads/` dans le dossier de données utilisateur de l'app, pas dans le dossier projet ;
- sauvegarde/restauration du dossier de données ;
- signature et notarisation Apple pour éviter les blocages Gatekeeper hors poste de développement.

Pour une démonstration technique sur Mac, l'installation minimale reste :

```bash
bash scripts/setup_mac.sh
```

Ce script installe les prérequis via Homebrew, prépare le backend/frontend, initialise la base et crée un lanceur double-clic `Nutripuncture Desk.command` sur le Bureau.

Pour le praticien final, cette étape doit disparaître au profit d'un double-clic sur l'application.

## OCR et controle apres import

Pour l'OCR image, installer Tesseract localement:

- macOS: `brew install tesseract tesseract-lang`
- Ubuntu/Debian: `sudo apt install tesseract-ocr tesseract-ocr-fra`
- Windows: installer Tesseract puis ajouter l'executable au `PATH`

Sans Tesseract, l'upload fonctionne et le document est indexe avec les metadonnees disponibles. Pour les PDF, le POC extrait d'abord le texte natif via `pypdf`, puis tente un OCR page par page avec PyMuPDF + Tesseract si le PDF est scanne.

Apres chaque import, l'interface affiche un controle OCR: statut, moteur utilise, nombre de caracteres et texte extrait. Le praticien peut corriger le texte puis cliquer sur `Enregistrer OCR`; la correction est stockee dans SQLite et l'index de recherche est reconstruit.

## API

- `GET /references`
- `GET /search?q=...`
- `GET /references/{id}`
- `POST /references`
- `PUT /references/{id}`
- `DELETE /references/{id}`
- `POST /documents/upload`
- `PUT /documents/{id}/ocr`
- `GET /health`

## Donnees de demo

Le seed integre les fiches:

- TEST PREPROBIO
- CERVEAU ENTERIQUE
- MEMOIRES DU SANG
- SONAR EPIPHYSAIRE
- MOUVEMENTS ARCHETYPAUX
- COLONNE VERTEBRALE

Les 4 scans du POC sont inclus dans `backend/app/fixtures/scans/`. Au seed, ils sont copies dans `uploads/`, rattaches aux fiches concernees et indexes avec une transcription OCR corrigee.

La recherche couvre titre, categorie, references numeriques, sous-categories, associations, tags, notes et texte OCR. Exemples utiles:

- `foie ethérique`
- `roue iracik`
- `plaque de Peyer`
- `atlas-axis`
- `fascia`
- `sang identité`
- `pumping out`
- `31 17 34 09 22`
