"""Génère les fiches à remplir à partir des tableaux des projets.

Usage, depuis la racine du dossier :
    python -I fiches-a-remplir/_generer.py

Les tableaux de chaque fiche vivent dans fiches-a-remplir/_sources/ ; la mise en page,
l'enregistrement et l'export, dans _gabarit.html. Pour modifier une fiche, on édite sa
source ou le gabarit, puis on relance ce script : il réécrit les fiches. Les projets, eux,
ne contiennent plus qu'un lien vers leur fiche.
"""
import html
import pathlib
import sys

ICI = pathlib.Path(__file__).resolve().parent
SOURCES = ICI / "_sources"

FICHES = [
    {
        "source": "projet00-audit.html",
        "sortie": "Projet00-Fiche-Audit.html",
        "id": "projet00-audit",
        "titre": "Fiche d’audit — Projet 00",
        "surtitre": "Contexte InGen · Projet 00 · Fiche à remplir",
        "projet_lien": "../INGEN-Projet00-Preparatoire.html#fiche",
        "projet_nom": "Projet 00 : modélisation et audit",
        "consigne": (
            "Chaque valeur est suivie de la commande qui la prouve, entre crochets ou dans la colonne "
            "prévue. Une valeur sans commande n’est pas un relevé."
        ),
        "export": "Projet00-Fiche",
        "ident_nom": 0,      # colonne « Nom » du tableau d’identité
        "ident_groupe": 1,   # colonne « Groupe »
        "ancienne_cle": "ingen-projet00-audit",   # saisies de l’ancienne fiche intégrée à l’énoncé
    },
    {
        "source": "projet01-recette.html",
        "sortie": "Projet01-Fiche-Recette.html",
        "id": "projet01-recette",
        "titre": "Fiche de recette — Projet 01",
        "surtitre": "Contexte InGen · Projet 01 · Fiche à remplir",
        "projet_lien": "../INGEN-Projet01-Durcissement.html#recette",
        "projet_nom": "Projet 01 : durcissement",
        "consigne": (
            "Jouez chaque test sur le matériel réel, notez le résultat obtenu, puis cochez s’il est "
            "conforme. Remplissez la fiche depuis PC-DSI-01. Les lignes V24 à V27 sont à vous : "
            "trouvez ce que les tests précédents ne prouvent pas encore."
        ),
        "export": "Projet01-Recette",
        "ident_nom": 1,      # colonne « Noms du binôme »
        "ident_groupe": 0,   # colonne « Groupe »
        "ancienne_cle": "ingen-projet01-recette",
    },
]

GABARIT = (ICI / "_gabarit.html").read_text(encoding="utf-8")


def main():
    for f in FICHES:
        corps = (SOURCES / f["source"]).read_text(encoding="utf-8").strip("\n")
        page = GABARIT
        for cle, val in {
            "{{TITRE}}": html.escape(f["titre"], quote=False),
            "{{SURTITRE}}": html.escape(f["surtitre"], quote=False),
            "{{CONSIGNE}}": html.escape(f["consigne"], quote=False),
            "{{PROJET_LIEN}}": f["projet_lien"],
            "{{PROJET_NOM}}": html.escape(f["projet_nom"], quote=False),
            "{{ID}}": f["id"],
            "{{EXPORT}}": f["export"],
            "{{IDENT_NOM}}": str(f["ident_nom"]),
            "{{IDENT_GROUPE}}": str(f["ident_groupe"]),
            "{{ANCIENNE_CLE}}": f["ancienne_cle"],
            "{{CORPS}}": corps,
        }.items():
            page = page.replace(cle, val)
        if "{{" in page:
            sys.exit(f"Champ non remplacé dans {f['sortie']}")
        (ICI / f["sortie"]).write_text(page, encoding="utf-8", newline="\n")
        print("écrit", f["sortie"])


if __name__ == "__main__":
    main()
