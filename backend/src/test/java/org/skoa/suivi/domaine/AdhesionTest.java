package org.skoa.suivi.domaine;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.time.Instant;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

public class AdhesionTest {

    private static final UUID CAMILLE = UUID.fromString("00000000-0000-0000-0000-00000000c001");
    private static final UUID AGORAFOLKS = UUID.fromString("00000000-0000-0000-0000-00000000a001");
    private static final Instant LE_24_NOVEMBRE = Instant.parse("2026-11-24T10:00:00Z");

    @Test
    @DisplayName("Une Adhesion enregistrée porte l'Adherent, la Structure et sa date d'enregistrement")
    void enregistrer() {
        UUID adhesionId = UUID.fromString("00000000-0000-0000-0000-0000000ad001");
        Adhesion adhesion = Adhesion.enregistrer(adhesionId, CAMILLE, AGORAFOLKS, LE_24_NOVEMBRE, new AdhesionsEnMemoire() );
        assertThat(adhesion.adherentId()).isEqualTo(CAMILLE);
        assertThat(adhesion.structureId()).isEqualTo(AGORAFOLKS);
        assertThat(adhesion.enregistreeLe()).isEqualTo(LE_24_NOVEMBRE);
        assertThat(adhesion.id()).isEqualTo(adhesionId);
    }

    @Test
    @DisplayName("INV-SUI-008 La seconde Adhesion de Camille chez AgoraFolks est refusée")
    void enregistrerDoublonRenvoieErreur() {
        UUID adhesionId = UUID.fromString("00000000-0000-0000-0000-0000000ad001");
        UUID adhesionIdAutre = UUID.fromString("00000000-0000-0000-0000-0000000ad002");
        AdhesionsEnMemoire adhesionsEnMemoire = new AdhesionsEnMemoire();
        adhesionsEnMemoire.ajouter(Adhesion.enregistrer(adhesionId, CAMILLE, AGORAFOLKS, LE_24_NOVEMBRE, adhesionsEnMemoire));

        assertThatThrownBy(()->Adhesion.enregistrer(adhesionIdAutre, CAMILLE, AGORAFOLKS, LE_24_NOVEMBRE, adhesionsEnMemoire))
                .isInstanceOf(IllegalStateException.class);

    }
}
