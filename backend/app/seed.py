from __future__ import annotations

import shutil
from pathlib import Path

from .database import ROOT_DIR, UPLOAD_DIR, init_db
from .repository import attach_document_once, list_references, upsert_reference
from .schemas import ReferenceIn

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "scans"

MEMOIRES_DU_SANG_TEXT = """
OCR corrige - scan IMG_0805 - MEMOIRES DU SANG / CIRCULATION LYMPHATIQUE

A - SANG IDENTITE
F: 30 01 32 13 37 AC 15 04 27 34 08
H: 30 01 32 13 38 AC 15 04 27 34 08

AA - SANG DETOXICATION
F: 35 01 11 37 30 AC 30 26 37 34 08
H: 36 01 11 38 30 AC 30 26 38 34 08

SANG PLACENTAIRE
F: 12 22 37 08 30 AC 04 22 08 09 23
H: 12 22 38 08 30 AC 04 22 08 09 23

SANG UNITAIRE FAMILIAL
F: 11 03 08 34 19 AC 11 19 26 15 28
H: 11 03 08 34 19 AC 11 19 26 15 21

SANG LIMITES ENDO-YEUX
F: 28 30 26 37 23 AC 08 12 25 33 30
H: 21 30 26 38 23 AC 08 12 25 33 30

SANG DE LA MOELLE
F: 23 04 11 30 35 AC 16 26 04 17 03
H: 23 04 11 30 36 AC 16 26 04 17 03

SANG-PEAU INVERSION CRUAUTE
F: 01 11 35 26 19 AC 27 09 12 31 08
H: 01 11 36 26 19 AC 27 09 12 31 08

SANG : REGLES IDENTITE
F: 33 28 27 01 29 AC 28 26 30 12 03

SANG : RYTHME DES REGLES
F: 11 27 04 12 28 AC 09 04 24 30 12

POMPING OUT VEINE
F: 16 09 30 15 24 AC 20 34 12 28 08
H: 16 09 30 15 14 AC 20 34 12 21 08

POMPING INN ARTERE
F: 05 37 28 23 30 AC 12 24 04 09 16
H: 05 38 21 23 30 AC 12 14 04 09 16

REFUS HERITAGE, origine corps
F: 30 37 04 24 13 AC 11 04 08 27 18
H: 30 38 04 14 13 AC 11 04 08 27 18

TROISIEME SPHERE
F: 11 22 04 30 33 AC 03 04 34 26 02
H: 11 22 04 30 33 AC 03 04 34 26 02

CIRCULATION LYMPHATIQUE
F: 29 15 11 37 30 AC 27 15 16 34 25
H: 29 15 11 38 30 AC 27 15 16 34 25

LYMPHATIQUES BOUCHE
F: 15 37 33 28 10 AC 15 29 37 10 08
H: 15 38 33 21 10 AC 15 29 38 10 08

LYMPHATIQUES IDENTITE
F: 25 15 33 24 07 AC 25 05 15 12 13
H: 25 15 33 14 06 AC 25 05 15 12 13
"""

SONARS_TEXT = """
OCR corrige - scan IMG_0804 - LES SONARS : DES OSCILLATEURS FONDAMENTAUX

Les sonars sont des oscillateurs avec une action a trois niveaux : le sonar epiphysaire
en relation avec le cycle de la lumiere, le thoracique avec les rythmes du corps et
l'insertion du temps, le pelvien en rapport avec le systeme metabolique.

SONAR EPIPHYSAIRE
03 08 24/14 35/36 34
AC 23 32 08 24/14 26

CERVEAU ETHERIQUE / CERVEAU ETHÉRIQUE
35/36 27 08 30 02
AC 03 09 16 08 02

SONAR THORACIQUE
04 01 32 27 24/14
AC 23 26 27 09 29

COEUR ETHERIQUE / COEUR ETHÉRIQUE
35/36 34 37/38 33 30
AC 16 08 04 35/36 27

ROUE IRACIK
31 27 04 34 03 AC 31 09 23 08 32

SONAR PELVIEN
11 04 28/21 33/36
AC 27 28/21 07/06 03 08

FOIE ETHERIQUE / FOIE ETHÉRIQUE
11 22 35/36 02 15
AC 11 18 03 16 23

SERTISSAGE, SANG VIE, EAU STRUCTURE, SANG MOELLE, RATE.
"""

