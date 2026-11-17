package org.skoa;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.List;

import org.junit.jupiter.api.Test;
import org.skoa.ConformiteContextMap.Dependance;
import org.skoa.ConformiteContextMap.Evenement;
import org.skoa.ConformiteContextMap.TypeEvenement;

/** Prouve que la gate « conformité à la context map » échoue sur chaque violation, avec des faits fabriqués. */
class ConformiteContextMapTest {

    private final ConformiteContextMap gate = new ConformiteContextMap(List.of(
            new Evenement("DemandeAcceptee", "mise-en-relation", "rencontre", List.of("demandeId", "preneurId")),
            new Evenement("DemandeAcceptee", "mise-en-relation", "suivi", List.of("demandeId", "structureId")),
            new Evenement("RencontreAnnulee", "rencontre", "mise-en-relation", List.of("rencontreId"))));

    private static final String DEMANDE_ACCEPTEE = "org.skoa.miseenrelation.evenements.DemandeAcceptee";

    @Test
    void uneDependanceAUnEvenementDeclarePasse() {
        var d = new Dependance("rencontre", "org.skoa.rencontre.OuvertureDeRencontre", "miseenrelation", DEMANDE_ACCEPTEE);
        assertThat(gate.verifier(List.of(d), List.of())).isEmpty();
    }

    @Test
    void uneDependanceAuCodeInterneDUnAutreBcBloque() {
        var d = new Dependance("rencontre", "org.skoa.rencontre.OuvertureDeRencontre", "miseenrelation",
                "org.skoa.miseenrelation.Demande");
        assertThat(gate.verifier(List.of(d), List.of())).singleElement().asString()
                .contains("dépend de org.skoa.miseenrelation.Demande");
    }

    @Test
    void uneDependanceAUnEvenementDeclareVersUnAutreBcBloque() {
        var d = new Dependance("rencontre", "org.skoa.rencontre.Rencontre", "suivi", "org.skoa.suivi.evenements.StructureCreee");
        assertThat(gate.verifier(List.of(d), List.of())).hasSize(1);
    }

    @Test
    void uneDependanceAUnEvenementDansLeMauvaisSensBloque() {
        var d = new Dependance("miseenrelation", "org.skoa.miseenrelation.Demande", "rencontre",
                "org.skoa.rencontre.evenements.DemandeAcceptee");
        assertThat(gate.verifier(List.of(d), List.of())).hasSize(1);
    }

    @Test
    void unRecordQuiSuitLUnionDesPayloadsPasse() {
        var t = new TypeEvenement("miseenrelation", DEMANDE_ACCEPTEE, true, List.of("demandeId", "preneurId", "structureId"));
        assertThat(gate.verifier(List.of(), List.of(t))).isEmpty();
    }

    @Test
    void unRecordQuiNeSuitPasSonPayloadBloque() {
        var t = new TypeEvenement("miseenrelation", DEMANDE_ACCEPTEE, true, List.of("demandeId", "adresse"));
        assertThat(gate.verifier(List.of(), List.of(t))).singleElement().asString()
                .contains("manquants [preneurId, structureId]", "en trop [adresse]");
    }

    @Test
    void unEvenementPublieQuiNEstPasUnRecordBloque() {
        var t = new TypeEvenement("miseenrelation", DEMANDE_ACCEPTEE, false, List.of());
        assertThat(gate.verifier(List.of(), List.of(t))).singleElement().asString().contains("doit être un record");
    }

    @Test
    void unEvenementNonDeclareDansLePaquetEvenementsBloque() {
        var t = new TypeEvenement("miseenrelation", "org.skoa.miseenrelation.evenements.VagueLancee", true, List.of());
        assertThat(gate.verifier(List.of(), List.of(t))).singleElement().asString().contains("aucun événement VagueLancee");
    }

    @Test
    void unEvenementDeclarePourUnAutreAmontBloque() {
        var t = new TypeEvenement("suivi", "org.skoa.suivi.evenements.RencontreAnnulee", true, List.of("rencontreId"));
        assertThat(gate.verifier(List.of(), List.of(t))).hasSize(1);
    }
}
