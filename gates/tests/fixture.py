"""Un dépôt skoa minimal et valide, dans un dossier temporaire, que chaque test abîme à sa façon.

Les termes interdits apparaissent ici, volontairement : c'est ce que les gates doivent attraper.
gates/ n'est pas analysé par la gate de langage.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from skoa_gates.depot import Depot  # noqa: E402

CLAUDE_MD = """\
# skoa

## Vocabulaire interdit partout

`Patient`, `Client`, `Aidant`.
Le domaine n'emploie pas ces mots.
"""

CONTEXT_MAP = """\
version: 1
contexts:
  - id: alpha
    dossier: contexts/alpha
  - id: beta
    dossier: contexts/beta
relations:
  - upstream: alpha
    downstream: beta
    events:
      - name: DemandeAcceptee
        payload: [demandeId]
"""


def glossaire(bc: str, termes: list[tuple[str, list[str], str | None]]) -> str:
    lignes = [f"context: {bc}", "terms:"]
    for nom, interdits, agregat in termes:
        lignes += [f"  - term: {nom}",
                   f"    definition: Définition de {nom}.",
                   f"    forbidden: [{', '.join(interdits)}]",
                   f"    aggregate: {agregat or 'null'}"]
    return "\n".join(lignes) + "\n"


def termes_de_remplissage(prefixe: str, n: int) -> list[tuple[str, list[str], str | None]]:
    lettres = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return [(f"{prefixe}{lettres[i]}", [], None) for i in range(n)]


def context_md(publies: list[tuple[str, str]], consommes: list[tuple[str, str]], agregats: list[str]) -> str:
    lignes = ["# BC", "", "## Mission", "m", "", "## Responsabilités", "r", "", "## HORS-PÉRIMÈTRE", "h", "",
              "## Agrégats", "| Agrégat | Racine |", "|---|---|"]
    lignes += [f"| `{a}` | racine |" for a in agregats]
    lignes += ["", "## Événements publiés", "| Événement | Consommé par |", "|---|---|"]
    lignes += [f"| `{e}` | {bc} |" for e, bc in publies]
    lignes += ["", "## Événements consommés", "| Événement | Émis par | Effet |", "|---|---|---|"]
    lignes += [f"| `{e}` | {bc} | effet |" for e, bc in consommes]
    return "\n".join(lignes) + "\n"


class DepotDeTest:
    def __init__(self):
        self._dossier = tempfile.TemporaryDirectory()
        self.racine = Path(self._dossier.name)
        self.ecrire("CLAUDE.md", CLAUDE_MD)
        self.ecrire("contexts/context-map.yaml", CONTEXT_MAP)
        self.ecrire("contexts/alpha/glossary.yaml", glossaire("alpha", [
            ("Demande", ["Requete", "Besoin"], "Demande"),
            ("BesoinDEnParler", [], "Demande"),
            ("Preneur", ["Benevole"], "Demande"),
            *termes_de_remplissage("Terme", 12),
        ]))
        self.ecrire("contexts/alpha/invariants.yaml", textwrap.dedent("""\
            context: alpha
            invariants:
              - id: INV-ALP-001
                regle: Une Demande a un Preneur au plus.
                agregat: Demande
                exemple_violation: Deux Preneurs.
            """))
        self.ecrire("contexts/alpha/CONTEXT.md", context_md([("DemandeAcceptee", "beta")], [], ["Demande"]))
        self.ecrire("contexts/beta/glossary.yaml", glossaire("beta", [
            ("Rencontre", ["Seance"], "Rencontre"),
            *termes_de_remplissage("Mot", 14),
        ]))
        self.ecrire("contexts/beta/invariants.yaml", textwrap.dedent("""\
            context: beta
            invariants:
              - id: INV-BET-001
                regle: Une Rencontre a deux participants.
                agregat: Rencontre
                exemple_violation: Une Rencontre à trois.
            """))
        self.ecrire("contexts/beta/CONTEXT.md", context_md([], [("DemandeAcceptee", "alpha")], ["Rencontre"]))
        subprocess.run(["git", "init", "-q"], cwd=self.racine, check=True)

    def ecrire(self, chemin: str, contenu: str):
        fichier = self.racine / chemin
        fichier.parent.mkdir(parents=True, exist_ok=True)
        fichier.write_text(contenu, encoding="utf-8")

    def remplacer(self, chemin: str, avant: str, apres: str):
        fichier = self.racine / chemin
        texte = fichier.read_text(encoding="utf-8")
        assert avant in texte, f"{avant!r} absent de {chemin}"
        fichier.write_text(texte.replace(avant, apres), encoding="utf-8")

    def depot(self) -> Depot:
        return Depot(self.racine)

    def fermer(self):
        self._dossier.cleanup()


def erreurs(constats) -> list[str]:
    return [c.message for c in constats if c.bloquant]
