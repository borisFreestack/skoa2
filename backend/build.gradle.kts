plugins {
    java
    id("org.springframework.boot") version "4.1.2"
    id("io.spring.dependency-management") version "1.1.7"
    id("org.openapi.generator") version "7.27.0"
    id("info.solidsoft.pitest") version "1.19.0"
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
    // Gate « conformité à la context map » (ContextMapTest) : relancée quand la context map change.
    val racine = rootProject.layout.projectDirectory
    inputs.file(racine.file("contexts/context-map.yaml")).withPropertyName("contextMap")
    systemProperty("skoa.racine", racine.asFile.absolutePath)
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

// Gate « qualité réelle des tests » : PIT modifie le code (mutants) et exige qu'un test échoue.
// On mute ce qui porte les règles métier, le domaine et l'application, avec les seuls tests des BC.
// ArchitectureTest impose que tout le code d'un BC soit rangé dans une couche connue : rien n'y échappe.
pitest {
    pitestVersion = "1.30.1"
    junit5PluginVersion = "1.2.3"
    targetClasses = listOf("org.skoa.*.domaine.*", "org.skoa.*.application.*")
    targetTests = contrats.values.map { "org.skoa.$it.*" }
    mutationThreshold = 80
    // Tant qu'aucun BC n'a de code métier, il n'y a rien à muter : ce n'est pas un échec.
    failWhenNoMutations = false
    timestampedReports = false
    outputFormats = listOf("HTML", "XML")
}

tasks.check {
    dependsOn(tasks.pitest)
}
