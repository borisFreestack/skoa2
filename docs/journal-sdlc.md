# Journal de la chaîne SDLC AI-native

Ce journal sert l'objectif 2 de l'ADR-002 : apprendre par la pratique ce que coûte, ce qu'impose et ce qu'apporte une chaîne de développement pilotée par des agents.
Il raconte le vécu. Les décisions qui font foi sont dans `docs/adr/`.

## Comment écrire une entrée

Une entrée par fait marquant, datée, rangée sous son sprint. Chaque entrée a cinq rubriques :

- **Fait** : ce qui s'est passé, en une ou deux phrases ;
- **Choix** : ce qui a été retenu, et les alternatives écartées ;
- **Friction** : ce qui a coincé ou surpris (« aucune » est une réponse valable) ;
- **Leçon** : ce qu'on en retient pour la chaîne ;
- **Simplification** : si la leçon dépend du contexte simplifié de l'ADR-002, dire laquelle.

On écrit au fil de l'eau. Une entrée reconstituée plus tard le signale.

---

## S0 — Modélisation (12 au 13/11/2026)

*Entrées reconstituées le 2026-11-17 à partir de l'historique Git et de `docs/synthese-s0.md`.*

### 2026-11-13 — L'event storming invalide le domaine du cadrage

- **Fait** : l'event storming a fait apparaître un autre domaine que celui du cadrage. Les BC proposés (Échange, Modération) et le vocabulaire du cadrage, refusé par le produit, ne tenaient pas.
- **Choix** : la maquette v0.2 devient la référence produit. L'ADR-001 dit ce qui prime. Le cadrage n'est pas réécrit.
- **Friction** : deux sources de vérité qui se contredisent. Un agent qui lirait le cadrage modéliserait des situations vécues, ce que le produit refuse.
- **Leçon** : le contexte d'un agent doit désigner explicitement ce qui l'emporte en cas de conflit. Un document dépassé mais présent est un risque tant que rien ne dit qu'il est dépassé. D'où la phrase de priorité en tête de `CLAUDE.md`.
- **Simplification** : aucune.

### 2026-11-13 — Les artefacts de contexte cassent dès leur écriture

