"""Gate « tests rejoués sur la branche de base » : un test ajouté par une PR doit échouer sans le code qu'il accompagne.

Un test qui passe déjà sur la branche de base ne prouve rien du code de la PR : soit il teste
un comportement qui existait, soit il ne vérifie rien. C'est la preuve, après coup, que le test
a été vu rouge avant le code (TDD).

    python3 gates/tests_rejoues.py [--base origin/main]

Trois passes de `./gradlew :backend:test` :
  1. l'arbre courant (la PR), pour connaître ses tests ;
  2. la base (le point où la PR a quitté --base), dans un worktree temporaire, pour connaître les tests qui existaient ;
  3. le même worktree, avec les tests des BC de la PR, pour voir chaque nouveau test rejoué sans le code de la PR.

Un nouveau test est un test (classe et nom affiché) présent en 1 et absent en 2. Seuls comptent
les tests rangés dans un paquet de BC (`org.skoa.<bc>..`) : les tests des gates, à la racine
de `org.skoa`, accompagnent du code de test, pas du code de production.

Un test qui ne compile pas sans le code de la PR est rouge : c'est souvent le premier rouge du TDD.

Code de sortie 1 si un nouveau test passe (ou est ignoré) sur la base, 2 si une passe n'a pas pu tourner.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from skoa_gates.depot import Depot  # noqa: E402
from skoa_gates.rapport import Constat, imprimer  # noqa: E402

GATE = "tests-rejoues"
EXPLICATION = (
    "Un nouveau test doit échouer sur la branche de base, sans le code de la PR : sinon il ne prouve rien de ce code.\n"
    "Écris d'abord le test, vois-le échouer, puis écris le code. Un test qui reformule un comportement existant\n"
    "n'est pas nouveau : modifie le test existant plutôt que d'en ajouter un."
)
SOURCES_DE_TEST = "backend/src/test/java/"
RESULTATS = "backend/build/test-results/test"


class Statut(Enum):
    PASSE = "passe"
    ECHOUE = "échoue"
    IGNORE = "ignoré"


@dataclass(frozen=True)
class Passe:
    """Résultat d'une exécution des tests : statut par test, ou compilation des tests impossible."""
    resultats: dict[tuple[str, str], Statut]
    compilation_echouee: bool = False


def dossiers_de_test(paquets: list[str]) -> list[str]:
    return [f"{SOURCES_DE_TEST}org/skoa/{p}/" for p in paquets]


def est_un_test_de_bc(classe: str, paquets: list[str]) -> bool:
    return any(classe.startswith(f"org.skoa.{p}.") for p in paquets)


def touche_les_tests(chemins: list[str], paquets: list[str]) -> bool:
    dossiers = dossiers_de_test(paquets)
    return any(c.startswith(d) for c in chemins for d in dossiers)


def chemin_du_test(classe: str) -> str:
    return SOURCES_DE_TEST + classe.split("$", 1)[0].replace(".", "/") + ".java"


def lire_resultats(dossier: Path) -> dict[tuple[str, str], Statut]:
    """Lit les rapports JUnit XML de Gradle : un statut par (classe, nom affiché du test)."""
    resultats = {}
    for fichier in sorted(dossier.glob("TEST-*.xml")):
        for cas in ET.parse(fichier).getroot().iter("testcase"):
            if cas.find("skipped") is not None:
                statut = Statut.IGNORE
            elif cas.find("failure") is not None or cas.find("error") is not None:
                statut = Statut.ECHOUE
            else:
                statut = Statut.PASSE
            resultats[(cas.get("classname"), cas.get("name"))] = statut
    return resultats


def juger(tete: Passe, base: Passe, rejouee: Passe | None, paquets: list[str]) -> tuple[list[Constat], list[str]]:
    """Renvoie les constats bloquants et, pour le rapport, une ligne par nouveau test rouge."""
    nouveaux = sorted(t for t in tete.resultats if est_un_test_de_bc(t[0], paquets) and t not in base.resultats)
    constats, rouges = [], []
    for classe, nom in nouveaux:
        test = f"{classe.rsplit('.', 1)[-1]} « {nom} »"
        if rejouee is None or rejouee.compilation_echouee:
            rouges.append(f"{test} : rouge, ne compile pas sans le code de la PR")
            continue
        statut = rejouee.resultats.get((classe, nom))
        if statut is Statut.ECHOUE:
            rouges.append(f"{test} : rouge")
        elif statut is Statut.PASSE:
            constats.append(Constat(GATE, chemin_du_test(classe), None,
                                    f"{test} passe déjà sur la branche de base : il ne prouve rien du code de la PR"))
        elif statut is Statut.IGNORE:
            constats.append(Constat(GATE, chemin_du_test(classe), None,
                                    f"{test} est ignoré sur la branche de base : un test désactivé ne prouve rien"))
        else:
            constats.append(Constat(GATE, chemin_du_test(classe), None,
                                    f"{test} n'a pas été exécuté sur la branche de base"))
    return constats, rouges


