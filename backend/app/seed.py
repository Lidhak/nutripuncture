from __future__ import annotations

from .database import init_db
from .repository import create_reference, list_references
from .schemas import ReferenceIn

SAMPLES = [
    ReferenceIn(
        title="TEST PRÉPROBIO",
        category="Microbiote intestinal",
        description="Recherche sur le terrain intestinal et neurotransmetteurs.",
        numeric_refs="15 11 05 27 13",
        associations=["cerveau entérique", "amygdale", "commande limbique", "oméga 3"],
        tags=["microbiote", "intestin", "neurotransmetteurs", "digestion", "cerveau entérique"],
        notes="Fiche prioritaire pour explorer les liens intestin, humeur et terrain digestif.",
    ),
    ReferenceIn(
        title="CERVEAU ENTÉRIQUE",
        category="Système digestif",
        numeric_refs="05 08 12 18 15",
        associations=["microbiote intestinal", "commande limbique"],
        tags=["intestin", "cerveau", "digestion"],
    ),
    ReferenceIn(
        title="MÉMOIRES DU SANG",
        category="Circulation lymphatique",
        subcategories=["sang identité", "sang détoxication", "sang placentaire", "sang unitaire familial"],
        tags=["sang", "mémoire", "lymphatique", "identité"],
    ),
    ReferenceIn(
        title="SONAR ÉPIPHYSAIRE",
        category="Oscillateurs fondamentaux",
        numeric_refs="03 08 24 14 35 36 34",
        associations=["cerveau éthérique", "roue iracik"],
        tags=["sonar", "épiphyse", "oscillation"],
    ),
    ReferenceIn(
        title="MOUVEMENTS ARCHÉTYPAUX",
        category="Structure corporelle",
        subcategories=["1er mouvement", "2ème mouvement", "3ème mouvement", "mouvements oculaires"],
        tags=["mouvement", "archétype", "structure"],
    ),
    ReferenceIn(
        title="COLONNE VERTÉBRALE",
        category="Ostéopathie structurelle",
        subcategories=["atlas-axis", "coccyx", "sacrum", "vertèbres cervicales", "vertèbres dorsales", "vertèbres lombaires"],
        tags=["colonne", "vertèbres", "ostéopathie"],
    ),
]


def seed() -> None:
    init_db()
    if list_references():
        return
    for sample in SAMPLES:
        create_reference(sample)


if __name__ == "__main__":
    seed()
    print("Base SQLite initialisee avec les donnees POC.")
