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

### 2026-11-17 — Le reviewer sera Devstral, pas Claude

- **Fait** : l'agent reviewer, prévu en S2, est cadré avant d'être implémenté (ADR-003). Il tournera sur Devstral, par l'API Mistral, depuis GitHub Actions, et ses commentaires ne bloqueront pas la PR.
- **Choix** : un modèle d'une autre famille que celle de l'agent code, pour ne pas relire avec les mêmes angles morts. Écartés : Claude (angles morts corrélés), OpenRouter (un intermédiaire de plus pour les données), Ollama en local (le modèle tient mal dans 16 Go et la review sortirait de la CI), un verdict bloquant d'emblée (taux de faux positifs inconnu).
- **Friction** :
  - Deux écarts au cadrage. La boucle n'est plus mono-fournisseur : l'orchestrateur et les agents tests et code restent sur Claude. Et le « même modèle » de l'expérience A/B devient ambigu : il faut préciser qu'il porte sur l'agent code, le reviewer restant identique dans les deux configurations.
  - C'est la première sortie volontaire de contenu du dépôt vers un service tiers. Elle applique la règle posée pour oasdiff : on l'a décidée explicitement au lieu de la laisser passer par défaut.
- **Leçon** :
  - Le cadrage disait ce que le reviewer voit, pas sur quel modèle il tourne. Pour un agent qui juge d'autres agents, le modèle fait partie de son contexte : il décide de ce qu'il est capable de ne pas voir.
  - La gate de langage laisse passer un terme métier inventé mais neutre (entrée précédente). Ce cas entre explicitement dans la grille du reviewer, au lieu de rester l'affaire d'une review humaine non écrite.
  - Un reviewer non bloquant n'a de valeur que si on compte ce qu'il trouve : commentaires utiles, faux positifs, défauts que les gates n'avaient pas vus. C'est ce compte qui dira, par un nouvel ADR, s'il peut devenir bloquant.
- **Simplification** : les données sont fictives, ce qui rend acceptable l'envoi du diff chez Mistral. Avec des données réelles, il faudrait un modèle hébergé sur place ou un contrat de traitement des données.

### 2026-11-17 — Protéger les fichiers protégés : CODEOWNERS ne suffit pas

- **Fait** : `.github/CODEOWNERS` liste les fichiers protégés (`contexts/`, `contracts/`, `gates/`, la CI, `CLAUDE.md`, les ADR, la configuration des gates). Un check « Fichiers protégés » fait échouer une PR qui les touche, tant qu'un propriétaire n'a pas posé le label `modification-protegee-validee`. La règle 4 de `CLAUDE.md` renvoie désormais à cette liste.
- **Choix** :
  - Le check tourne en `pull_request_target`, donc avec la version de la branche de base. Avec `pull_request`, une PR pourrait modifier le workflow ou le script qui la juge.
  - La validation passe par un label plutôt que par une review approuvée, pour trois raisons. GitHub interdit d'approuver sa propre PR, ce qui bloquerait les PR du seul humain. `pull_request_target` ne se déclenche pas sur une review. Et un label est le geste déjà prévu pour la Gate 1.
  - Le label est retiré à chaque nouveau commit : une validation porte sur un état précis de la PR.
  - La liste n'existe qu'à un endroit, `CODEOWNERS`. Le script la lit au lieu d'en tenir une copie.
- **Friction** :
  - Le dépôt est privé, sur un compte GitHub gratuit : ni protection de branche ni rulesets (HTTP 403). CODEOWNERS n'impose donc aucune review, aucun check ne peut être exigé avant le merge, et un push direct sur `main` reste possible. Toutes les gates sont aujourd'hui des signaux, pas des barrières.
  - Le check ne reconnaît un agent qu'à son identité GitHub. Si un agent pousse avec le compte du propriétaire, il peut poser le label lui-même.
