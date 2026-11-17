"""Gate « invariants » : chaque invariant d'un agrégat écrit est prouvé par au moins un test.

Règle d'activation (ADR-002, choix du 2026-11-17) : un invariant n'est exigé que lorsque
son agrégat existe dans le code du BC, c'est-à-dire qu'une classe, un record, une interface
ou un enum porte exactement le nom de l'agrégat sous backend/src/main/java/org/skoa/<bc>/.
Il n'y a pas de liste de dérogations : rien qu'un agent puisse allonger pour passer.

Un test cite un invariant par son identifiant dans une chaîne (nom affiché du test,
@DisplayName, describe/it). Un commentaire ne compte pas.
"""

from __future__ import annotations

import re

from .depot import ArtefactIllisible, BoundedContext, Depot
from .rapport import Constat
from .texte import decouper

GATE = "invariants"
EXPLICATION = (
    "Chaque invariant de contexts/<bc>/invariants.yaml dont l'agrégat existe doit être cité,\n"
    "par son identifiant, dans le nom d'au moins un test du même BC.\n"
    "Exemple : @DisplayName(\"INV-MER-005 un Adherent n'est jamais sollicité pour sa propre Demande\")."
)
REFERENCE = re.compile(r"\bINV-[A-Z]{3}-\d{3}\b")


def verifier(depot: Depot) -> list[Constat]:
    try:
        bcs = depot.bounded_contexts
    except ArtefactIllisible as e:
        return [Constat(GATE, "contexts", None, f"{e} (lance d'abord la gate artefacts)")]

    tous_les_ids = {i.id: bc.id for bc in bcs for i in bc.invariants}
    constats = []
    for bc in bcs:
        couverts = set()
        for fichier in depot.tests_du_bc(bc):
            for seg in decouper(fichier.read_text(encoding="utf-8")).chaines:
                for m in REFERENCE.finditer(seg.texte):
                    ident = m.group()
                    ligne = seg.ligne + seg.texte.count("\n", 0, m.start())
                    chemin = depot.relatif(fichier)
                    if ident not in tous_les_ids:
                        constats.append(Constat(GATE, chemin, ligne, f"{ident} n'existe dans aucun invariants.yaml"))
                    elif tous_les_ids[ident] != bc.id:
                        constats.append(Constat(GATE, chemin, ligne,
                                                f"{ident} est un invariant de {tous_les_ids[ident]}, pas de {bc.id} : "
                                                "un BC ne prouve que ses propres règles"))
                    else:
                        couverts.add(ident)

        ecrits = agregats_ecrits(depot, bc)
        chemin_inv = depot.relatif(bc.dossier / "invariants.yaml")
        en_attente: dict[str, list[str]] = {}
        for inv in bc.invariants:
            if inv.id in couverts:
                continue
            if inv.agregat in ecrits:
                constats.append(Constat(GATE, chemin_inv, None,
                                        f"{inv.id} ({inv.agregat}) n'est cité par aucun test de {bc.id} : {inv.regle}"))
            else:
                en_attente.setdefault(inv.agregat, []).append(inv.id)
        for agregat, ids in sorted(en_attente.items()):
            constats.append(Constat(GATE, chemin_inv, None,
                                    f"agrégat {agregat} pas encore écrit : {', '.join(ids)} en attente",
                                    bloquant=False))
    return constats


def agregats_ecrits(depot: Depot, bc: BoundedContext) -> set[str]:
    declarations = set()
    for fichier in depot.code_principal_du_bc(bc):
        for seg in decouper(fichier.read_text(encoding="utf-8")).code:
            declarations.update(re.findall(r"\b(?:class|record|interface|enum)\s+([A-Z]\w*)", seg.texte))
    return declarations & bc.agregats
