package org.skoa;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.List;

import com.tngtech.archunit.core.importer.ClassFileImporter;
import com.tngtech.archunit.lang.EvaluationResult;
import org.junit.jupiter.api.Test;
import org.skoa.exemples.architecture.exemple.HorsCouche;
import org.skoa.exemples.architecture.exemple.adaptateurs.Adaptateur;
import org.skoa.exemples.architecture.exemple.api.CodeGenere;
import org.skoa.exemples.architecture.exemple.application.ApplicationSurAdaptateur;
import org.skoa.exemples.architecture.exemple.application.ApplicationSurContrat;
import org.skoa.exemples.architecture.exemple.application.CasDUsage;
import org.skoa.exemples.architecture.exemple.divers.CoucheInconnue;
import org.skoa.exemples.architecture.exemple.domaine.DomaineSurAdaptateur;
import org.skoa.exemples.architecture.exemple.domaine.DomaineSurSpring;
import org.skoa.exemples.architecture.exemple.domaine.Entite;
import org.skoa.exemples.architecture.exemple.evenements.EvenementSurDomaine;
import org.skoa.exemples.architecture.exemple.evenements.FaitPublie;

/** Prouve que chaque règle d'{@link ArchitectureHexagonale} échoue, sur le faux BC de {@code org.skoa.exemples.architecture}. */
class ArchitectureHexagonaleTest {

    private static final String RACINE = "org.skoa.exemples.architecture";

    @Test
    void unBcBienRangePasse() throws ClassNotFoundException {
        assertThat(violations(Entite.class, CasDUsage.class, Adaptateur.class, CodeGenere.class, FaitPublie.class,
                Class.forName(RACINE + ".exemple.evenements.package-info"))).isEmpty();
    }

    @Test
    void unDomaineQuiDependDeSpringBloque() {
        assertThat(violations(DomaineSurSpring.class)).singleElement().asString()
                .contains("DomaineSurSpring", "ApplicationEventPublisher");
    }

    @Test
    void unDomaineQuiDependDUnAdaptateurBloque() {
        assertThat(violations(DomaineSurAdaptateur.class)).singleElement().asString()
                .contains("DomaineSurAdaptateur", "Adaptateur");
    }

    @Test
    void uneApplicationQuiDependDUnAdaptateurBloque() {
        assertThat(violations(ApplicationSurAdaptateur.class)).singleElement().asString()
                .contains("ApplicationSurAdaptateur", "Adaptateur");
    }

    @Test
    void uneApplicationQuiDependDuContratGenereBloque() {
        assertThat(violations(ApplicationSurContrat.class)).singleElement().asString()
                .contains("ApplicationSurContrat", "CodeGenere");
    }

    @Test
    void unEvenementPublieQuiExposeLeDomaineBloque() {
        assertThat(violations(EvenementSurDomaine.class)).singleElement().asString()
                .contains("EvenementSurDomaine", "Entite");
    }

    @Test
    void uneClasseALaRacineDuBcBloque() {
        assertThat(violations(HorsCouche.class)).singleElement().asString().contains("HorsCouche");
    }

    @Test
    void uneClasseDansUneCoucheInconnueBloque() {
        assertThat(violations(CoucheInconnue.class)).singleElement().asString().contains("CoucheInconnue");
    }

    /** Une ligne par règle enfreinte, avec le détail de ses violations. */
    private static List<String> violations(Class<?>... exemples) {
        var classes = new ClassFileImporter().importClasses(exemples);
        return ArchitectureHexagonale.regles(RACINE).stream()
                .map(regle -> regle.evaluate(classes))
                .filter(EvaluationResult::hasViolation)
                .map(resultat -> resultat.getFailureReport().toString())
                .toList();
    }
}
