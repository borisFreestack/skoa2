package org.skoa.suivi.domaine;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/**
 * Fausse implémentation du port, pour les tests : une liste en mémoire.
 */
class AdhesionsEnMemoire implements Adhesions {

    private final List<Adhesion> adhesions = new ArrayList<>();

    public void ajouter(Adhesion adhesion) {
        adhesions.add(adhesion);
    }

    @Override
    public boolean aUneAdhesionEnCours(UUID adherentId, UUID structureId) {
        return adhesions.stream()
                .anyMatch(a -> a.adherentId().equals(adherentId) && a.structureId().equals(structureId));
    }
}