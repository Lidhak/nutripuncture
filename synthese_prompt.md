# Synthèse du prompt

## Vision

Créer un logiciel desktop multiplateforme pour un ostéopathe utilisant la nutripuncture, capable de transformer une documentation papier/PDF dispersée en base de connaissance locale, rapide et facile à consulter.

Le logiciel doit être le reflet fidèle de la documentation du praticien : fiches, codes numériques, catégories, organes, associations, scans et notes doivent être retrouvables immédiatement.

## Problème métier

Le praticien possède de nombreux classeurs, documents papier, scans et PDF. La recherche manuelle prend du temps, surtout en consultation.

Le POC doit permettre de retrouver une information en tapant :

- un début de code
- un organe
- une catégorie
- un mot-clé
- un tag
- une association thérapeutique

## Objectif du POC

Disposer rapidement d'une application locale montrable et utilisable, avec :

- recherche instantanée
- interface moderne et fluide
- fiches thérapeutiques claires
- visualisation des scans
- ajout/modification/suppression de fiches
- upload d'image/PDF
- OCR basique
- indexation locale dans SQLite

## Priorités UX

La priorité absolue est l'expérience utilisateur.

L'application doit donner immédiatement une impression :

- professionnelle
- moderne
- haut de gamme
- simple
- rapide
- adaptée à un usage cabinet

Inspirations : Raycast, Notion, Linear, Obsidian.

## Stack demandée

- Frontend : React, TailwindCSS, shadcn/ui
- Backend : Python FastAPI
- Base : SQLite + FTS5
- Desktop : Tauri
- OCR : Tesseract OCR ou PaddleOCR
- Fonctionnement : 100% local, offline-first

## Données POC

Le POC doit intégrer des exemples métier :

- TEST PRÉPROBIO
- CERVEAU ENTÉRIQUE
- MÉMOIRES DU SANG
- SONAR ÉPIPHYSAIRE
- MOUVEMENTS ARCHÉTYPAUX
- COLONNE VERTÉBRALE

Les scans ajoutés doivent aussi être extraits, corrigés si nécessaire, découpés en entrées recherchables et indexés pour permettre des recherches fines comme `foie`, `atlas`, `amygdale`, `pumping out`, `31 17`.

## Architecture attendue

Structure projet :

```text
frontend/
backend/
database/
uploads/
ocr/
src-tauri/
scripts/
```

Tables principales :

- references
- categories
- tags
- documents
- associations

Endpoints API :

- `GET /references`
- `GET /search?q=...`
- `POST /references`
- `PUT /references/{id}`
- `DELETE /references/{id}`
- `POST /documents/upload`

## Résultat attendu

Le POC doit permettre dès demain matin de :

- lancer l'application localement
- rechercher immédiatement dans les fiches
- ajouter une nouvelle référence
- uploader un scan
- voir le texte OCR indexé
- montrer une interface élégante et crédible

En une phrase : construire une première version d'une mémoire thérapeutique locale, structurée et recherchable, orientée praticien.