- **Fait** : deux commits correctifs le jour même. Le YAML des invariants de Suivi était invalide (`fb0d474`), et Annulation et Desistement s'interdisaient mutuellement dans les glossaires (`b104f2a`).
- **Choix** : contrôles manuels en fin de S0 (chargement YAML, nombre de termes, identifiants d'invariants, cohérence des événements, termes interdits). Leur automatisation est prévue en S1.
- **Friction** : les listes `forbidden` sont une règle croisée entre glossaires. Personne ne voit le conflit en lisant un seul fichier.
- **Leçon** : confirme le risque du cadrage (« un document que rien ne contrôle dérive »). Les artefacts lus par les agents ont besoin de leurs propres gates, avant même le code. Le lint de langage doit aussi vérifier qu'un terme n'est pas à la fois défini dans un BC et interdit dans un autre, sauf si c'est voulu.
- **Simplification** : aucune.

---

## S1 — Walking skeleton + CI/CD (à partir du 17/11/2026)

*Entrées reconstituées le 2026-11-17 à partir des messages de commit.*

### 2026-11-17 — S1 réalisée avec un agent, alors qu'elle était prévue « sans agent »

- **Fait** : le backlog du cadrage prévoit une S1 « codée à la main, sans agent ». Les commits de S1 sont co-écrits par Claude Code, qui voit tout le dépôt.
- **Choix** : on continue ainsi (question O2 de l'ADR-002).
- **Friction** : l'agent de S1 n'est soumis à aucune des règles qu'il met en place. Il lit tous les BC, et aucune gate ne l'encadre encore.
- **Leçon** : construire la chaîne avec un agent non borné, c'est déjà la configuration A de l'expérience de S3, mais sans la mesurer. Il faudra s'en souvenir en lisant les résultats A/B.
- **Simplification** : un seul humain, qui est aussi celui qui pilote l'agent.

### 2026-11-17 — Gradle plutôt que Maven (Q7)

- **Fait** : le cadrage parle de `mvn verify` ; le squelette est en Gradle 9.6, avec une toolchain Java 21.
- **Choix** : Gradle est conservé (`795dfce`). La toolchain est fixée dans le build plutôt que laissée au JDK du poste, qui est en Java 8 par défaut.
- **Friction** : le cadrage et le code divergeaient sans que rien ne le signale. La question a traîné de S0 à S1.
- **Leçon** : les noms d'outils écrits dans un document (ici, une gate) deviennent faux sans prévenir. Une gate se décrit mieux par ce qu'elle bloque que par sa commande.
- **Simplification** : aucune.

### 2026-11-17 — La CI dérive toute seule

- **Fait** : deux commits d'entretien juste après la création de la CI. Les actions v4 tournaient sur Node 20, qui est déprécié (`8a167e1`). `ubuntu-latest` allait basculer vers Ubuntu 26 (`ab18d1e`).
- **Choix** : versions majeures des actions mises à jour et image fixée sur `ubuntu-24.04`.
- **Friction** : une CI peut casser sans aucun changement dans le dépôt.
- **Leçon** : une gate n'est fiable que si son environnement est figé. Pour une chaîne d'agents, c'est encore plus important : un échec dû à l'environnement renvoie l'agent itérer sur un problème qui n'est pas le sien, et lui fait consommer ses trois itérations.
- **Simplification** : aucune.

### 2026-11-17 — Les contrats HTTP comme source de vérité, et la compilation comme gate

- **Fait** : un `contracts/<bc>/openapi.yaml` par BC. Le backend (openapi-generator, interfaces Spring) et le frontend (ng-openapi-gen) régénèrent leur code à chaque build. Le code généré n'est pas versionné (`fed87a7`, `329feb9`).
- **Choix** : préférer la génération à chaque build plutôt qu'un code généré commité. En CI, oasdiff compare chaque contrat à celui de la branche de base et échoue sur un changement cassant (`5ae3125`).
- **Friction** : les contrats sont vides pour l'instant. La gate existe, mais elle n'a encore rien bloqué.
- **Leçon** : faire échouer la compilation est une gate gratuite. Un contrôleur ou un service Angular qui ne suit plus le contrat ne compile plus, sans script dédié. Une gate qui n'a jamais échoué n'est pas encore prouvée : il faudra provoquer volontairement un changement cassant pour la voir rougir.
- **Simplification** : un seul dépôt. Avec des BC dans des dépôts séparés, il faudrait publier les contrats comme artefacts versionnés.

### 2026-11-17 — Frontières de BC côté backend et côté frontend

- **Fait** : Spring Modulith avec un module par BC et un test `ApplicationModules.verify()`. Côté Angular, Sheriff (via ESLint) interdit à un BC d'importer un autre BC et refuse les imports profonds.
- **Choix** : deux outils différents pour la même règle. Chaque écosystème garde son outil natif.
- **Friction** : aucune pour l'instant, faute de code qui pourrait la violer.
- **Leçon** : la règle 1 de `CLAUDE.md` (« ne lis ni ne modifie le code d'un autre BC ») est vérifiée sur les imports, pas sur la lecture. Rien n'empêche encore un agent de lire un autre BC. Seul l'assemblage du contexte en S2 pourra le garantir.
- **Simplification** : aucune.

### 2026-11-17 — Le poste local contraint la pile

- **Fait** : `sass-embedded` embarque une VM Dart qui exige macOS 14. Sur le poste, en macOS 12, `ng build` et `ng test` échouent avec un message peu clair.
- **Choix** : le frontend est en CSS plutôt qu'en SCSS. Docker pour le front local a été écarté : il est jugé trop lourd pour un front.
- **Friction** : la CI (Ubuntu) n'aurait jamais détecté le problème. Il n'apparaît qu'en local.
- **Leçon** : une chaîne a deux environnements à tenir, la CI et le poste. Un agent qui ajoute une dépendance à binaire natif peut casser le poste sans casser la CI. Il faut vérifier la version minimale d'OS d'un binaire avant de l'adopter.
- **Simplification** : poste unique et contraint.

### 2026-11-17 — Confidentialité des outils de la chaîne

- **Fait** : oasdiff propose d'envoyer les contrats à oasdiff.com. Cet envoi est désactivé en CI.
- **Choix** : aucun contenu du dépôt ne part vers un service tiers sans décision explicite.
- **Friction** : l'option est activée par défaut dans l'outil.
- **Leçon** : chaque outil de la chaîne est un canal de sortie potentiel. Les options par défaut sont à lire, pas à supposer.
- **Simplification** : les données sont fictives. Avec des données réelles, cette vigilance deviendrait une gate.

### 2026-11-17 — Les gates DDD : quatre gates, deux langages

- **Fait** : quatre gates écrites (`gates/README.md`). Trois scripts Python : artefacts de `contexts/`, langage, couverture des invariants. Un test Java : conformité à la context map, qui analyse le bytecode avec Spring Modulith. Un job CI `gates-ddd` lance les scripts ; `./gradlew build` lance le test Java.
- **Choix** :
  - Python pour les gates de texte, plutôt que JUnit ou Node. Les rapports tiennent sur une ligne par constat, faciles à relire pour un agent, et un script peut aussi tourner en pre-commit.
  - Java pour la context map, parce que seules les dépendances compilées disent la vérité.
  - Couverture des invariants exigée par agrégat : un invariant devient exigible dès que son agrégat est écrit. Les alternatives étaient une gate non bloquante en S1, ou bloquante tout de suite, donc rouge en permanence.
  - Aucune règle recopiée : le vocabulaire interdit partout est lu dans `CLAUDE.md`, le reste dans `contexts/`.
- **Friction** :
  - Les tests des gates ont trouvé deux défauts avant leur première exécution réelle. Les pluriels passaient : « ListeClients » ne contient pas exactement « Client ». Et le nom d'origine d'un import aliasé était jugé à tort.
  - Faire rougir la gate context map sur du vrai bytecode a révélé un troisième défaut : `package-info` était pris pour un événement.
  - Le vocabulaire interdit partout n'existait qu'en prose dans `CLAUDE.md`. La gate dépend donc de la forme d'un paragraphe.
  - Des synonymes refusés (« Minimum », « Date », « Support ») sont aussi des mots-clés techniques. Il a fallu ne juger que les noms qu'on choisit : pas les mots-clés OpenAPI, pas les noms importés d'une bibliothèque.
- **Leçon** :
  - Une gate se teste comme du code, et on ne la croit qu'après l'avoir vue rougir. Les tests unitaires des gates sont une étape du job CI, avant les gates elles-mêmes.
  - Une gate sur le langage n'attrape que les mots qu'on lui a dit d'interdire. Un terme métier inventé mais neutre passe : la règle 3 de `CLAUDE.md` reste l'affaire de la review.
  - Les conventions que les gates imposent (paquet `evenements`, citation d'un invariant dans le nom d'un test) ne sont écrites que dans `gates/README.md`. Un agent qui ne les connaît pas les découvrira en échouant, et chaque échec lui coûte une de ses trois itérations.
- **Simplification** : un seul dépôt et un monolithe modulaire. Avec des services séparés, la conformité à la context map ne pourrait plus s'appuyer sur le bytecode : il faudrait vérifier les schémas d'événements publiés.

### 2026-11-17 — Le payload d'un événement partagé est une union

- **Fait** : la context map déclare `DemandeAcceptee` deux fois. Vers `rencontre`, le payload contient le lieu et le créneau ; vers `suivi`, il ne les contient pas. Or, dans le monolithe, un événement est un seul record.
- **Choix** : la gate exige que le record porte l'union des deux payloads.
- **Friction** : `suivi` recevra donc `lieuDeRencontre` et `creneau`, que la context map ne lui destine pas. Si cette différence de payload était voulue (pour ne pas exposer de lieu au Suivi), le code ne peut pas la respecter.
- **Leçon** : une context map écrite avant le code peut déclarer des choses que l'architecture choisie ne sait pas garantir. À trancher par une tâche contrat : soit deux événements distincts, soit un payload unique assumé.
- **Simplification** : un seul processus. Avec un broker, on pourrait projeter un payload par consommateur.

---

## Reste à faire en S1 (au 17/11/2026)

D'après le backlog du cadrage :

- [ ] fonctionnalité de bout en bout : s'abonner à un service et recevoir une Sollicitation pour une Demande proche ;
- [x] scripts de gates DDD : conformité à la context map, lint de langage (avec la vérification croisée des `forbidden`), couverture des invariants ;
- [ ] PIT (mutation testing), ArchUnit ;
- [ ] tests rejoués sur la branche de base, fichiers protégés ;
- [ ] images (Jib, Docker), preview Helm sur k3d, e2e Playwright, déploiement et rollback.

## Questions de chaîne à garder en tête

- Comment voir rougir chaque gate au moins une fois, pour prouver qu'elle bloque vraiment ?
- Où s'arrête la règle 1 : sur les imports (vérifiée) ou sur la lecture (non vérifiée avant S2) ?
- Qu'est-ce qui, dans ce journal, ne tiendrait plus avec une équipe à la place d'un seul humain ?
