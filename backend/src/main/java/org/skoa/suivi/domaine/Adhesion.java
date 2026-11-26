package org.skoa.suivi.domaine;

import java.time.Instant;
import java.util.UUID;

public class Adhesion {
    private final UUID id;
    private final UUID adherentId;
    private final UUID structureId;
    private final Instant enregistreeLe;

    private Adhesion(UUID id, UUID adherentId, UUID structureId, Instant enregistreeLe) {
        this.id = id;
        this.adherentId = adherentId;
        this.structureId = structureId;
        this.enregistreeLe = enregistreeLe;
    }

    public UUID id() { return id; }
    public UUID adherentId() { return adherentId; }
    public UUID structureId() { return structureId; }
    public Instant enregistreeLe() { return enregistreeLe; }

    public static Adhesion enregistrer(UUID adhesionId, UUID adherentId, UUID structureId,
                                       Instant enregistreeLe, Adhesions adhesions) {
        if(adhesions.aUneAdhesionEnCours(adherentId,structureId)) {
            throw new IllegalStateException("INV-SUI-008 : cet Adherent a déjà une Adhesion en cours dans cette Structure");
        }
        return new Adhesion(adhesionId, adherentId, structureId, enregistreeLe);
    }


}