# --- exécution -----------------------------------------------------------


class PasseImpossible(Exception):
    pass


def git(racine: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(racine), *args], check=True, capture_output=True, text=True).stdout


def fichiers_modifies(racine: Path, depart: str) -> list[str]:
    """Fichiers modifiés depuis le point de départ, y compris les changements locaux non commités."""
    suivis = git(racine, "diff", "--name-only", depart).splitlines()
    nouveaux = git(racine, "ls-files", "--others", "--exclude-standard").splitlines()
    return suivis + nouveaux


def executer_les_tests(arbre: Path, etiquette: str) -> Passe:
    resultats = arbre / RESULTATS
    shutil.rmtree(resultats, ignore_errors=True)
    print(f"→ tests de {etiquette}…", flush=True)
    proc = subprocess.run([str(arbre / "gradlew"), "-p", str(arbre), ":backend:cleanTest", ":backend:test",
                           "--console=plain", "--quiet"],
                          capture_output=True, text=True, env=os.environ)
    sortie = proc.stdout + proc.stderr
    if proc.returncode != 0 and "task ':backend:compileTestJava'" in sortie:
        return Passe({}, compilation_echouee=True)
    if proc.returncode != 0 and not resultats.is_dir():
        raise PasseImpossible(f"les tests de {etiquette} n'ont pas pu tourner :\n{sortie[-3000:]}")
    return Passe(lire_resultats(resultats))


def recopier_les_tests(source: Path, cible: Path, paquets: list[str]) -> None:
    for dossier in dossiers_de_test(paquets):
        shutil.rmtree(cible / dossier, ignore_errors=True)
        if (source / dossier).is_dir():
            shutil.copytree(source / dossier, cible / dossier)


def main(arguments: list[str]) -> int:
    parseur = argparse.ArgumentParser(description="Gate « tests rejoués sur la branche de base »")
    parseur.add_argument("--base", default="origin/main", help="branche de base (par défaut origin/main)")
    parseur.add_argument("--racine", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parseur.parse_args(arguments)
    racine = args.racine.resolve()

    paquets = [bc.paquet for bc in Depot(racine).bounded_contexts]
    depart = git(racine, "merge-base", args.base, "HEAD").strip()
    if not touche_les_tests(fichiers_modifies(racine, depart), paquets):
        print(f"✓ {GATE} : aucun test de BC modifié depuis {args.base}, rien à rejouer.")
        return 0

    worktree = Path(tempfile.mkdtemp(prefix="skoa-base-"))
    try:
        git(racine, "worktree", "add", "--detach", str(worktree), depart)
        tete = executer_les_tests(racine, "la PR")
        if tete.compilation_echouee:
            raise PasseImpossible("les tests de la PR ne compilent pas : le check « Backend » le signale déjà")
        base = executer_les_tests(worktree, f"la base ({depart[:8]})")
        rejouee = None
        if any(est_un_test_de_bc(t[0], paquets) and t not in base.resultats for t in tete.resultats):
            recopier_les_tests(racine, worktree, paquets)
            rejouee = executer_les_tests(worktree, "la base, avec les tests de la PR")
    except PasseImpossible as e:
        print(f"✗ {GATE} : {e}")
        return 2
    finally:
        subprocess.run(["git", "-C", str(racine), "worktree", "remove", "--force", str(worktree)], capture_output=True)
        shutil.rmtree(worktree, ignore_errors=True)

    constats, rouges = juger(tete, base, rejouee, paquets)
    if rouges:
        print(f"Nouveaux tests rouges sur la base ({len(rouges)}) :")
        for ligne in rouges:
            print(f"  {ligne}")
        print()
    return imprimer(GATE, constats, EXPLICATION)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
