# État du projet skoa

Mis à jour : 2026-11-18, en fin de session.

Ce fichier dit où on en est, pour reprendre au même point. Il est réécrit à chaque fin de session, pas complété : l'historique est dans Git, le vécu dans `docs/journal-sdlc.md`. Les artefacts eux-mêmes font foi : `contexts/`, `docs/adr/`, `CLAUDE.md`, `gates/`.

`docs/synthese-s0.md` reste l'état de fin de S0, figé au 2026-11-13.

## En une phrase

S0 (modélisation) est terminée. S1 (walking skeleton et CI/CD) a toutes ses gates de qualité : squelette, contrats, CI, gates DDD, ArchUnit, PIT, tests rejoués sur la branche de base, protection des fichiers. Il reste la fonctionnalité de bout en bout, puis les images et la preview. Le prochain pas est une décision de domaine (Q4), pas du code.

## Les trois objectifs (ADR-002)

1. **Application** : livrer skoa, conforme à la maquette v0.2 et à l'ADR-001.
2. **Chaîne SDLC AI-native** : apprendre en pratique ce qu'elle coûte et impose. Trace : `docs/journal-sdlc.md`.
3. **Montée en compétence** : remise à niveau Java / Spring / Angular, découverte de DDD et TDD. Trace : `docs/apprentissage.md`.

## Ce qui est en place

