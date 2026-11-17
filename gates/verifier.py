"""Lance les gates DDD de skoa.

    python3 gates/verifier.py              # toutes les gates
    python3 gates/verifier.py langage      # une seule : artefacts, langage ou invariants

Code de sortie 1 si une gate trouve au moins une erreur.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from skoa_gates import artefacts, invariants, langage  # noqa: E402
from skoa_gates.depot import Depot  # noqa: E402
from skoa_gates.rapport import imprimer  # noqa: E402

GATES = {"artefacts": artefacts, "langage": langage, "invariants": invariants}


def main(arguments: list[str]) -> int:
    parseur = argparse.ArgumentParser(description="Gates DDD de skoa")
    parseur.add_argument("gates", nargs="*", metavar="gate", help=f"{', '.join(GATES)} (toutes par défaut)")
    parseur.add_argument("--racine", type=Path, default=Path(__file__).resolve().parent.parent,
                         help="racine du dépôt (par défaut, le dépôt qui contient ce script)")
    args = parseur.parse_args(arguments)
    inconnues = [g for g in args.gates if g not in GATES]
    if inconnues:
        parseur.error(f"gate inconnue : {', '.join(inconnues)}")

    depot = Depot(args.racine)
    code = 0
    for nom in args.gates or list(GATES):
        module = GATES[nom]
        code |= imprimer(nom, module.verifier(depot), module.EXPLICATION)
        print()
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
