# Note utilisateur rapide

## Objectif

Nutripuncture Desk sert à retrouver rapidement une information issue des fiches papier/scans du praticien.

Le praticien peut chercher par :

- début de code : `31 17`, `3117`, `15 11`
- organe ou zone : `foie`, `coeur`, `atlas`, `sacrum`
- notion métier : `microbiote`, `sang`, `amygdale`, `fascia`
- association : `commande limbique`, `pumping out`, `roue iracik`

## Lancer le logiciel en local

Depuis le dossier du projet :

```bash
cd /home/depot-github/nutripuncture
bash scripts/start_app.sh
```

Ouvrir ensuite :

```text
http://127.0.0.1:5173
```

L'API locale FastAPI tourne sur :

```text
http://127.0.0.1:8000
```

## Utilisation en consultation

1. Ouvrir l'application.
2. Cliquer dans la grande barre de recherche.
3. Taper un code, un organe, un mot de fiche ou une association.
4. Cliquer sur le résultat voulu.
5. Lire la fiche : codes, tags, associations, notes et scan source.

Exemples de recherches utiles :

- `microbiote` retrouve `TEST PRÉPROBIO`
- `sang identité` retrouve `A - SANG IDENTITÉ`
- `3117` retrouve `INTERACTION SYSTÈME MÉTABOLIQUE SANGUIN`
- `coeur etherique` retrouve `CŒUR ÉTHÉRIQUE`
- `atlas` retrouve `ATLAS-AXIS`
- `pumping out` retrouve `POMPING OUT VEINE`

## Ajouter une nouvelle fiche

1. Cliquer sur `Admin`.
2. Cliquer sur `Nouvelle fiche`.
3. Renseigner le titre, la catégorie, les codes, les tags et les notes.
4. Cliquer sur `Enregistrer`.

Conseil : ajouter plusieurs tags simples pour faciliter la recherche future.

## Ajouter un scan ou un PDF

1. Sélectionner une fiche existante.
2. Aller dans `Admin`.
3. Utiliser la zone `Uploader une image ou un PDF`.
4. Le document est copié en local, analysé par OCR et indexé dans SQLite.

Le scan reste visible dans la fiche, avec son texte OCR.

## Données déjà intégrées dans le POC

Le POC contient les fiches de démonstration et les 4 scans fournis :

- mémoires du sang et circulation lymphatique
- sonars oscillateurs fondamentaux
- terrain intestinal et neurotransmetteurs
- colonne vertébrale, mouvements archétypaux et fascia

La base contient des entrées fines pour que la recherche tombe directement sur la bonne ligne documentaire, pas seulement sur une grande fiche globale.

## Version desktop

Les paquets Linux générés sont dans :

```text
src-tauri/target/release/bundle/
```

Pour le POC, le lancement navigateur via `scripts/start_app.sh` reste le plus simple pour vérifier et présenter rapidement l'application.