| Brique | Où | État |
|---|---|---|
| Modèle du domaine : 3 BC, glossaires, invariants, context map | `contexts/` | stable depuis S0 |
| Backend Spring Boot 4.1 + Spring Modulith 2.1, un module par BC | `backend/` | squelette vide, sans code métier |
| Frontend Angular 22, zoneless, Vitest, un module Sheriff par BC | `frontend/` | squelette vide |
| Contrats OpenAPI par BC, code généré à chaque build | `contracts/` | contrats vides (`paths: {}`) |
| CI : backend, frontend, contrats (oasdiff), gates DDD | `.github/workflows/ci.yml` | vert |
| Gates DDD : artefacts, langage, invariants (Python), context map (Java) | `gates/`, `backend/src/test/java/org/skoa/ContextMapTest.java` | vertes, chacune vue en échec |
| Architecture hexagonale : 5 couches par BC (ArchUnit), prouvée sur un faux BC | `backend/src/test/java/org/skoa/Architecture*.java`, `gates/README.md` | verte, chaque règle vue en échec |
| Mutation testing : PIT sur `domaine` et `application`, seuil 80 % | `backend/build.gradle.kts` | vert (rien à muter), vu en échec à la main |
| Tests rejoués sur la branche de base : chaque nouveau test de BC doit y échouer | `gates/tests_rejoues.py`, job CI dédié, règle 6 de `CLAUDE.md` | vue en échec à la main sur trois cas ; **pas encore obligatoire** (voir « En cours ») |
| Fichiers protégés : CODEOWNERS + check en `pull_request_target` + label | `.github/CODEOWNERS`, `.github/workflows/fichiers-proteges.yml` | vu en échec et en succès sur GitHub (PR #2) |
| Dépôt public et ruleset de `main` | GitHub | PR obligatoire, 7 checks obligatoires, aucun contournement |

## En cours

- **Ruleset de `main`** : le 18/11 en fin de session, il n'exige encore que 7 checks, sans « Tests rejoués sur la branche de base ». La mise à jour n'a pas pris. À vérifier, puis à refaire :
  ```sh
  gh api repos/borisFreestack/skoa2/rulesets/27450136 --jq '[.rules[]|select(.type=="required_status_checks").parameters.required_status_checks[].context]'
  ```
- **ADR-003** (agent reviewer Devstral via l'API Mistral, non bloquant) : statut « Proposé », questions R1 à R4 ouvertes. Prévu pour S2, ou dès S1 selon R2.

## Prochaines étapes (ordre du backlog S1)

1. Trancher Q4 (où vivent les adhésions) et O4 (où le porteur du projet code lui-même) : les deux conditionnent l'étape suivante.
2. Fonctionnalité de bout en bout : s'abonner à un service et recevoir une Sollicitation pour une Demande proche. Si O4 est tranchée dans ce sens, le porteur du projet l'écrit en partie à la main, en TDD. Premier code métier : les gates d'invariants, d'architecture, PIT et tests rejoués jugeront enfin du vrai code.
3. Images (Jib, Docker), preview Helm sur k3d, e2e Playwright, déploiement et rollback.

## Décisions à prendre

### Domaine (synthèse S0, toujours ouvertes)

| # | Question | Hypothèse actuelle |
|---|---|---|
| Q1 | Un adhérent peut-il appartenir à plusieurs structures ? | Cloisonnement par Structure, règle d'appartenance non définie |
| Q2 | Le Retour est-il donné par les deux participants ? | Un Retour par participant |
| Q3 | L'heure se convient-elle seulement après l'acceptation ? | Oui, dans `rencontre` |
| Q4 | Où vivent les adhésions ? | Nulle part : trou de modélisation, **prioritaire** |
| Q5 | Faut-il mettre à jour `docs/cadrage-poc.md` ? | Non, l'ADR-001 prime |
| Q6 | Corriger les écarts de vocabulaire de la maquette ? | À corriger, pas encore fait |
| — | `DemandeAcceptee` a deux payloads différents (vers `rencontre` et vers `suivi`), mais un seul record en Java | La gate exige l'union. Tâche contrat à ouvrir : deux événements, ou un payload unique assumé |

Q7 (Gradle ou Maven) est tranchée : Gradle.

### Projet et chaîne

| # | Question | Hypothèse actuelle |
|---|---|---|
| O1 | Les livrables « montrables » restent-ils des objectifs ? | Sous-produits de l'apprentissage |
| O2 | Refaire une partie de S1 à la main ? | Non, l'écart est noté au journal |
| O3 | Le reviewer lit-il le journal ? | Non tranché |
| O4 | Où le porteur du projet code-t-il lui-même ? | Piste : l'agrégat `Demande` en TDD en S1 |
| — | Identité GitHub des agents en S2 | GitHub App ou `github.token` d'un workflow, **jamais le compte du propriétaire** |
| — | Vocabulaire interdit partout lisible par la machine | Aujourd'hui en prose dans `CLAUDE.md`, lu par la gate |
| — | Méthode de merge | Squash et merge commit tous deux autorisés ; à restreindre au squash si on veut un historique linéaire |
| — | PR « test seul » sur un comportement existant (règle 6) | Bloquée par la gate des tests rejoués, sans contournement possible. Piste : un label `test-sans-code-valide` posé par l'humain, à créer au premier cas réel |
| — | Voir rougir PIT et les tests rejoués automatiquement | Aujourd'hui vus en échec à la main seulement |
| — | Tests rejoués côté Angular (`*.spec.ts`) | Non rejoués : à faire quand le front aura du code de BC |
| — | PIT sur le seul BC modifié, seuil par BC (cœur ou support) | PIT mute tous les BC, seuil unique de 80 % |
| — | Orchestrateur de S2 | Claude Agent SDK, ou Claude Code headless lancé par la CI (cadrage) |

## Comment on travaille

- **Rien ne va directement sur `main`.** Une branche, une PR, les checks obligatoires verts, puis le merge.
- **Fichier protégé modifié** (liste dans `.github/CODEOWNERS`) : le check « Fichiers protégés » échoue jusqu'à ce que le propriétaire pose le label `modification-protegee-validee`. Seul l'humain pose ce label, jamais l'agent. Chaque nouveau commit le retire.
- **En local avant de pousser :**
  - `python3 gates/verifier.py` ;
  - `python3 -m unittest discover -s gates/tests -t gates/tests` ;
  - `JAVA_HOME=$(/usr/libexec/java_home -v 21) ./gradlew build` (tests, ArchUnit, PIT) ;
  - `JAVA_HOME=$(/usr/libexec/java_home -v 21) python3 gates/tests_rejoues.py` si la PR touche des tests de BC.
- **Poste :** macOS 12, Java 8 par défaut (le JDK 21 est choisi par la toolchain Gradle), Node via nvm, Python 3.13 + PyYAML. Pas de Docker pour le front, et éviter les binaires qui exigent macOS 14.
- **Commits :** auteur avec l'adresse noreply GitHub, fixée dans la configuration git locale du dépôt.
- **Explications :** l'assistant ajoute une rubrique « À retenir » quand il emploie un concept, et la reporte dans `docs/apprentissage.md`.

## Pour reprendre

Lire, dans l'ordre :
1. ce fichier ;
2. `docs/adr/ADR-002-objectifs-du-projet.md`, puis ADR-001 et ADR-003 ;
3. la fin de `docs/journal-sdlc.md` ;
4. `CLAUDE.md` et `gates/README.md` ;
5. `contexts/context-map.yaml` et le `CONTEXT.md` du BC concerné.