- **Leçon** :
  - Une gate n'est bloquante que si la plateforme la rend obligatoire. Le meilleur script ne remplace pas la protection de branche. Cette dépendance à l'offre de l'hébergeur fait partie de l'architecture de la chaîne.
  - L'identité des agents est un choix de sécurité, pas un détail d'outillage. Elle doit être tranchée avant S2 : un GitHub App ou le `github.token` d'un workflow, jamais le compte du propriétaire.
  - Faire tourner un check en `pull_request_target` ferme une porte et en ouvre une autre : il ne faut jamais y exécuter le code de la PR.
- **Simplification** : un seul propriétaire pour tout. Avec une équipe, chaque dossier aurait ses propriétaires, et la règle « la dernière ligne qui couvre un chemin l'emporte » compterait.

### 2026-11-17 — Rendre le dépôt public : l'historique publie aussi des métadonnées

- **Fait** : le dépôt est passé en public pour obtenir la protection de branche. Avant de le publier, l'historique a été vérifié : aucun secret ni fichier sensible, mais l'adresse email personnelle figurait comme auteur des 24 commits.
- **Choix** :
  - L'historique a été réécrit avec l'adresse noreply GitHub (`git filter-branch`, faute de `git filter-repo` installé), après une sauvegarde complète en bundle. Le contenu des fichiers est identique, mais les SHA ont changé. `main` a été force-pushée avec `--force-with-lease` sur l'ancien SHA distant.
  - L'adresse noreply est fixée dans la configuration git locale du dépôt, pour qu'elle ne revienne pas au prochain commit.
  - Alternatives écartées : publier avec l'adresse visible, ou attendre que le réglage soit fait côté GitHub.
- **Friction** :
  - La fuite n'était pas dans le code mais dans les métadonnées de commit, qu'aucune gate ne regarde.
  - `filter-branch` réécrit aussi la référence locale `origin/main`. Il a fallu refaire un fetch pour que `--force-with-lease` compare au vrai état distant.
  - GitHub peut garder les anciens commits accessibles par SHA tant que son support ne les a pas purgés.
- **Leçon** : publier est quasi irréversible (cache, indexation, robots). La vérification avant publication porte sur l'historique entier, métadonnées comprises, pas seulement sur l'état courant des fichiers. Une réécriture d'historique est faisable tant que le dépôt n'a qu'un seul clone actif. Après, elle casse le travail des autres.
- **Simplification** : un seul clone et aucune PR ouverte. Avec une équipe, réécrire `main` imposerait à chacun de recloner.

### 2026-11-17 — Le ruleset de `main` : les gates deviennent des barrières

- **Fait** : un ruleset protège `main`. Il interdit la suppression et le force-push, exige une PR et rend obligatoires sept checks : « Gates DDD », « Backend », « Frontend », « Fichiers protégés » et les trois « Contrat <bc> ». Cette entrée est la première à passer par ce chemin.
- **Choix** :
  - Aucune review approuvée exigée et pas de review obligatoire des code owners : GitHub interdit d'approuver sa propre PR, et il n'y a qu'un humain. La validation humaine des fichiers protégés passe par le label, contrôlé par le check « Fichiers protégés ».
  - Aucune exception de contournement, même pour l'administrateur. Une gate qu'on peut contourner sans trace n'apprend rien. En cas de blocage, on modifie le ruleset, ce qui laisse une trace.
  - La branche n'a pas besoin d'être à jour avec `main` avant le merge. C'est inutile avec un seul contributeur.
- **Friction** :
  - Les checks obligatoires sont identifiés par le nom du job. Renommer un job dans la CI le rend introuvable, et la PR attend alors un check qui n'arrivera jamais. Les jobs en matrice ajoutent un piège : le job « Contrat » s'affiche avec un `${{ matrix.bc }}` littéral quand il est sauté sur un push.
  - Depuis cette entrée, plus aucun commit ne va directement sur `main`, ni ceux de l'humain, ni ceux de l'agent qui l'assiste.
