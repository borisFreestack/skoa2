"""Gate « artefacts » : contexts/ est cohérent avec lui-même et avec CLAUDE.md.

Elle passe avant les autres : les gates de langage et d'invariants lisent ces fichiers.
"""

from __future__ import annotations

import re

from .depot import ArtefactIllisible, Depot
from .rapport import Constat
from .texte import mots

GATE = "artefacts"
EXPLICATION = (
    "Les fichiers de contexts/ sont en lecture seule pour les agents (CLAUDE.md, règle 4).\n"
    "Si une erreur porte sur contexts/, signale-la dans la PR ; seul un humain corrige ces fichiers."
)
TERMES_MIN, TERMES_MAX = 15, 30
NOM_DE_TERME = re.compile(r"^[A-Z][A-Za-z]*$")
ID_INVARIANT = re.compile(r"^INV-([A-Z]{3})-(\d{3})$")
SECTIONS_OBLIGATOIRES = ["## Mission", "## Responsabilités", "## HORS-PÉRIMÈTRE", "## Agrégats",
                         "## Événements publiés", "## Événements consommés"]


def verifier(depot: Depot) -> list[Constat]:
    try:
        bcs = depot.bounded_contexts
        interdits_partout = depot.interdits_partout
        evenements = depot.evenements
    except ArtefactIllisible as e:
        return [Constat(GATE, "contexts", None, str(e))]

    constats: list[Constat] = []
    ids_connus = {c["id"] for c in depot.context_map.get("contexts") or []}
    for e in evenements:
        for cote in (e.amont, e.aval):
            if cote not in ids_connus:
                constats.append(Constat(GATE, "contexts/context-map.yaml", None,
                                        f"l'événement {e.nom} cite le BC inconnu « {cote} »"))

    for bc in bcs:
        constats += _glossaire(depot, bc, interdits_partout)
        constats += _invariants(depot, bc)
        constats += _context_md(depot, bc)
    constats += _croisements(depot)
    return constats


def _glossaire(depot, bc, interdits_partout) -> list[Constat]:
    chemin = depot.relatif(bc.dossier / "glossary.yaml")
    brut = depot.racine / chemin
    constats = []
    contexte = (_charger(brut) or {}).get("context")
    if contexte != bc.id:
        constats.append(Constat(GATE, chemin, None, f"« context: {contexte} » au lieu de « {bc.id} »"))
    if not TERMES_MIN <= len(bc.termes) <= TERMES_MAX:
        constats.append(Constat(GATE, chemin, None,
                                f"{len(bc.termes)} termes, hors de la fourchette {TERMES_MIN} à {TERMES_MAX}"))
    noms = [t.term for t in bc.termes]
    for nom in {n for n in noms if noms.count(n) > 1}:
        constats.append(Constat(GATE, chemin, None, f"le terme {nom} est défini plusieurs fois"))
    interdits_globaux = {tuple(mots(x)) for x in interdits_partout}
    for t in bc.termes:
        if not NOM_DE_TERME.match(t.term):
            constats.append(Constat(GATE, chemin, None, f"« {t.term} » n'est pas un nom de terme en PascalCase sans accent"))
        if not t.definition.strip():
            constats.append(Constat(GATE, chemin, None, f"le terme {t.term} n'a pas de définition"))
        if t.aggregate and t.aggregate not in noms:
            constats.append(Constat(GATE, chemin, None,
                                    f"le terme {t.term} se rattache à l'agrégat {t.aggregate}, qui n'est pas un terme du glossaire"))
        if tuple(mots(t.term)) in interdits_globaux:
            constats.append(Constat(GATE, chemin, None, f"le terme {t.term} est interdit partout (CLAUDE.md)"))
        for x in t.forbidden:
            if x in noms:
                constats.append(Constat(GATE, chemin, None,
                                        f"le terme {t.term} interdit {x}, qui est lui-même un terme du glossaire"))
    return constats


