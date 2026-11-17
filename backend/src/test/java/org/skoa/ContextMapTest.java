package org.skoa;

import static org.assertj.core.api.Assertions.assertThat;

import java.lang.reflect.RecordComponent;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.List;

import com.tngtech.archunit.core.domain.JavaClass;
import com.tngtech.archunit.core.importer.ClassFileImporter;
import com.tngtech.archunit.core.importer.ImportOption;
import org.junit.jupiter.api.Test;
import org.skoa.ConformiteContextMap.Dependance;
import org.skoa.ConformiteContextMap.TypeEvenement;
import org.springframework.modulith.core.ApplicationModules;

/** Gate « conformité à la context map » appliquée au code réel. */
class ContextMapTest {

    private final ApplicationModules modules = ApplicationModules.of(SkoaApplication.class);

    @Test
    void lesDependancesEntreBoundedContextsSontCellesDeLaContextMap() throws Exception {
        Path contextMap = Path.of(System.getProperty("skoa.racine", "..")).resolve("contexts/context-map.yaml");
        ConformiteContextMap gate = ConformiteContextMap.lire(contextMap);

        List<Dependance> dependances = modules.stream()
                .flatMap(m -> m.getDirectDependencies(modules).stream()
                        .map(d -> new Dependance(m.getIdentifier().toString(), d.getSourceType().getName(),
                                d.getTargetModule().getIdentifier().toString(), d.getTargetType().getName())))
                .toList();

        List<TypeEvenement> types = modules.stream()
                .flatMap(m -> new ClassFileImporter()
                        .withImportOption(ImportOption.Predefined.DO_NOT_INCLUDE_TESTS)
                        .importPackages(ConformiteContextMap.paquetEvenements(m.getIdentifier().toString()))
                        .stream()
                        .filter(c -> !c.isNestedClass() && !c.getSimpleName().equals("package-info"))
                        .map(c -> typeEvenement(m.getIdentifier().toString(), c)))
                .toList();

        assertThat(gate.verifier(dependances, types))
                .as("Voir contexts/context-map.yaml (CLAUDE.md, règle 5). Un nouvel événement est un changement de contrat : tâche contrat et Gate 1.")
                .isEmpty();
    }

    private static TypeEvenement typeEvenement(String module, JavaClass classe) {
        Class<?> type = classe.reflect();
        List<String> composants = type.isRecord()
                ? Arrays.stream(type.getRecordComponents()).map(RecordComponent::getName).toList()
                : List.of();
        return new TypeEvenement(module, type.getName(), type.isRecord(), composants);
    }
}