- **Leçon** : renommer un job ou un workflow, c'est modifier le contrat du ruleset. C'est une raison de plus pour que `.github/` soit protégé.
- **Simplification** : un seul humain. Avec une équipe, on exigerait au moins une review approuvée par un code owner, et le label deviendrait inutile pour les humains.

### 2026-11-18 — PIT et ArchUnit : des gates sur un code qui n'existe pas encore

- **Fait** : deux gates de plus dans `./gradlew build`, donc dans le check obligatoire « Backend ». ArchUnit impose cinq couches par BC (`domaine`, `application`, `adaptateurs`, `evenements`, `api`) et leurs sens de dépendance. PIT mute `domaine` et `application` et exige 80 % de mutants tués.
- **Choix** :
  - La convention de paquets est fixée maintenant, avant le premier agrégat : une règle posée après le code se négocie contre l'existant. Elle est écrite dans `gates/README.md`, là où l'agent la lit.
  - Une règle d'ArchUnit range tout le code d'un BC dans une couche connue. Sans elle, du code métier posé à la racine du BC échapperait à la fois aux règles hexagonales et à PIT, qui ne cible que deux paquets.
  - Les règles prennent la racine en paramètre, pour être prouvées sur un faux BC (`org.skoa.exemples.architecture`), comme les gates Python sur leurs fixtures. Ce faux BC est ajouté à `CODEOWNERS` : affaiblir l'exemple fautif affaiblirait la preuve.
  - PIT ne compte que les tests rangés dans un paquet de BC. Les tests des gates, à la racine de `org.skoa`, ne doivent pas tuer de mutants métier.
  - PIT tourne dans `check`, sans nouveau job CI : un nouveau job n'aurait été bloquant qu'après une modification du ruleset.
  - PIT 1.30.1 plutôt que 1.30.2, sortie il y a moins de deux semaines.
- **Friction** :
  - Sur des BC vides, une gate verte ne prouve rien. ArchUnit refuse par défaut une règle sans classe ; il a fallu l'autoriser explicitement (`allowEmptyShould`), et compter sur le faux BC pour prouver qu'elle mord. PIT, de même, réussit avec « No mutations found » (`failWhenNoMutations = false`).
  - PIT a été vu en échec à la main, avec une classe et un test temporaires, puis retirés : 33 % sur `km <= rayon` testé par le seul cas `(1, 5)`, 100 % après avoir ajouté la limite. Aucun test automatique ne prouve que la configuration de PIT reste mordante.
- **Leçon** : une gate se pose avant le code qu'elle juge, mais elle ne se prouve que sur un exemple fautif. Pour une règle statique (ArchUnit), l'exemple fautif peut vivre dans le dépôt ; pour une mesure (PIT), il faut le fabriquer à chaque fois qu'on la change.
- **Simplification** : PIT mute tous les BC à chaque build, et le seuil est le même pour tous. Le cadrage prévoyait de ne muter que le BC modifié, et l'ADR-001 met plus de soin sur les BC cœur.

---

## Reste à faire en S1 (au 18/11/2026)

D'après le backlog du cadrage :

- [ ] fonctionnalité de bout en bout : s'abonner à un service et recevoir une Sollicitation pour une Demande proche ;
- [x] scripts de gates DDD : conformité à la context map, lint de langage (avec la vérification croisée des `forbidden`), couverture des invariants ;
- [x] PIT (mutation testing), ArchUnit ;
- [ ] tests rejoués sur la branche de base ;
- [x] fichiers protégés (CODEOWNERS et check de chemins), bloquants grâce au ruleset de `main` ;
- [ ] images (Jib, Docker), preview Helm sur k3d, e2e Playwright, déploiement et rollback.

## Questions de chaîne à garder en tête

- Comment voir rougir chaque gate au moins une fois, pour prouver qu'elle bloque vraiment ?
- Où s'arrête la règle 1 : sur les imports (vérifiée) ou sur la lecture (non vérifiée avant S2) ?
- Qu'est-ce qui, dans ce journal, ne tiendrait plus avec une équipe à la place d'un seul humain ?