def _invariants(depot, bc) -> list[Constat]:
    chemin = depot.relatif(bc.dossier / "invariants.yaml")
    constats = []
    contexte = (_charger(depot.racine / chemin) or {}).get("context")
    if contexte != bc.id:
        constats.append(Constat(GATE, chemin, None, f"« context: {contexte} » au lieu de « {bc.id} »"))
    ids = [i.id for i in bc.invariants]
    for i in {x for x in ids if ids.count(x) > 1}:
        constats.append(Constat(GATE, chemin, None, f"l'identifiant {i} est utilisé plusieurs fois"))
    prefixes = set()
    for inv in bc.invariants:
        m = ID_INVARIANT.match(inv.id)
        if not m:
            constats.append(Constat(GATE, chemin, None, f"« {inv.id} » ne suit pas le format INV-XXX-NNN"))
        else:
            prefixes.add(m.group(1))
        if inv.agregat not in bc.agregats:
            constats.append(Constat(GATE, chemin, None,
                                    f"{inv.id} porte sur {inv.agregat}, qui n'est pas un agrégat du glossaire"))
        for champ in ("regle", "exemple_violation"):
            if not getattr(inv, champ).strip():
                constats.append(Constat(GATE, chemin, None, f"{inv.id} n'a pas de champ « {champ} »"))
    if len(prefixes) > 1:
        constats.append(Constat(GATE, chemin, None, f"plusieurs préfixes d'invariants : {', '.join(sorted(prefixes))}"))
    return constats


def _context_md(depot, bc) -> list[Constat]:
    fichier = bc.dossier / "CONTEXT.md"
    chemin = depot.relatif(fichier)
    if not fichier.exists():
        return [Constat(GATE, chemin, None, "fichier absent")]
    texte = fichier.read_text(encoding="utf-8")
    constats = [Constat(GATE, chemin, None, f"section « {s[3:]} » absente")
                for s in SECTIONS_OBLIGATOIRES if s not in texte.splitlines()]

    declares_publies = {(e.nom, e.aval) for e in depot.evenements if e.amont == bc.id}
    declares_consommes = {(e.nom, e.amont) for e in depot.evenements if e.aval == bc.id}
    lus_publies = {(nom, autre) for nom, autre in _table(texte, "## Événements publiés")}
    lus_consommes = {(nom, autre) for nom, autre in _table(texte, "## Événements consommés")}
    constats += _ecarts(chemin, "publie", "vers", lus_publies, declares_publies)
    constats += _ecarts(chemin, "consomme", "depuis", lus_consommes, declares_consommes)

    agregats_md = {nom for nom, _ in _table(texte, "## Agrégats")}
    for a in sorted(agregats_md ^ bc.agregats):
        ou = "CONTEXT.md" if a in agregats_md else "glossary.yaml"
        constats.append(Constat(GATE, chemin, None, f"l'agrégat {a} n'apparaît que dans {ou}"))
    return constats


def _ecarts(chemin, verbe, prep, lus, declares) -> list[Constat]:
    constats = []
    for nom, autre in sorted(lus - declares):
        constats.append(Constat(GATE, chemin, None,
                                f"CONTEXT.md {verbe} {nom} {prep} {autre}, ce que contexts/context-map.yaml ne déclare pas"))
    for nom, autre in sorted(declares - lus):
        constats.append(Constat(GATE, chemin, None,
                                f"contexts/context-map.yaml déclare que ce BC {verbe} {nom} {prep} {autre}, CONTEXT.md ne le dit pas"))
    return constats


def _table(texte: str, titre: str) -> list[tuple[str, str]]:
    """(nom entre backquotes de la 1re colonne, BC cités en 2e colonne) pour chaque ligne de la table sous `titre`."""
    lignes = texte.splitlines()
    if titre not in lignes:
        return []
    resultat = []
    for ligne in lignes[lignes.index(titre) + 1:]:
        if ligne.startswith("#"):
            break
        cellules = [c.strip() for c in ligne.strip().strip("|").split("|")]
        if len(cellules) < 2 or not cellules[0].startswith("`"):
            continue
        nom = cellules[0].strip("`")
        autres = [a.strip() for a in cellules[1].split(",") if a.strip()]
        if titre == "## Agrégats":
            resultat.append((nom, ""))
        else:
            resultat += [(nom, a) for a in autres]
    return resultat


def _croisements(depot) -> list[Constat]:
    """Un terme défini dans un BC et interdit dans un autre : souvent voulu, toujours à savoir."""
    constats = []
    for bc in depot.bounded_contexts:
        noms = {t.term for t in bc.termes}
        for autre in depot.bounded_contexts:
            if autre is bc:
                continue
            for t in autre.termes:
                for x in t.forbidden:
                    if x in noms:
                        constats.append(Constat(
                            GATE, depot.relatif(autre.dossier / "glossary.yaml"), None,
                            f"{autre.id} interdit {x} (synonyme refusé de {t.term}), que {bc.id} définit comme terme",
                            bloquant=False))
    return constats


def _charger(chemin):
    from .depot import charger_yaml
    try:
        return charger_yaml(chemin)
    except ArtefactIllisible:
        return None
