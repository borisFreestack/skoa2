"""Gate « langage » : aucun nom choisi dans le code ou les contrats n'emploie un terme interdit.

- Partout : les termes de la section « Vocabulaire interdit partout » de CLAUDE.md.
- Dans le code et le contrat d'un BC : en plus, les synonymes refusés (`forbidden`) de son glossaire.

Sont jugés les identifiants du code Java et TypeScript et les noms des contrats OpenAPI
(chemins, operationId, schémas, propriétés, paramètres, valeurs d'enum). Ne sont pas jugés :
les commentaires, le texte des chaînes, les descriptions, et les noms importés d'une
bibliothèque tierce (ce n'est pas nous qui les avons choisis).

Un terme du glossaire ou un événement de la context map peut contenir un mot interdit
(« BesoinDEnParler » contient « Besoin ») : la partie du nom qui forme un terme autorisé
n'est pas jugée.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from .depot import ArtefactIllisible, BoundedContext, Depot
from .rapport import Constat
from .texte import decouper, identifiants, mots, noms_externes, occurrences

GATE = "langage"
EXPLICATION = (
    "N'emploie que les termes du glossary.yaml de ton BC (CLAUDE.md, règle 2).\n"
    "Si aucun terme ne convient, propose un ajout au glossaire dans la PR (règle 3) au lieu d'inventer un nom."
)
CLES_DE_TEXTE = {"description", "summary", "title", "example", "examples", "externalDocs", "info", "servers"}
# Les clés de ces objets sont des noms qu'on choisit ; les autres clés sont des mots-clés OpenAPI
# (« minimum », « format »…), qu'on ne juge pas.
CLES_NOMMANTES = {"properties", "schemas", "parameters", "requestBodies", "responses", "headers", "securitySchemes"}


class Regles:
    """Les motifs interdits et autorisés applicables à un fichier."""

    def __init__(self, depot: Depot, bc: BoundedContext | None):
        self.interdits: list[tuple[list[str], str]] = [(mots(x), "interdit partout (CLAUDE.md)")
                                                       for x in depot.interdits_partout]
        self.autorises: list[list[str]] = []
        if bc:
            for t in bc.termes:
                self.interdits += [(mots(x), f"synonyme refusé de {t.term} ({bc.id})") for x in t.forbidden]
                self.autorises.append(mots(t.term))
            self.autorises += [mots(e) for e in depot.evenements_du_bc(bc.id)]

    def juger(self, nom: str) -> list[str]:
        sequence = mots(nom)
        couverts = set()
        for motif in self.autorises:
            for i in occurrences(sequence, motif):
                couverts.update(range(i, i + len(motif)))
        raisons = []
        for motif, raison in self.interdits:
            for i in occurrences(sequence, motif):
                if not set(range(i, i + len(motif))) <= couverts:
                    raisons.append(f"« {nom} » contient « {''.join(m.capitalize() for m in motif)} », {raison}")
                    break
        return raisons


def verifier(depot: Depot) -> list[Constat]:
    try:
        depot.interdits_partout
        depot.bounded_contexts
    except ArtefactIllisible as e:
        return [Constat(GATE, "contexts", None, f"{e} (lance d'abord la gate artefacts)")]

    constats = []
    for fichier in depot.sources_code():
        constats += _juger_code(depot, fichier)
    for fichier in depot.contrats():
        constats += _juger_contrat(depot, fichier)
    return constats


def _juger_code(depot: Depot, fichier: Path) -> list[Constat]:
    regles = Regles(depot, depot.bc_du_fichier(fichier))
    source = fichier.read_text(encoding="utf-8")
    externes = noms_externes(source, fichier.suffix)
    deja_vus: set[tuple[str, int]] = set()
    constats = []
    for nom, ligne in identifiants(decouper(source)):
        if nom in externes or (nom, ligne) in deja_vus:
            continue
        deja_vus.add((nom, ligne))
        for raison in regles.juger(nom):
            constats.append(Constat(GATE, depot.relatif(fichier), ligne, raison))
    return constats


def _juger_contrat(depot: Depot, fichier: Path) -> list[Constat]:
    regles = Regles(depot, depot.bc_du_fichier(fichier))
    try:
        racine = yaml.compose(fichier.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        return [Constat(GATE, depot.relatif(fichier), None, f"YAML invalide ({e})")]
    constats = []
    for nom, ligne in _noms_du_contrat(racine):
        for raison in regles.juger(nom):
            constats.append(Constat(GATE, depot.relatif(fichier), ligne, raison))
    return constats


def _noms_du_contrat(noeud, cle_parente: str | None = None):
    """(nom, ligne) des noms choisis dans un contrat OpenAPI, sans le texte libre."""
    if noeud is None:
        return
    ligne = noeud.start_mark.line + 1
    if isinstance(noeud, yaml.MappingNode):
        for cle, valeur in noeud.value:
            nom_cle = cle.value
            if nom_cle in CLES_DE_TEXTE:
                continue
            if cle_parente == "paths":
                for morceau in nom_cle.replace("{", "/").replace("}", "/").split("/"):
                    if morceau:
                        yield morceau, cle.start_mark.line + 1
            elif cle_parente in CLES_NOMMANTES:
                yield nom_cle, cle.start_mark.line + 1
            if nom_cle in ("operationId", "name") and isinstance(valeur, yaml.ScalarNode):
                yield valeur.value, valeur.start_mark.line + 1
            elif nom_cle == "$ref" and isinstance(valeur, yaml.ScalarNode):
                yield valeur.value.rsplit("/", 1)[-1], valeur.start_mark.line + 1
            else:
                yield from _noms_du_contrat(valeur, nom_cle)
    elif isinstance(noeud, yaml.SequenceNode):
        for element in noeud.value:
            yield from _noms_du_contrat(element, cle_parente)
    elif isinstance(noeud, yaml.ScalarNode) and cle_parente in ("enum", "tags", "required"):
        yield noeud.value, ligne
