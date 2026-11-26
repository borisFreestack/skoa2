package org.skoa.suivi.domaine;

import java.util.UUID;

public interface Adhesions {
    boolean aUneAdhesionEnCours(UUID adherentId, UUID structureId);
}
