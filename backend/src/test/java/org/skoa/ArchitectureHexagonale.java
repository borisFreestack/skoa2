package org.skoa;

import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.classes;
import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noClasses;

import java.util.List;

import com.tngtech.archunit.lang.ArchRule;

/**
 * Règles hexagonales de chaque bounded context, sous {@code <racine>.<bc>} :
 * <ul>
 *   <li>{@code domaine} : agrégats, value objects, règles métier, ports. Ne dépend que du JDK et des événements du BC ;</li>
 *   <li>{@code application} : cas d'usage, orchestre le domaine. Peut dépendre de Spring, jamais des adaptateurs ;</li>
 *   <li>{@code adaptateurs} : web, persistance, messagerie. Seule couche qui touche au code généré des contrats ;</li>
 *   <li>{@code evenements} : événements publiés (gates/README.md), records du JDK seul ;</li>
 *   <li>{@code api} : code généré depuis {@code contracts/}, jamais écrit à la main.</li>
 * </ul>
 * La racine est un paramètre pour que {@code ArchitectureHexagonaleTest} prouve chaque règle sur des exemples fautifs.
 */
final class ArchitectureHexagonale {

    private ArchitectureHexagonale() {
    }

    static List<ArchRule> regles(String racine) {
        String bc = racine + ".*";
        String domaine = bc + ".domaine..";
        String application = bc + ".application..";
        String adaptateurs = bc + ".adaptateurs..";
        String evenements = bc + ".evenements..";
        String api = bc + ".api..";

        return List.of(
                classes().that().resideInAPackage(domaine)
                        .should().onlyDependOnClassesThat().resideInAnyPackage("java..", "", domaine, evenements)
                        .because("le domaine ne dépend ni de Spring, ni d'une bibliothèque, ni des autres couches")
                        .allowEmptyShould(true),

                noClasses().that().resideInAPackage(application)
                        .should().dependOnClassesThat().resideInAnyPackage(adaptateurs, api)
                        .because("l'application parle aux adaptateurs par les ports du domaine, et ignore les contrats générés")
                        .allowEmptyShould(true),

                classes().that().resideInAPackage(evenements).and().doNotHaveSimpleName("package-info")
                        .should().onlyDependOnClassesThat().resideInAnyPackage("java..", "", evenements)
                        .because("un événement publié est un record lisible par tout BC aval, sans dépendance")
                        .allowEmptyShould(true),

                classes().that().resideInAPackage(bc + "..").and().doNotHaveSimpleName("package-info")
                        .should().resideInAnyPackage(domaine, application, adaptateurs, evenements, api)
                        .because("le code d'un BC est rangé dans une couche connue, sinon il échappe à ces règles et à PIT")
                        .allowEmptyShould(true));
    }
}
