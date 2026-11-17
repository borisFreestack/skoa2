plugins {
    java
    id("org.springframework.boot") version "4.1.2"
    id("io.spring.dependency-management") version "1.1.7"
    id("org.openapi.generator") version "7.27.0"
}

group = "org.skoa"
version = "0.1.0-SNAPSHOT"

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(21)
    }
}

repositories {
    mavenCentral()
}

dependencyManagement {
    imports {
        mavenBom("org.springframework.modulith:spring-modulith-bom:2.1.2")
    }
}

dependencies {
    implementation("org.springframework.boot:spring-boot-starter-webmvc")
    implementation("org.springframework.boot:spring-boot-starter-validation")
    implementation("org.springframework.modulith:spring-modulith-starter-core")

    testImplementation("org.springframework.boot:spring-boot-starter-webmvc-test")
    testImplementation("org.springframework.modulith:spring-modulith-starter-test")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
}

tasks.test {
    useJUnitPlatform()
}

// Contrats HTTP : contracts/<bc>/openapi.yaml est la source de vérité.
// Les interfaces Spring et les DTO sont régénérés à chaque build et ne sont pas versionnés ;
// les contrôleurs du BC les implémentent, donc une dérive casse la compilation.
val contrats = mapOf(
    "mise-en-relation" to "miseenrelation",
    "rencontre" to "rencontre",
    "suivi" to "suivi",
)

val generationDesContrats = contrats.map { (dossier, paquet) ->
    tasks.register<org.openapitools.generator.gradle.plugin.tasks.GenerateTask>("genererContrat-$dossier") {
        group = "contrats"
        description = "Génère les interfaces Spring et les DTO du contrat $dossier."
        generatorName = "spring"
        inputSpec = rootProject.layout.projectDirectory.file("contracts/$dossier/openapi.yaml")
        outputDir = layout.buildDirectory.dir("generated/openapi/$dossier")
        apiPackage = "org.skoa.$paquet.api"
        modelPackage = "org.skoa.$paquet.api.dto"
        cleanupOutput = true
        generateApiTests = false
        generateModelTests = false
        generateApiDocumentation = false
        generateModelDocumentation = false
        configOptions = mapOf(
            "useSpringBoot4" to "true",
            "interfaceOnly" to "true",
            "skipDefaultInterface" to "true",
            "useTags" to "true",
            "useResponseEntity" to "true",
            "useBeanValidation" to "true",
            "openApiNullable" to "false",
            "annotationLibrary" to "none",
            "documentationProvider" to "none",
            "sourceFolder" to "src/main/java",
        )
    }
}

sourceSets.main {
    java {
        contrats.keys.forEach { srcDir(layout.buildDirectory.dir("generated/openapi/$it/src/main/java")) }
    }
}

tasks.compileJava {
    dependsOn(generationDesContrats)
}
