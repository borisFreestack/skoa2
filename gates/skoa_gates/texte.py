"""Découpage du code source Java et TypeScript : identifiants, chaînes, mots.

Le découpage est lexical, sans analyse syntaxique. C'est suffisant pour juger
les noms qu'on choisit : les commentaires et le texte des chaînes sont du
français libre, ils ne sont pas soumis au glossaire.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

IDENTIFIANT = re.compile(r"[A-Za-z_$][A-Za-z0-9_$]*")
MOT = re.compile(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+|[0-9]+")


@dataclass
class Segment:
    texte: str
    ligne: int  # ligne de début, 1-indexée


@dataclass
class Decoupage:
    code: list[Segment]
    chaines: list[Segment]


def decouper(source: str) -> Decoupage:
    """Sépare le code, les chaînes et les commentaires (ceux-ci sont jetés)."""
    code, chaines = [], []
    i, n, ligne = 0, len(source), 1
    debut_code, ligne_code = 0, 1

    def fermer_code(fin: int):
        if fin > debut_code:
            code.append(Segment(source[debut_code:fin], ligne_code))

    while i < n:
        c = source[i]
        deux = source[i:i + 2]
        if deux == "//" or deux == "/*":
            fermer_code(i)
            fin = source.find("\n", i) if deux == "//" else source.find("*/", i + 2)
            fin = n if fin == -1 else (fin if deux == "//" else fin + 2)
        elif source.startswith('"""', i):
            fermer_code(i)
            fin = source.find('"""', i + 3)
            fin = n if fin == -1 else fin + 3
            chaines.append(Segment(source[i + 3:fin - 3], ligne))
        elif c in "\"'`":
            fermer_code(i)
            j = i + 1
            while j < n and source[j] != c:
                if source[j] == "\\":
                    j += 1
                elif source[j] == "\n" and c != "`":
                    break
                j += 1
            fin = min(j + 1, n)
            chaines.append(Segment(source[i + 1:j], ligne))
        else:
            if c == "\n":
                ligne += 1
            i += 1
            continue
        ligne += source.count("\n", i, fin)
        i = fin
        debut_code, ligne_code = i, ligne
    fermer_code(n)
    return Decoupage(code, chaines)


def identifiants(decoupage: Decoupage) -> list[tuple[str, int]]:
    """(identifiant, ligne) pour chaque identifiant du code."""
    resultat = []
    for seg in decoupage.code:
        for m in IDENTIFIANT.finditer(seg.texte):
            resultat.append((m.group(), seg.ligne + seg.texte.count("\n", 0, m.start())))
    return resultat


def sans_accents(texte: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texte) if unicodedata.category(c) != "Mn")


def mots(nom: str) -> list[str]:
    """« DelaiDeReponse », « delai_de_reponse » ou « delai-de-reponse » donnent [delai, de, reponse].

    Chaque mot est ramené au singulier par une règle grossière (s ou x final retiré au-delà de
    trois lettres), appliquée des deux côtés : « ListeClients » contient bien « Client ».
    """
    return [_singulier(m.lower()) for m in MOT.findall(sans_accents(nom))]


def _singulier(mot: str) -> str:
    return mot[:-1] if len(mot) > 3 and mot[-1] in "sx" else mot


def occurrences(sequence: list[str], motif: list[str]) -> list[int]:
    """Positions où `motif` apparaît comme suite contiguë de mots dans `sequence`."""
    k = len(motif)
    return [i for i in range(len(sequence) - k + 1) if motif and sequence[i:i + k] == motif]


IMPORT_JAVA = re.compile(r"^\s*import\s+(?:static\s+)?([\w.]+?)(\.\*)?\s*;", re.M)
IMPORT_TS = re.compile(r"""import\s+(?:type\s+)?(?P<liste>[^;]*?)\s+from\s+['"](?P<module>[^'"]+)['"]""", re.S)


def noms_externes(source: str, suffixe: str) -> set[str]:
    """Noms importés d'une bibliothèque tierce : on ne les a pas choisis, on ne les juge pas."""
    noms = set()
    if suffixe == ".java":
        for m in IMPORT_JAVA.finditer(source):
            if not m.group(2) and not m.group(1).startswith("org.skoa."):
                noms.add(m.group(1).rsplit(".", 1)[-1])
    elif suffixe == ".ts":
        for m in IMPORT_TS.finditer(source):
            if m.group("module").startswith("."):
                continue
            liste = m.group("liste")
            accolades = re.search(r"\{([^}]*)\}", liste)
            if accolades:
                for element in accolades.group(1).split(","):
                    # « X as Y » : X vient de la bibliothèque, Y est un nom qu'on choisit.
                    origine = element.strip().removeprefix("type ").split(" as ")[0].strip()
                    if origine:
                        noms.add(origine)
            defaut = re.match(r"\s*([A-Za-z_$][\w$]*)\s*(,|$)", liste)
            if defaut:
                noms.add(defaut.group(1))
    return noms
