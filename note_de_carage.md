# Note de cadrage — POC Nutripuncture IA

## Projet : Logiciel métier intelligent pour praticiens en nutripuncture

Dépôt GitHub :
[https://github.com/Lidhak/nutripuncture.git](https://github.com/Lidhak/nutripuncture.git)

---

# 1. Vision du projet

Créer un logiciel desktop moderne permettant à un praticien en nutripuncture de :

* centraliser ses références thérapeutiques
* rechercher instantanément des protocoles et associations
* organiser sa base documentaire
* visualiser les relations entre systèmes biologiques
* automatiser la recherche dans ses documents/scans/PDF

Le logiciel doit fonctionner :

* 100% en local
* sans connexion Internet
* sur Mac, Windows et Linux

L’objectif final est de construire une véritable :

"mémoire thérapeutique intelligente"

capable d’assister le praticien dans sa pratique quotidienne.

---

# 2. Problème actuel

Aujourd’hui le praticien travaille avec :

* documents papier
* classeurs
* PDF
* scans
* tableaux thérapeutiques

Les difficultés :

* recherche lente
* informations dispersées
* associations difficiles à retrouver
* perte de temps importante en consultation

---

# 3. Objectifs du POC (version demain matin)

Le POC doit démontrer :

## Recherche instantanée

Le praticien tape :

* “microbiote”
* “sang”
* “atlas”

→ résultats immédiats.

---

## Interface moderne

Une UI professionnelle inspirée de :

* Notion
* Raycast
* Linear
* Obsidian

---

## Fiches thérapeutiques

Affichage :

* titre
* catégorie
* références
* tags
* associations
* images/scans

---

## Administration

Le praticien peut :

* ajouter une fiche
* modifier une fiche
* uploader un document

---

## OCR basique

Import d’image/PDF :

* extraction texte
* indexation automatique

---

# 4. Stack technique retenue

## Frontend

* React
* TailwindCSS
* shadcn/ui

---

## Backend

* Python FastAPI

---

## Base de données

* SQLite + FTS5

---

## Desktop

* Tauri

---

## OCR

* Tesseract OCR

---

# 5. Architecture

```text
┌─────────────────────┐
│ Tauri Desktop App   │
├─────────────────────┤
│ React Frontend      │
│ Tailwind UI         │
├─────────────────────┤
│ FastAPI Local API   │
│ Python              │
├─────────────────────┤
│ SQLite + FTS5       │
├─────────────────────┤
│ OCR Engine          │
└─────────────────────┘
```

---

# 6. Fonctionnalités du POC

## Recherche ultra rapide

Recherche :

* mot-clé
* référence numérique
* catégorie
* tags

---

## Base de données thérapeutique

Exemples intégrés :

* microbiote intestinal
* cerveau entérique
* mémoires du sang
* colonne vertébrale
* mouvements archétypaux
* oscillateurs fondamentaux

---

## Upload documents

Formats :

* PDF
* JPG
* PNG

---

## OCR automatique

Extraction texte des scans.

---

## Interface admin

CRUD complet :

* ajouter
* modifier
* supprimer
* classer

---

# 7. Ce qui rend le projet très intéressant

Le projet possède :

* une forte spécialisation métier
* très peu de concurrence logicielle
* une donnée thérapeutique structurée
* un fort potentiel IA

Ce n’est pas seulement :

* un lecteur PDF
* une base documentaire

C’est potentiellement :

* un moteur de connaissance thérapeutique intelligent.

---

# 8. Évolutions futures — IA avancée

## 8.1 Recherche sémantique IA

Aujourd’hui :
recherche mot-clé.

Demain :
recherche intelligente.

Exemple :

```text
stress digestif anxiété sommeil
```

→ le logiciel comprend :

* microbiote
* amygdale
* système limbique
* cerveau entérique

sans mot-clé exact.

---

## 8.2 Embeddings thérapeutiques

Créer des relations intelligentes entre :

* organes
* émotions
* neurotransmetteurs
* systèmes biologiques
* protocoles

Technologies :

* Sentence Transformers
* Ollama
* embeddings locaux

---

# 8.3 Graphe thérapeutique visuel

Visualisation des connexions :

```text
Microbiote
   ↔ Amygdale
   ↔ Intestin
   ↔ Sommeil
   ↔ Stress
```

Technologies :

* React Flow
* Cytoscape.js

Très forte valeur ajoutée métier.

---

# 8.4 Assistant thérapeutique IA

Le praticien saisit :

```text
fatigue chronique + digestion + anxiété
```

Le système suggère :

* protocoles
* références
* associations
* pistes thérapeutiques

---

# 8.5 OCR intelligent

Au lieu d’extraire uniquement du texte :

Le logiciel :

* détecte automatiquement les références
* comprend les catégories
* crée des fiches automatiquement

---

# 8.6 Historique thérapeutique patient

Future possibilité :

* suivi patient
* séances
* protocoles utilisés
* évolution

---

# 8.7 IA locale privée

Utilisation possible :

* Ollama
* Mistral
* Llama
* modèles locaux

Avantages :

* confidentialité totale
* données non envoyées au cloud
* fonctionnement offline

---

# 9. Évolution architecture cible

## POC actuel

```text
React + FastAPI + SQLite + Tauri
```

---

## Version avancée IA

```text
React
+ Rust/Tauri
+ Vector Database
+ Ollama local
+ Embeddings IA
+ Knowledge Graph
```

---

# 10. Roadmap proposée

## Phase 1 — POC

* recherche
* fiches
* upload
* OCR
* UI moderne

---

## Phase 2 — Structuration métier

* tags avancés
* relations thérapeutiques
* protocoles

---

## Phase 3 — IA locale

* embeddings
* recherche sémantique
* recommandations

---

## Phase 4 — Graphe intelligent

* visualisation des relations
* moteur thérapeutique

---

## Phase 5 — Assistant clinique

* IA contextuelle
* protocoles suggérés
* aide à la consultation

---

# 11. Conclusion

Le projet possède un très fort potentiel car il combine :

* expertise métier spécialisée
* structuration thérapeutique
* recherche documentaire
* IA locale
* confidentialité
* ergonomie moderne

L’objectif n’est pas seulement de numériser des documents.

L’objectif est de construire :

"une base de connaissance thérapeutique intelligente et augmentée par l’IA"

capable d’assister les praticiens dans leur quotidien.
