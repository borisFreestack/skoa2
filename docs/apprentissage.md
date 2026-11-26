# Apprentissage — technique et pratiques dans skoa

Ce fichier sert l'objectif 3 de l'ADR-002 : se remettre à niveau sur Java, Spring et Angular, et apprendre DDD et TDD sur le code de skoa. Le journal (`docs/journal-sdlc.md`) raconte la chaîne ; ce fichier explique la technique et les pratiques.

Une fiche par concept :
- **Quoi** : le concept en une ou deux phrases ;
- **Dans skoa** : où le voir (fichier, classe, test) ;
- **Piège** : l'erreur classique ;
- **Nouveau** : pour la pile technique, ce qui a changé ces dernières années.

Le statut indique si le concept est **en place** dans le code ou **à venir**. Une fiche est ajoutée ou complétée dans la PR qui met le concept en place. Un détail de version qui n'a pas été vérifié dans le dépôt est signalé « à vérifier ».

## Sommaire

1. [DDD stratégique](#1-ddd-stratégique) : bounded context, ubiquitous language, context map
2. [DDD tactique](#2-ddd-tactique) : agrégat, invariant, événement de domaine, value object, architecture hexagonale
3. [TDD et qualité des tests](#3-tdd-et-qualité-des-tests)
4. [Java moderne](#4-java-moderne)
5. [Spring Boot 4 et Spring Modulith](#5-spring-boot-4-et-spring-modulith)
6. [Angular moderne](#6-angular-moderne)
7. [Outillage et contrats](#7-outillage-et-contrats)
8. [Pour vérifier que c'est acquis](#8-pour-vérifier-que-cest-acquis)

---

## 1. DDD stratégique

Le DDD stratégique découpe le domaine et fixe le langage, avant toute ligne de code. C'est ce qu'a produit la session S0.

### Bounded context (BC) — en place

- **Quoi** : une frontière à l'intérieur de laquelle chaque mot a un seul sens et un seul modèle. Deux BC peuvent employer le même mot avec deux sens différents ; c'est même le signe qu'il faut une frontière.
- **Dans skoa** : `mise-en-relation`, `rencontre` et `suivi`, décrits dans `contexts/<bc>/CONTEXT.md`. `Demandeur` existe dans `mise-en-relation` (rattaché à l'agrégat `Demande`) et dans `rencontre` (rattaché à `Rencontre`).
- **Piège** : découper par couche technique (front, back, base) ou par entité (« le module Adherent »). Un BC se découpe par langage et par règles métier.

### Ubiquitous language — en place

- **Quoi** : le même vocabulaire, celui du métier, dans les conversations, les specs, le code et les tests.
- **Dans skoa** : `contexts/<bc>/glossary.yaml`, où chaque terme a sa définition et ses synonymes refusés (`forbidden`). La gate `langage` (`gates/skoa_gates/langage.py`) les impose dans le code et les contrats. Le code est en français pour ne garder qu'une langue.
- **Piège** : traduire en anglais dans le code (« Request » pour Demande). Le glossaire et le code divergent alors en silence, et on finit par traduire mentalement à chaque lecture.

### Context map et ses patterns — en place

- **Quoi** : la carte des relations entre BC : qui fournit, qui consomme, et comment chacun se protège de l'autre.
- **Dans skoa** : `contexts/context-map.yaml`, vérifiée par la gate `ContextMapTest`.

| Pattern | Sens | Dans skoa |
|---|---|---|
| Customer-supplier | l'amont fournit ce dont l'aval a besoin, et ils négocient le contrat | `mise-en-relation` → `rencontre` (`DemandeAcceptee`) |
| Open-host service | l'amont publie un contrat stable et ouvert à tous | `mise-en-relation` et `rencontre` vers `suivi` |
| Conformist | l'aval prend le modèle de l'amont tel quel, sans le traduire | `suivi` |
| Anticorruption layer (ACL) | l'aval traduit le modèle externe dans le sien pour ne pas être contaminé | chaque BC traduit l'identité fournie par `identite` |
| Published language | un format d'échange documenté, distinct du modèle interne | les payloads d'événements de la context map |

- **Piège** : une relation bidirectionnelle entre deux BC cœur. Ici, `mise-en-relation` et `rencontre` dépendent l'un de l'autre (`DemandeAcceptee` dans un sens, `DesistementSignale` dans l'autre) : c'est un couplage à surveiller, noté dans l'ADR-001.

### Cœur, support, générique — en place

- **Quoi** : un BC **cœur** fait la différence du produit et mérite le meilleur soin ; un BC de **support** est nécessaire mais banal ; un BC **générique** s'achète ou se délègue.
- **Dans skoa** : `mise-en-relation` et `rencontre` sont cœur, `suivi` est support, l'identité est générique et confiée à une application séparée (ADR-005).
- **Piège** : mettre le même effort partout. Le mutation testing, par exemple, compte surtout pour `mise-en-relation`.

---

## 2. DDD tactique

Le DDD tactique, ce sont les briques du modèle dans le code. Il commence avec la fonctionnalité de bout en bout de S1.

### Agrégat — en place

- **Quoi** : un groupe d'objets qu'on modifie d'un seul bloc, dans une transaction, et qui garantit ses propres règles. On n'y accède que par sa racine, et un agrégat ne référence un autre agrégat que par son identifiant.
- **Dans skoa** : les champs `aggregate` du glossaire, par exemple `Demande`, `Abonnement`, `Rencontre` ou `ElementATraiter`. La gate `invariants` exige les tests d'un agrégat dès que sa classe existe.
- **Premier dans le code** : `backend/src/main/java/org/skoa/suivi/domaine/Adhesion.java`. Champs `final`, sans setter : un changement d'état passera par une méthode au nom métier (`terminer`), qui pourra garder ses règles.
- **Taille** : on regroupe ce qu'une règle oblige à modifier ensemble, pas ce qui « appartient à ». `Adhesion` est séparée de `Structure` parce qu'aucune règle ne lie les adhésions de deux personnes (ADR-004).
- **Piège** : l'agrégat géant qui charge tout, ou un objet qui tient une référence directe vers un autre agrégat (`demande.getRencontre()`). Les deux rendent les transactions lourdes et les règles floues.

### Invariant — en place

- **Quoi** : une règle qui doit être vraie après chaque transaction de l'agrégat. C'est l'agrégat qui la garantit, pas le contrôleur ni le service.
- **Dans skoa** : `contexts/<bc>/invariants.yaml`. Le champ `exemple_violation` est déjà un cas de test tout écrit. Exemple : INV-MER-005, « un Adherent n'est jamais sollicité pour sa propre Demande ».
- **Piège** : vérifier la règle dans un service applicatif. Le jour où un deuxième chemin modifie l'agrégat, la règle saute.
- **Invariant d'ensemble** : une règle qui porte sur plusieurs instances, comme une unicité, dépasse l'agrégat. INV-SUI-008 (« au plus une Adhesion en cours par Adherent dans une même Structure ») ne peut pas être vu par une Adhesion seule. Le domaine l'exprime en interrogeant un port (`Adhesions.aUneAdhesionEnCours`) ; la base le garantira face aux enregistrements simultanés, par une contrainte d'unicité. Test : `AdhesionTest`, « INV-SUI-008 … ».

### Fabrique — en place

- **Quoi** : une méthode statique qui crée l'agrégat, nommée dans la langue du domaine, et qui peut refuser de créer. Le constructeur est `private` : c'est le seul chemin de création, donc la règle ne peut pas être contournée.
- **Dans skoa** : `Adhesion.enregistrer(adhesionId, adherentId, structureId, enregistreeLe, adhesions)`. Ce qui est arbitraire ou dépend du moment (l'identifiant, la date) vient de l'extérieur : le domaine reste déterministe et le test peut tout vérifier.
- **Piège** : sauvegarder dans la fabrique. Créer et sauvegarder sont deux responsabilités ; la sauvegarde appartient au cas d'usage, dans sa transaction.

### Événement de domaine — défini, code à venir

- **Quoi** : un fait passé et significatif pour le métier, nommé au participe (`DemandeAcceptee`). Un événement **publié** est un contrat entre BC ; un événement **interne** reste dans le BC.
- **Dans skoa** : les événements publiés sont dans `contexts/context-map.yaml`. Les événements internes sont listés dans `CONTEXT.md` (`VagueLancee`, `RencontreOuverte`). Dans le code, un événement publié est un record de `org.skoa.<bc>.evenements` (`gates/README.md`).
- **Piège** : l'ordre déguisé en événement (« EnvoyerSollicitation »). Un événement constate, il ne commande pas : c'est le consommateur qui décide quoi en faire.

### Value object — à venir

- **Quoi** : un objet sans identité, défini par ses valeurs, et immuable. Deux `Creneau` identiques sont interchangeables.
- **Dans skoa** : les candidats sont `Creneau`, `LieuDeRencontre`, `Rayon` et `Ressenti`. Un record Java est la forme naturelle d'un value object.
- **Piège** : passer des `String` et des `int` partout (« primitive obsession »). La validation se disperse, et rien n'empêche de passer un rayon à la place d'un plafond.

### Architecture hexagonale (ports et adaptateurs) — en place

- **Quoi** : le domaine est au centre et ne connaît aucune technique. Il déclare des **ports** (des interfaces : « enregistrer une Demande », « trouver les Abonnements proches ») ; des **adaptateurs** les implémentent avec Spring, une base ou HTTP. Les dépendances pointent toujours vers le domaine, jamais l'inverse.
- **Dans skoa** : chaque BC range son code en cinq paquets, `domaine`, `application`, `adaptateurs`, `evenements` et `api` (le code généré depuis `contracts/`). Les règles sont dans `backend/src/test/java/org/skoa/ArchitectureHexagonale.java` et décrites dans `gates/README.md`.
- **Premier port** : `Adhesions`, une interface de `suivi/domaine` à une seule méthode, celle dont la règle a besoin. Le domaine possède son port et le nomme dans sa langue (inversion de dépendance) ; l'implémentation vit dans les tests (le fake) et, plus tard, dans `adaptateurs`.
- **Piège** : une annotation Spring ou JPA « juste pour ce champ » dans le domaine. Le domaine ne se teste plus sans démarrer Spring, et chaque changement d'infrastructure touche les règles métier.

---

## 3. TDD et qualité des tests

### Rouge, vert, refactor — en place

- **Quoi** : on écrit un test qui échoue (rouge), puis le minimum de code pour le faire passer (vert), puis on nettoie sans changer le comportement (refactor). Le test guide le design au lieu de constater après coup.
- **Dans skoa** : le cadrage prévoit un agent tests qui écrit des tests qui doivent échouer, avant l'agent code. La gate « tests rejoués sur la branche de base » (`gates/tests_rejoues.py`) le prouve après coup : elle rejoue chaque nouveau test d'un BC sur la branche de base, sans le code de la PR, et bloque s'il y passe déjà.
- **Deux sortes de rouge** : le test ne compile pas, parce que la classe ou la méthode n'existe pas encore ; ou le test compile et son assertion échoue, parce que le comportement est absent ou faux. Les deux comptent. Le second est le plus probant : il montre que le test distingue l'ancien comportement du nouveau.
- **Piège** : écrire le test après le code et le faire passer du premier coup. Un test qu'on n'a jamais vu échouer ne prouve rien.
- **Vu sur `Adhesion`** : une fabrique qui renvoie `null` donne un rouge par assertion dès le premier test. Le refactor (vérifier avant de créer, message de l'exception) s'est fait tests verts, et ils le sont restés.
- **Triangulation** : écrire d'abord le code le plus naïf, puis un test qui le contredit, plutôt que de généraliser d'avance. Sur `Adhesion`, les tests prévus pour trianguler (autre Structure, autre personne) n'auraient pas pu rougir : c'est le fake qui filtrait. Ils ont été reportés aux tests de l'adaptateur.

### Voir rougir — en place pour les gates

- **Quoi** : avant de faire confiance à un test ou à une gate, on la voit échouer sur un cas fautif.
- **Dans skoa** : `gates/tests/` et `ConformiteContextMapTest.java` prouvent que chaque gate bloque. La PR #2 a fait échouer « Fichiers protégés » sur GitHub, puis l'a fait passer, puis échouer de nouveau. Les gates n'ont pas été écrites en TDD strict (le code avant les tests), mais ce sont leurs tests qui ont trouvé les défauts des pluriels et des alias.
- **Piège** : se rassurer avec une gate verte qui n'a jamais rien eu à bloquer.

### Tests rejoués sur la branche de base (fail-to-pass) — en place

- **Quoi** : on rejoue chaque nouveau test sans le code qu'il accompagne ; il doit échouer. C'est l'automatisation d'une vieille question de revue : « as-tu vérifié que ton test échoue sans ta correction ? ». À la main, on annule la correction, on lance le test (rouge attendu), puis on remet la correction (vert).
- **D'où ça vient** : ce n'est pas une méthode établie sous un nom précis. Le benchmark SWE-bench, qui évalue les agents de code sur de vrais bugs GitHub, la formalise. Il range les tests en **FAIL_TO_PASS** (rouges avant la correction, verts après : ils prouvent qu'elle fait quelque chose) et en **PASS_TO_PASS** (verts avant et après : ils prouvent qu'on n'a rien cassé). Un nouveau test vert avant et vert après ne prouve rien de la correction.
- **Dans skoa** : `gates/tests_rejoues.py` et le job « Tests rejoués sur la branche de base ». La règle 6 de `CLAUDE.md` en tire la conduite d'un agent : un refactoring n'ajoute pas de test, et un test qui manque sur un comportement existant passe par une PR à part.
- **Parenté avec PIT** : les deux posent la question « si le code était différent, le test le verrait-il ? ». PIT change des détails (un `>=` devient `>`) ; les tests rejoués retirent toute la PR. Ils forment comme un seul mutant, énorme : « la PR n'existe pas ».
- **Ce que ça prouve** : le test aurait pu échouer, il distingue le code d'avant de celui d'après. Ça ne prouve ni qu'il a été écrit en premier, ni qu'il vérifie bien (un test qui ne compile pas sans la nouvelle classe compte comme rouge, même s'il n'affirme rien). PIT rattrape ce second cas.
- **Piège** : ajouter un test pendant un refactoring « pour être sûr ». Il passe sur la base, et la gate le bloque à juste titre : il ne prouve rien du refactoring.

### Tester le comportement aux ports — à venir

- **Quoi** : on teste ce que le BC fait, par ses entrées et sorties (commandes, événements, API), pas la façon dont il le fait. Les tests survivent alors aux refactorings.
- **Dans skoa** : l'agent tests du cadrage voit « les ports du BC », pas l'implémentation.
- **Piège** : mocker chaque collaborateur interne. Le moindre refactoring casse des dizaines de tests qui ne protégeaient rien.

### Fake plutôt que mock — en place

- **Quoi** : un fake est une vraie implémentation d'un port, simplifiée (une liste en mémoire). Il a un comportement, là où un mock vérifie des appels. Le test juge alors ce que la règle produit, pas comment elle interroge le port.
- **Dans skoa** : `backend/src/test/java/org/skoa/suivi/domaine/AdhesionsEnMemoire.java`, dans `test` et jamais dans `main`. Sa méthode `ajouter` n'existe que sur lui : le port n'a que la méthode dont le domaine a besoin.
- **Arrange, act, assert** : le test prépare l'état par le fake (`ajouter`), appelle une seule fois le code testé (`Adhesion.enregistrer`), puis vérifie.
- **Piège, vécu** : mettre la règle dans le fake. Le test était vert, mais l'exception venait de `AdhesionsEnMemoire.ajouter` : le domaine ne vérifiait rien. Pour le repérer, se demander quelle ligne fait échouer le test ; si ce n'est pas un appel au code de production, le test ne le juge pas. PIT l'aurait vu aussi : il ne mute que `main`.

### Mutation testing (PIT) — en place

- **Quoi** : l'outil modifie le code (un `>` devient `>=`, un `return true` devient `return false`) et vérifie qu'au moins un test échoue. Un mutant qui survit révèle un test complaisant.
- **Dans skoa** : le bloc `pitest` de `backend/build.gradle.kts`. PIT mute les paquets `domaine` et `application` de chaque BC, avec les seuls tests des BC, et fait échouer `./gradlew build` sous 80 % de mutants tués. Le rapport est dans `backend/build/reports/pitest/`. C'est la parade du cadrage contre un agent qui écrirait des tests qui ne vérifient rien.
- **Exemple vu** : `return km <= rayon` testé par le seul cas `(1, 5)` donne 33 %. Le mutant `<` survit, car 1 < 5 reste vrai. Il faut tester la limite `(5, 5)` et le cas `(6, 5)` pour atteindre 100 %.
- **Premier code métier** : sur `Adhesion`, 6 mutants, 6 tués. Les accesseurs qui renvoient `null` sont tués par les assertions du test 1, l'`if` inversé par le test 2.
- **Piège** : viser 100 %. Certains mutants sont équivalents (ils ne changent rien d'observable) ; le score sert à repérer les zones faibles, pas à être maximisé.

---

## 4. Java moderne

Le projet est en Java 21, la version LTS sortie en septembre 2023.

### Records — en place

- **Quoi** : `record DemandeAcceptee(String demandeId, ...) {}` déclare une classe immuable, avec constructeur, accesseurs (`demandeId()`, sans `get`), `equals`, `hashCode` et `toString`.
- **Dans skoa** : les records imbriqués de `ConformiteContextMap.java`. Ce seront aussi les événements publiés et les value objects.
- **Hors des records** : le style d'accesseur sans `get` (`adherentId()`) se répand aussi dans les classes ordinaires, comme `Adhesion`, qui ne peut pas être un record puisqu'elle aura une date de fin.
- **Piège** : un record est immuable en surface seulement : un composant `List` reste modifiable. Il faut le copier (`List.copyOf`) dans le constructeur compact.
- **Nouveau** : stable depuis Java 16.

### Pattern matching — en place

- **Quoi** : `if (aval instanceof List<?> liste)` teste et déclare la variable en une fois, sans cast. Le `switch` sait aussi filtrer par type et déstructurer un record (`case Ouverte o ->`).
- **Dans skoa** : `ConformiteContextMap.lire`.
- **Nouveau** : `instanceof` depuis Java 16, patterns dans `switch` et patterns de record depuis Java 21.

### Sealed types — à venir

- **Quoi** : `sealed interface Statut permits Ouverte, Convenue, Annulee` fixe la liste des sous-types. Combiné au `switch`, le compilateur vérifie qu'aucun cas n'est oublié.
- **Dans skoa** : candidats naturels, les statuts de `Rencontre` et le `Motif` d'un `ElementATraiter`.
- **Nouveau** : depuis Java 17.

### Text blocks, `var`, collections immuables — en place

- **Quoi** : `"""…"""` pour les chaînes multilignes, `var` pour l'inférence de type locale, `List.of` et `toList()` pour des collections immuables.
- **Dans skoa** : `stream().toList()` dans `ContextMapTest.java`.
- **Piège** : `Stream.toList()` rend une liste immuable, contrairement à `collect(Collectors.toList())`. Le code qui la modifiait ensuite casse.

### Threads virtuels — à venir, à décider

- **Quoi** : des threads très légers gérés par la JVM, qui rendent abordable le style bloquant à forte concurrence. Spring Boot les active avec `spring.threads.virtual.enabled=true`.
- **Dans skoa** : pas encore utilisés. Il n'y a aucun besoin de charge pour l'instant.

---

## 5. Spring Boot 4 et Spring Modulith

### Spring Boot 4 — en place

- **Quoi** : la version majeure de fin 2025, sur Spring Framework 7.
- **Dans skoa** : `backend/build.gradle.kts` (Spring Boot 4.1.2).
- **Nouveau** :
  - socle Jakarta EE 11 (les paquets `javax.*` ont disparu dès Boot 3) ;
  - starters plus fins : `spring-boot-starter-webmvc` plutôt que `spring-boot-starter-web` ;
  - annotations de nullité JSpecify dans le framework ;
  - générateur OpenAPI configuré avec `useSpringBoot4`.
  - À vérifier au cas par cas : les détails des versions 4.x mineures.
- **Piège** : reprendre un tutoriel Spring Boot 2 tel quel. Les noms de starters, les paquets et une partie de la configuration ont changé.

### Spring Modulith — en place

- **Quoi** : un monolithe découpé en modules vérifiés. Chaque sous-paquet direct de `org.skoa` est un module ; ce qu'il contient est interne par défaut ; un sous-paquet n'est visible des autres que s'il est déclaré `@NamedInterface`.
- **Dans skoa** :
  - `backend/src/main/java/org/skoa/<bc>/package-info.java` déclare un module par BC ;
  - `ModulesTest` appelle `ApplicationModules.verify()`, qui fait échouer le build en cas de dépendance interdite ;
  - `ContextMapTest` utilise la même analyse pour comparer les dépendances réelles à la context map.
- **Cycles** : `verify()` refuse aussi les cycles. Un événement évite l'appel direct, mais celui qui écoute importe la classe de l'événement : deux BC qui s'écoutent forment un cycle (ADR-004).
- **Piège** : croire qu'un module est isolé parce qu'il est dans un paquet à part. Sans `verify()` en test, rien ne l'empêche d'importer l'interne d'un autre.

### Événements entre modules — à venir

- **Quoi** : un module publie avec `ApplicationEventPublisher`, et un autre écoute avec `@ApplicationModuleListener`. Celui-ci s'exécute après la transaction de l'émetteur, de façon asynchrone. Le registre de publication des événements stocke chaque événement jusqu'à son traitement, comme un outbox.
- **Dans skoa** : c'est le chemin prévu pour tous les événements de la context map.
- **Piège** : un `@EventListener` classique s'exécute dans la transaction de l'émetteur. Si l'écouteur échoue, il annule l'action de l'émetteur, ce qui recrée le couplage qu'on voulait éviter.

### OAuth avec Spring Security — à venir

- **Quoi** : le serveur d'autorisation émet les jetons, le serveur de ressources les vérifie. Avec le flux *authorization code*, PKCE prouve que celui qui échange le code est celui qui a démarré la connexion ; un front ne peut pas garder de secret. Avec *client credentials*, une application s'identifie elle-même, sans personne connectée.
- **Dans skoa** : `identite` sera le serveur d'autorisation, le backend le serveur de ressources (ADR-005).
- **Piège** : mettre dans le jeton des faits métier, comme l'Adhesion ou le rôle de Referent. Le jeton reste valable après que le fait a changé.

---

## 6. Angular moderne

Le front est en Angular 22.

### Composants standalone — en place

- **Quoi** : plus de `NgModule`. Chaque composant déclare lui-même ce qu'il utilise dans `imports`.
- **Dans skoa** : `frontend/src/app/app.ts` (`imports: [RouterOutlet]`).
- **Nouveau** : standalone par défaut depuis Angular 19, il n'y a plus besoin d'écrire `standalone: true`.

### Signals et fonctionnement sans zone (zoneless) — en place

- **Quoi** : un signal (`signal('skoa')`) est une valeur réactive. Angular sait exactement quoi rafraîchir quand il change, sans zone.js pour intercepter chaque événement du navigateur. `computed()` dérive une valeur, et `effect()` réagit à un changement.
- **Dans skoa** : `title = signal('skoa')` dans `app.ts`. Le front n'a pas de dépendance zone.js, il est donc zoneless.
- **Piège** : muter un objet contenu dans un signal (`liste().push(x)`). Le signal ne voit rien : il faut `set` ou `update` avec une nouvelle valeur.

### Nouveau guide de style, nouveau build, Vitest — en place

- **Quoi** :
  - fichiers nommés sans suffixe (`app.ts` plutôt que `app.component.ts`) ;
  - build esbuild et Vite (`@angular/build:application`) au lieu de webpack ;
  - tests unitaires avec Vitest (`@angular/build:unit-test`) au lieu de Karma et Jasmine.
- **Dans skoa** : `frontend/angular.json`, `frontend/src/app/app.spec.ts`.
- **Piège** : chercher `karma.conf.js` ou `test.ts`. Ils n'existent plus.

### Sheriff — en place

- **Quoi** : des frontières de modules dans le front, vérifiées par ESLint. C'est l'équivalent de Spring Modulith côté Angular.
- **Dans skoa** : `frontend/sheriff.config.ts` déclare un module par BC (`src/app/<bc>`) et interdit les dépendances entre BC ; seul le shell les compose. Chaque BC expose son API publique dans `index.ts`.
- **Piège** : importer un fichier profond d'un autre BC « juste pour un type ». C'est exactement ce que Sheriff refuse.

---

## 7. Outillage et contrats

### Toolchain Gradle — en place

- **Quoi** : le build déclare la version de Java dont il a besoin, et Gradle trouve ou télécharge le JDK correspondant, quel que soit le Java par défaut du poste.
- **Dans skoa** : `java { toolchain { languageVersion = JavaLanguageVersion.of(21) } }` dans `backend/build.gradle.kts`. Le poste a Java 8 par défaut.

### ArchUnit — en place

- **Quoi** : une bibliothèque qui lit le bytecode compilé et vérifie des règles d'architecture écrites comme des tests JUnit (« les classes de `..domaine..` ne dépendent que de `java..` »).
- **Dans skoa** : `ArchitectureTest` applique les règles hexagonales au code réel, et `ArchitectureHexagonaleTest` prouve que chacune bloque sur un faux BC (`org.skoa.exemples.architecture`). Spring Modulith s'appuie aussi sur ArchUnit pour `verify()`.
- **Piège** : une règle qui ne porte sur aucune classe passe sans rien prouver. ArchUnit la refuse par défaut ; ici, `allowEmptyShould(true)` est voulu, tant que les BC sont vides, et c'est le faux BC qui prouve que les règles mordent.

### Contract-first OpenAPI — en place

- **Quoi** : on écrit d'abord le contrat de l'API, puis on génère le code qui le suit, et non l'inverse.
- **Dans skoa** : `contracts/<bc>/openapi.yaml`. Le backend génère des interfaces Spring (`interfaceOnly`) que les contrôleurs implémentent ; le front génère son client avec ng-openapi-gen. Le code généré n'est pas versionné : si le contrat change, la compilation casse. oasdiff bloque un changement cassant en PR.
- **Piège** : versionner le code généré et le retoucher à la main. Le contrat et le code divergent au premier ajustement.

---

## 8. Pour vérifier que c'est acquis

À se poser régulièrement, sans relire les fiches.

**DDD**
- Pourquoi `Demandeur` peut-il exister dans deux BC sans être un doublon ?
- Quel BC de skoa est conformist, et qu'est-ce que ça lui coûte ?
- `Creneau` est-il une entité ou un value object ? Pourquoi ?
- Où doit vivre la vérification de INV-MER-005 : contrôleur, service ou agrégat ?
- INV-SUI-008 porte sur plusieurs Adhesions : comment le domaine le garantit-il, et que ne garantit-il pas ?

**TDD**
- Qu'est-ce qu'un test écrit en TDD prouve qu'un test écrit après le code ne prouve pas ?
- Quelle différence entre une couverture de lignes de 100 % et un score de mutation de 100 % ?
- Un port du domaine est une interface : où vit-elle, et où vit son implémentation ?
- Pourquoi un test ajouté pendant un refactoring est-il bloqué par la gate des tests rejoués, et où doit-il aller ?
- Un test est vert : comment savoir s'il juge le domaine ou le fake ?

**Java, Spring, Angular**
- Que vérifie `ApplicationModules.verify()`, et que ne vérifie-t-il pas ?
- Pourquoi un écouteur `@ApplicationModuleListener` plutôt qu'un `@EventListener` entre deux BC ?
- Dans un front zoneless, pourquoi `liste().push(x)` ne rafraîchit-il pas l'écran ?
