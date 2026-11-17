"""Format commun des rapports : une ligne par constat, lisible par un humain et par un agent."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Constat:
    gate: str
    chemin: str
    ligne: int | None
    message: str
    bloquant: bool = True

    def __str__(self) -> str:
        position = f"{self.chemin}:{self.ligne}" if self.ligne else self.chemin
        niveau = "ERREUR" if self.bloquant else "AVERTISSEMENT"
        return f"{position}: {niveau} [{self.gate}] {self.message}"


def imprimer(gate: str, constats: list[Constat], explication: str) -> int:
    """Imprime le rapport et renvoie le code de sortie (1 si au moins un constat bloquant)."""
    erreurs = [c for c in constats if c.bloquant]
    avertissements = [c for c in constats if not c.bloquant]
    for c in sorted(constats, key=lambda c: (not c.bloquant, c.chemin, c.ligne or 0)):
        print(c)
    if erreurs:
        print(f"\n✗ {gate} : {len(erreurs)} erreur(s), {len(avertissements)} avertissement(s).")
        print(explication)
        return 1
    print(f"✓ {gate} : aucune erreur, {len(avertissements)} avertissement(s).")
    return 0
