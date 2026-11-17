package org.skoa;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;
import org.springframework.modulith.core.ApplicationModule;
import org.springframework.modulith.core.JavaPackage;
import org.springframework.modulith.core.ApplicationModules;

class ModulesTest {

    private final ApplicationModules modules = ApplicationModules.of(SkoaApplication.class);

    @Test
    void chaqueBoundedContextEstUnModule() {
        assertThat(modules.stream().map(ApplicationModule::getBasePackage).map(JavaPackage::getName))
                .containsExactlyInAnyOrder("org.skoa.miseenrelation", "org.skoa.rencontre", "org.skoa.suivi");
    }

    @Test
    void lesModulesRespectentLeursFrontieres() {
        modules.verify();
    }
}