TERRAIN_INTESTINAL_TEXT = """
OCR corrige - scan IMG_0802 - RECHERCHE SUR LE TERRAIN INTESTINAL ET LES NEUROTRANSMETTEURS

SOI DE L'AMYGDALE
13 19 35/36 24/14 07/06
AC 17 10 09 04 32

AMYGDALE
03 05 31 25 07/06
AC 05 08 02 12 26

COMMANDE LIMBIQUE
34 18 13 31 09
AC 31 02 12 33 26

PHASE PSYCHO-NEURO-IMMUNO-ENDOCRINIEN
18 12 04 27 02 AC 16 08 02 23 32

PLAQUE DE PEYER
35/36 05 13 37/38 27
AC 34 13 33 12 08

LYMPHOCYTES LIE
05 15 35/36 13 12
AC 35/36 05 12 13 37/38

TEST PREPROBIO / TEST PRÉPROBIO
MICROBIOTE INTESTINAL
15 11 05 27 13
AC 15 13 05 37/38 08

CERVEAU ENTERIQUE / CERVEAU ENTÉRIQUE
05 08 12 18 15
AC 12 05 09 16 15

CERVEAU COMMANDE LIMBIQUE
34 18 13 31 09
AC 31 02 12 33 26

PREMIERE RECONNAISSANCE TISSULAIRE SEXUEE
23 30 04 01 32
AC 29 18 35/36 02 16

PREMIERE MATRICE MATERNELLE GROSSESSE
09 24/14 37/38 19 33
AC 37/38 27 04 34 31

SOI DE L'AMYGDALE
13 19 35/36 24/14 07/06
AC 17 10 09 04 32

INTERACTION AVEC LE SYSTEME METABOLIQUE SANGUIN
SANG PLACENTAIRE, PREMIERE MATRICE, 3EME SPHERE
31 17 34 09 22 AC 27 19 02 32 24/14
TEST OMEGA 3
"""

STRUCTURE_TEXT = """
OCR corrige - scan IMG_0801 - COLONNE VERTEBRALE, MOUVEMENTS ARCHETYPAUX, FASCIALE

C) SPHENOIDE
F: 35 37 32 33 34 AC 27 26 17 16 08
H: 36 38 32 33 34 AC 27 26 17 16 08

C) COCCYX
F: 37 17 28 35 34 AC 16 37 08 35 28
H: 38 17 21 36 34 AC 16 38 08 36 21

D) ETHMOIDE
F: 07 17 25 30 37 AC 07 12 30 15 08
H: 06 17 25 30 38 AC 06 12 30 15 08

D) PUBIS
F: 33 17 07 19 31 AC 07 17 05 25 12
H: 33 17 07 19 31 AC 06 17 05 25 12

COLONNE VERTEBRALE
DISQUES INTERVERTEBRAUX
F: 19 02 16 34 09 AC 02 16 34 08 17
H: 19 02 16 34 09 AC 02 16 34 08 17

ATLAS-AXIS
F: 26 33 34 30 02 AC 08 31 19 16 34
H: 26 38 34 30 02 AC 08 31 19 16 34

COCCYX
F: 37 17 28 35 34 AC 16 37 08 35 28
H: 38 17 21 36 34 AC 16 38 08 36 21

SACRUM
F: 17 11 28 34 30 AC 17 28 08 34 26
H: 17 11 21 34 30 AC 17 21 08 34 26

VERTEBRES CERVICALES
F: 34 17 37 16 27 AC 27 02 04 34 08
H: 34 17 38 16 27 AC 27 02 04 34 08

VERTEBRES DORSALES
F: 34 17 15 04 20 AC 31 17 16 04 20
H: 34 17 15 04 20 AC 31 17 16 04 20

VERTEBRES LOMBAIRES
F: 34 17 31 02 09 AC 16 31 17 34 37
H: 34 17 31 02 09 AC 16 31 17 34 38

MOUVEMENTS ARCHETYPAUX
1ER MOUVEMENT
F: 29 09 31 28 22 AC 19 16 18 15 26
H: 29 09 31 21 22 AC 19 16 18 15 26

2EME MOUVEMENT
F: 35 24 33 07 30 AC 19 16 15 07 30
H: 36 14 33 06 30 AC 19 16 15 06 30

3EME MOUVEMENT
F: 15 05 02 35 37 AC 16 19 15 31 09
H: 15 05 02 36 38 AC 16 19 15 31 09

4EME MOUVEMENT
F: 37 04 09 01 29 AC 09 24 15 37 27
H: 38 04 09 01 29 AC 09 14 15 38 27

5EME MOUVEMENT
F: 25 15 27 28 07 AC 16 33 15 37 30
H: 25 16 27 21 06 AC 16 33 15 38 30

MOUVEMENTS OCULAIRES
F: 35 37 32 23 08 AC 12 04 37 32 23
H: 36 38 32 23 08 AC 12 04 38 32 23

FASCIALE
1 LINGUAL F: 19 16 18 15 26 H: 19 16 18 15 26
2 MEDIAN F: 19 16 15 07 30 H: 19 16 15 06 30
3 POSTERIEUR F: 16 19 15 31 09 H: 16 19 15 31 09
4 ANTERO-LATERAL F: 09 24 15 37 27 H: 09 14 15 38 27
5 POSTERO LATERAL F: 16 33 15 37 30 H: 16 33 15 38 30
"""

