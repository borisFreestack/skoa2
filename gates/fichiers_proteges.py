"""Gate « fichiers protégés » : une PR qui touche un fichier listé dans .github/CODEOWNERS
doit avoir été validée par un de ses propriétaires.

La validation est le label « modification-protegee-validee », posé par un propriétaire.
Le workflow retire ce label à chaque nouveau commit : une validation porte sur un état
précis de la PR, pas sur ce qu'un agent y poussera ensuite.

    python3 gates/fichiers_proteges.py --codeowners .github/CODEOWNERS \\
        --fichiers fichiers.txt [--valide-par <login>]

`fichiers.txt` contient un chemin par ligne : les fichiers modifiés, ajoutés, supprimés,
et l'ancien nom des fichiers renommés (renommer un fichier protégé, c'est le retirer).
Code de sortie 1 si un fichier protégé est modifié sans validation de son propriétaire.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from skoa_gates.rapport import Constat, imprimer  # noqa: E402

GATE = "fichiers-proteges"
LABEL = "modification-protegee-validee"
EXPLICATION = (
    "Ces fichiers sont protégés (CLAUDE.md, règle 4) : un agent ne les modifie pas, il signale le problème dans la PR.\n"
    f"Si la modification est voulue, un propriétaire la valide en posant le label « {LABEL} »."
)


@dataclass(frozen=True)
class Regle:
    motif: str
    proprietaires: tuple[str, ...]
    expression: re.Pattern

    def couvre(self, chemin: str) -> bool:
        return bool(self.expression.match(chemin))


def lire_codeowners(texte: str) -> list[Regle]:
    regles = []
    for ligne in texte.splitlines():
        ligne = ligne.split("#", 1)[0].strip()
        if not ligne:
            continue
        motif, *proprietaires = ligne.split()
        regles.append(Regle(motif, tuple(p.lstrip("@").lower() for p in proprietaires), _expression(motif)))
    return regles


def _expression(motif: str) -> re.Pattern:
    """Sous-ensemble de la syntaxe CODEOWNERS (celle de .gitignore) : /, *, ** et le / final."""
    ancre = motif.startswith("/") or "/" in motif.rstrip("/")
    corps = motif.strip("/")
    regex = ""
    i = 0
    while i < len(corps):
        if corps.startswith("**", i):
            regex += ".*"
            i += 2
        elif corps[i] == "*":
            regex += "[^/]*"
            i += 1
        else:
            regex += re.escape(corps[i])
            i += 1
    prefixe = "^" if ancre else "^(?:.*/)?"
    # Un motif qui désigne un dossier couvre tout son contenu.
    return re.compile(prefixe + regex + "(?:/.*)?$")


def proprietaires(regles: list[Regle], chemin: str) -> tuple[str, ...] | None:
    """Propriétaires du chemin selon la dernière règle qui le couvre (règle de GitHub), None s'il n'est pas protégé."""
    trouve = None
    for r in regles:
        if r.couvre(chemin):
            trouve = r.proprietaires
    return trouve or None


def verifier(regles: list[Regle], fichiers: list[str], valide_par: str | None) -> list[Constat]:
    valide_par = valide_par.lower() if valide_par else None
    constats = []
    for chemin in sorted(set(fichiers)):
        p = proprietaires(regles, chemin)
        if not p:
            continue
        noms = ", ".join("@" + x for x in p)
        if valide_par in p:
            constats.append(Constat(GATE, chemin, None, f"fichier protégé, modification validée par @{valide_par}",
                                    bloquant=False))
        elif valide_par:
            constats.append(Constat(GATE, chemin, None,
                                    f"fichier protégé : validé par @{valide_par}, qui n'en est pas propriétaire ({noms})"))
        else:
            constats.append(Constat(GATE, chemin, None, f"fichier protégé modifié sans validation de {noms}"))
    return constats


def main(arguments: list[str]) -> int:
    parseur = argparse.ArgumentParser(description="Gate « fichiers protégés »")
    parseur.add_argument("--codeowners", type=Path, required=True)
    parseur.add_argument("--fichiers", type=Path, required=True, help="un chemin modifié par ligne")
    parseur.add_argument("--valide-par", default="", help="login de qui a posé le label de validation")
    args = parseur.parse_args(arguments)

    regles = lire_codeowners(args.codeowners.read_text(encoding="utf-8"))
    if not regles:
        print(f"{args.codeowners} ne contient aucune règle : rien n'est protégé, c'est sûrement une erreur.")
        return 1
    fichiers = [l.strip() for l in args.fichiers.read_text(encoding="utf-8").splitlines() if l.strip()]
    return imprimer(GATE, verifier(regles, fichiers, args.valide_par or None), EXPLICATION)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
