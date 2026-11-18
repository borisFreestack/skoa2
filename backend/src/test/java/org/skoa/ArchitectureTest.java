package org.skoa;

import com.tngtech.archunit.core.domain.JavaClasses;
import com.tngtech.archunit.core.importer.ClassFileImporter;
import com.tngtech.archunit.core.importer.ImportOption;
import org.junit.jupiter.api.DynamicTest;
import org.junit.jupiter.api.TestFactory;

import java.util.stream.Stream;

/** Gate « frontières de BC », volet hexagonal : les règles d'{@link ArchitectureHexagonale} appliquées au code réel. */
class ArchitectureTest {

    private final JavaClasses code = new ClassFileImporter()
            .withImportOption(ImportOption.Predefined.DO_NOT_INCLUDE_TESTS)
            .importPackages("org.skoa");

    @TestFactory
    Stream<DynamicTest> chaqueBoundedContextRespecteLArchitectureHexagonale() {
        return ArchitectureHexagonale.regles("org.skoa").stream()
                .map(regle -> DynamicTest.dynamicTest(regle.getDescription(), () -> regle.check(code)));
    }
}