SAMPLES = [
    ReferenceIn(
        title="TEST PRÉPROBIO",
        category="Microbiote intestinal",
        description="Recherche sur le terrain intestinal, le microbiote et les neurotransmetteurs.",
        numeric_refs="15 11 05 27 13",
        subcategories=["microbiote intestinal", "plaque de Peyer", "lymphocytes LIE", "test oméga 3"],
        associations=["cerveau entérique", "amygdale", "commande limbique", "oméga 3", "terrain intestinal"],
        tags=["microbiote", "intestin", "neurotransmetteurs", "digestion", "cerveau entérique", "préprobio", "preprobio"],
        notes=TERRAIN_INTESTINAL_TEXT,
    ),
    ReferenceIn(
        title="CERVEAU ENTÉRIQUE",
        category="Système digestif",
        description="Référence digestive connectée au microbiote intestinal et à la commande limbique.",
        numeric_refs="05 08 12 18 15",
        subcategories=["cerveau entérique", "commande limbique", "amygdale"],
        associations=["microbiote intestinal", "commande limbique", "test préprobio"],
        tags=["intestin", "cerveau", "digestion", "cerveau entérique", "enterique"],
        notes=TERRAIN_INTESTINAL_TEXT,
    ),
    ReferenceIn(
        title="MÉMOIRES DU SANG",
        category="Circulation lymphatique",
        description="Tableau des mémoires du sang, de l'identité sanguine et des circulations lymphatiques.",
        numeric_refs="30 01 32 13 37 AC 15 04 27 34 08",
        subcategories=[
            "sang identité",
            "sang détoxication",
            "sang placentaire",
            "sang unitaire familial",
            "sang limites endo-yeux",
            "sang de la moelle",
            "sang-peau inversion cruauté",
            "circulation lymphatique",
            "lymphatiques bouche",
            "lymphatiques identité",
        ],
        associations=["pumping out veine", "pumping inn artère", "refus héritage", "troisième sphère", "règles identité"],
        tags=["sang", "mémoire", "lymphatique", "identité", "détoxication", "placentaire", "moelle", "héritage", "veine", "artère"],
        notes=MEMOIRES_DU_SANG_TEXT,
    ),
    ReferenceIn(
        title="SONAR ÉPIPHYSAIRE",
        category="Oscillateurs fondamentaux",
        description="Sonars oscillateurs fondamentaux : épiphysaire, thoracique et pelvien.",
        numeric_refs="03 08 24/14 35/36 34",
        subcategories=["sonar épiphysaire", "sonar thoracique", "sonar pelvien", "cerveau éthérique", "cœur éthérique", "foie éthérique"],
        associations=["cerveau éthérique", "roue iracik", "cœur éthérique", "foie éthérique", "sang moelle", "rythmes du corps"],
        tags=["sonar", "épiphyse", "oscillation", "oscillateurs fondamentaux", "éthérique", "etherique", "thoracique", "pelvien"],
        notes=SONARS_TEXT,
    ),
    ReferenceIn(
        title="MOUVEMENTS ARCHÉTYPAUX",
        category="Structure corporelle",
        description="Mouvements archétypaux et lignes fasciales associés à la structure corporelle.",
        numeric_refs="29 09 31 28 22 AC 19 16 18 15 26",
        subcategories=["1er mouvement", "2ème mouvement", "3ème mouvement", "4ème mouvement", "5ème mouvement", "mouvements oculaires"],
        associations=["fascia lingual", "fascia médian", "fascia postérieur", "fascia antéro-latéral", "fascia postéro-latéral"],
        tags=["mouvement", "archétype", "structure", "fascia", "fasciale", "oculaires"],
        notes=STRUCTURE_TEXT,
    ),
    ReferenceIn(
        title="COLONNE VERTÉBRALE",
        category="Ostéopathie structurelle",
        description="Repères structurels : colonne vertébrale, disques, atlas-axis, sacrum, vertèbres et bassin.",
        numeric_refs="26 33 34 30 02 AC 08 31 19 16 34",
        subcategories=["atlas-axis", "coccyx", "sacrum", "vertèbres cervicales", "vertèbres dorsales", "vertèbres lombaires", "disques intervertébraux"],
        associations=["sphénoïde", "ethmoïde", "pubis", "mouvements archétypaux", "fascia"],
        tags=["colonne", "vertèbres", "ostéopathie", "atlas", "axis", "sacrum", "coccyx", "pubis", "sphénoïde"],
        notes=STRUCTURE_TEXT,
    ),
]

