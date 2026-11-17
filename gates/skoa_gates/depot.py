"""Lecture du dépôt : artefacts de contexts/, fichiers sources et rattachement à un BC.

Rien n'est dupliqué ici : la liste des BC vient de contexts/context-map.yaml,
le vocabulaire interdit partout vient de CLAUDE.md.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path

import yaml

SECTION_INTERDITS = "## Vocabulaire interdit partout"


class ArtefactIllisible(Exception):
    """Un artefact de contexts/ ou CLAUDE.md ne peut pas être lu : les autres gates n'ont pas de base."""


@dataclass
class Terme:
    term: str
    definition: str
    forbidden: list[str]
    aggregate: str | None


@dataclass
class Invariant:
    id: str
    regle: str
    agregat: str
    exemple_violation: str


@dataclass
class BoundedContext:
    id: str
    dossier: Path
    termes: list[Terme] = field(default_factory=list)
    invariants: list[Invariant] = field(default_factory=list)

    @property
    def paquet(self) -> str:
        """Nom du paquet Java du BC : « mise-en-relation » devient « miseenrelation »."""
        return self.id.replace("-", "")

    @property
    def agregats(self) -> set[str]:
        return {t.aggregate for t in self.termes if t.aggregate}


@dataclass
class Evenement:
    nom: str
    amont: str
    aval: str
    payload: list[str]


def charger_yaml(chemin: Path):
    try:
        with chemin.open(encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError as e:
        raise ArtefactIllisible(f"{chemin} : fichier absent") from e
    except yaml.YAMLError as e:
        raise ArtefactIllisible(f"{chemin} : YAML invalide ({e})") from e


class Depot:
    def __init__(self, racine: Path):
        self.racine = racine.resolve()

    # --- artefacts -------------------------------------------------------

    @cached_property
    def context_map(self) -> dict:
        return charger_yaml(self.racine / "contexts" / "context-map.yaml")

    @cached_property
    def bounded_contexts(self) -> list[BoundedContext]:
        """Les BC modélisés (ceux qui ont un dossier), dans l'ordre de la context map."""
        bcs = []
        for c in self.context_map.get("contexts") or []:
            if not c.get("dossier"):
                continue
            dossier = self.racine / c["dossier"]
            bc = BoundedContext(id=c["id"], dossier=dossier)
            glossaire = charger_yaml(dossier / "glossary.yaml") or {}
            for t in glossaire.get("terms") or []:
                bc.termes.append(Terme(
                    term=str(t.get("term", "")),
                    definition=str(t.get("definition", "")),
                    forbidden=[str(x) for x in (t.get("forbidden") or [])],
                    aggregate=t.get("aggregate"),
                ))
            invariants = charger_yaml(dossier / "invariants.yaml") or {}
            for i in invariants.get("invariants") or []:
                bc.invariants.append(Invariant(
                    id=str(i.get("id", "")),
                    regle=str(i.get("regle", "")),
                    agregat=str(i.get("agregat", "")),
                    exemple_violation=str(i.get("exemple_violation", "")),
                ))
            bcs.append(bc)
        return bcs

    def bc(self, id_bc: str) -> BoundedContext:
        return next(b for b in self.bounded_contexts if b.id == id_bc)

    @cached_property
    def evenements(self) -> list[Evenement]:
        """Un élément par couple (événement, aval) déclaré dans la context map."""
        resultat = []
        for r in self.context_map.get("relations") or []:
            avals = r.get("downstream")
            avals = avals if isinstance(avals, list) else [avals]
            for e in r.get("events") or []:
                for aval in avals:
                    resultat.append(Evenement(e["name"], r["upstream"], aval, list(e.get("payload") or [])))
        return resultat

    def evenements_du_bc(self, id_bc: str) -> set[str]:
        """Noms des événements que le BC publie ou consomme."""
        return {e.nom for e in self.evenements if id_bc in (e.amont, e.aval)}

    @cached_property
    def interdits_partout(self) -> list[str]:
        """Les termes entre backquotes du premier paragraphe de la section « Vocabulaire interdit partout » de CLAUDE.md."""
        chemin = self.racine / "CLAUDE.md"
        if not chemin.exists():
            raise ArtefactIllisible(f"{chemin} : fichier absent")
        lignes = chemin.read_text(encoding="utf-8").splitlines()
        try:
            debut = next(i for i, l in enumerate(lignes) if l.strip() == SECTION_INTERDITS)
        except StopIteration as e:
            raise ArtefactIllisible(f"CLAUDE.md : section « {SECTION_INTERDITS[3:]} » introuvable") from e
        paragraphe = []
        for ligne in lignes[debut + 1:]:
            if ligne.startswith("#"):
                break
            if not ligne.strip():
                if paragraphe:
                    break
                continue
            paragraphe.append(ligne)
        termes = re.findall(r"`([^`]+)`", " ".join(paragraphe))
        if not termes:
            raise ArtefactIllisible("CLAUDE.md : aucun terme entre backquotes sous « Vocabulaire interdit partout »")
        return termes

    # --- sources ---------------------------------------------------------

    @cached_property
    def fichiers(self) -> list[Path]:
        """Fichiers suivis ou nouveaux, hors .gitignore (donc hors code généré et build/)."""
        sortie = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
            cwd=self.racine, capture_output=True, text=True, check=True,
        ).stdout
        chemins = (self.racine / p for p in sortie.split("\0") if p)
        return sorted(p for p in chemins if p.is_file())

    def relatif(self, chemin: Path) -> str:
        return chemin.relative_to(self.racine).as_posix()

    def bc_du_fichier(self, chemin: Path) -> BoundedContext | None:
        """Le BC auquel appartient un fichier source, ou None pour le code partagé (shell, application)."""
        rel = self.relatif(chemin)
        for bc in self.bounded_contexts:
            if (rel.startswith(f"backend/src/main/java/org/skoa/{bc.paquet}/")
                    or rel.startswith(f"backend/src/test/java/org/skoa/{bc.paquet}/")
                    or rel.startswith(f"frontend/src/app/{bc.id}/")
                    or rel.startswith(f"contracts/{bc.id}/")):
                return bc
        return None

    def sources_code(self) -> list[Path]:
        """Code Java et TypeScript de l'application."""
        return [p for p in self.fichiers
                if (self.relatif(p).startswith("backend/src/") and p.suffix == ".java")
                or (self.relatif(p).startswith("frontend/src/") and p.suffix == ".ts")]

    def contrats(self) -> list[Path]:
        return [p for p in self.fichiers
                if self.relatif(p).startswith("contracts/") and p.name == "openapi.yaml"]

    def tests_du_bc(self, bc: BoundedContext) -> list[Path]:
        return [p for p in self.fichiers
                if (self.relatif(p).startswith(f"backend/src/test/java/org/skoa/{bc.paquet}/") and p.suffix == ".java")
                or (self.relatif(p).startswith(f"frontend/src/app/{bc.id}/") and p.name.endswith(".spec.ts"))]

    def code_principal_du_bc(self, bc: BoundedContext) -> list[Path]:
        prefixe = f"backend/src/main/java/org/skoa/{bc.paquet}/"
        return [p for p in self.fichiers if self.relatif(p).startswith(prefixe) and p.suffix == ".java"]