DOCUMENTS = {
    "TEST PRÉPROBIO": [("scan_terrain_intestinal_neurotransmetteurs.jpeg", TERRAIN_INTESTINAL_TEXT)],
    "CERVEAU ENTÉRIQUE": [("scan_terrain_intestinal_neurotransmetteurs.jpeg", TERRAIN_INTESTINAL_TEXT)],
    "MÉMOIRES DU SANG": [("scan_memoires_du_sang.jpeg", MEMOIRES_DU_SANG_TEXT)],
    "SONAR ÉPIPHYSAIRE": [("scan_sonars_oscillateurs.jpeg", SONARS_TEXT)],
    "MOUVEMENTS ARCHÉTYPAUX": [("scan_colonne_mouvements_fascia.jpeg", STRUCTURE_TEXT)],
    "COLONNE VERTÉBRALE": [("scan_colonne_mouvements_fascia.jpeg", STRUCTURE_TEXT)],
}


def install_fixture_document(reference_id: int, fixture_name: str, text: str) -> None:
    source = FIXTURE_DIR / fixture_name
    if not source.exists():
        return
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    stored_name = f"seed_{fixture_name}"
    destination = UPLOAD_DIR / stored_name
    if not destination.exists() or destination.stat().st_size != source.stat().st_size:
        shutil.copy2(source, destination)
    attach_document_once(
        reference_id=reference_id,
        filename=fixture_name,
        stored_path=f"/uploads/{stored_name}",
        mime_type="image/jpeg",
        ocr_text=text,
    )


def seed() -> None:
    init_db()
    seeded = []
    for sample in SAMPLES:
        reference = upsert_reference(sample)
        seeded.append(reference["id"])
        for fixture_name, text in DOCUMENTS.get(sample.title, []):
            install_fixture_document(reference["id"], fixture_name, text)
    if not list_references():
        raise RuntimeError("Seed impossible: aucune fiche creee")


if __name__ == "__main__":
    seed()
    print("Base SQLite initialisee avec les donnees POC et les scans indexes.")
