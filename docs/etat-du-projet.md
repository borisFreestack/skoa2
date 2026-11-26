# État du projet skoa

Mis à jour : 2026-11-26.

Ce fichier dit où on en est, pour reprendre au même point. Il est réécrit à chaque fin de session, pas complété : l'historique est dans Git, le vécu dans `docs/journal-sdlc.md`. Les artefacts eux-mêmes font foi : `contexts/`, `docs/adr/`, `CLAUDE.md`, `gates/`.

`docs/synthese-s0.md` reste l'état de fin de S0, figé au 2026-11-13.

## En une phrase

S0 (modélisation) est terminée. S1 (walking skeleton et CI/CD) a toutes ses gates de qualité : squelette, contrats, CI, gates DDD, ArchUnit, PIT, tests rejoués sur la branche de base, protection des fichiers. Il reste la fonctionnalité de bout en bout, puis les images et la preview. Q4 est tranchée (ADR-004) et l'identité se fera sans Keycloak (ADR-005). Le modèle correspondant est sur `main` (PR #8, mergée le 23/11). O4 est tranchée le 24/11 : le porteur du projet écrit `Adhesion` lui-même, en TDD. Le premier code métier existe : l'enregistrement d'une `Adhesion` et INV-SUI-008 (PR du 26/11). Le prochain pas est la publication de `AdhesionEnregistree`.

## Les trois objectifs (ADR-002)

1. **Application** : livrer skoa, conforme à la maquette v0.2 et à l'ADR-001.
2. **Chaîne SDLC AI-native** : apprendre en pratique ce qu'elle coûte et impose. Trace : `docs/journal-sdlc.md`.
3. **Montée en compétence** : remise à niveau Java / Spring / Angular, découverte de DDD et TDD. Trace : `docs/apprentissage.md`.

## Ce qui est en place

| Brique | Où | État |
|---|---|---|
| Modèle du domaine : 3 BC, glossaires, invariants, context map | `contexts/` | complété le 23/11 : `Adhesion` dans `suivi`, deux événements vers `mise-en-relation`, plus de Keycloak |
| Backend Spring Boot 4.1 + Spring Modulith 2.1, un module par BC | `backend/` | squelette vide, sans code métier |
| Frontend Angular 22, zoneless, Vitest, un module Sheriff par BC | `frontend/` | squelette vide |
| Contrats OpenAPI par BC, code généré à chaque build | `contracts/` | contrats vides (`paths: {}`) |
| CI : backend, frontend, contrats (oasdiff), gates DDD | `.github/workflows/ci.yml` | vert |
| Gates DDD : artefacts, langage, invariants (Python), context map (Java) | `gates/`, `backend/src/test/java/org/skoa/ContextMapTest.java` | vertes, chacune vue en échec |
| Architecture hexagonale : 5 couches par BC (ArchUnit), prouvée sur un faux BC | `backend/src/test/java/org/skoa/Architecture*.java`, `gates/README.md` | verte, chaque règle vue en échec |
| Mutation testing : PIT sur `domaine` et `application`, seuil 80 % | `backend/build.gradle.kts` | vert (rien à muter), vu en échec à la main |
| Tests rejoués sur la branche de base : chaque nouveau test de BC doit y échouer | `gates/tests_rejoues.py`, job CI dédié, règle 6 de `CLAUDE.md` | vue en échec à la main sur trois cas ; obligatoire depuis le 23/11 |
| Fichiers protégés : CODEOWNERS + check en `pull_request_target` + label | `.github/CODEOWNERS`, `.github/workflows/fichiers-proteges.yml` | vu en échec et en succès sur GitHub (PR #2) |
| Dépôt public et ruleset de `main` | GitHub | PR obligatoire, 8 checks obligatoires, aucun contournement |

## En cours

- **Point d'arrêt du 26/11** : l'enregistrement d'une `Adhesion` est écrit par le porteur du projet, en TDD (branche `s1/adhesion`, PR ouverte). Toutes les gates passent ; PIT tue 6 mutants sur 6.
  - **Code** : `Adhesion.enregistrer` refuse une seconde Adhesion en cours dans une même Structure (INV-SUI-008), via le port `Adhesions`. Le fake `AdhesionsEnMemoire` est dans les tests.
  - **Écarts au plan du 24/11** : les tests 3 (autre Structure) et 4 (autre personne) ne sont pas écrits. Ils passeraient du premier coup, car c'est le fake qui filtre. Leur place est le test du futur adaptateur de persistance.
  - **Refus** : une `IllegalStateException` avec un message. Une exception métier nommée serait un terme nouveau, à proposer d'abord (règle 3).
  - **Cycle suivant** : publier `AdhesionEnregistree`, puis le cas d'usage qui enregistre l'Adhesion (et donc le `save` du port). Hors de portée : la fin d'Adhesion, et « seul le Referent enregistre », faute d'agrégat `Structure`.
- **ADR-003** (agent reviewer Devstral via l'API Mistral, non bloquant) : statut « Proposé », questions R1 à R4 ouvertes. Prévu pour S2, ou dès S1 selon R2.

## Prochaines étapes (ordre du backlog S1)

1. Publier `AdhesionEnregistree`, puis le cas d'usage qui enregistre une Adhesion (voir « En cours »).
2. Suite de la fonctionnalité de bout en bout : enregistrer une Adhesion (`suivi`), puis s'abonner à un service et recevoir une Sollicitation pour une Demande proche (`mise-en-relation`), avec des identifiants fictifs fixes. Le porteur du projet écrit ensuite `Demande`. Premier code métier : les gates d'invariants, d'architecture, PIT et tests rejoués jugeront enfin du vrai code.
3. `identite`, serveur d'autorisation Spring en application séparée (ADR-005).
4. Images (Jib, Docker), preview Helm sur k3d, e2e Playwright, déploiement et rollback.

## Décisions à prendre

### Domaine (synthèse S0, toujours ouvertes)

| # | Question | Hypothèse actuelle |
|---|---|---|
| Q1 | Un adhérent peut-il appartenir à plusieurs structures ? | Permis par le modèle, une seule à l'écran (A4 de l'ADR-004) |
| Q2 | Le Retour est-il donné par les deux participants ? | Un Retour par participant |
| Q3 | L'heure se convient-elle seulement après l'acceptation ? | Oui, dans `rencontre` |
| Q5 | Faut-il mettre à jour `docs/cadrage-poc.md` ? | Non, l'ADR-001 prime |
| Q6 | Corriger les écarts de vocabulaire de la maquette ? | À corriger, pas encore fait |
| — | `DemandeAcceptee` a deux payloads différents (vers `rencontre` et vers `suivi`), mais un seul record en Java | La gate exige l'union. Tâche contrat à ouvrir : deux événements, ou un payload unique assumé |
| A5 | Une Rencontre en cours survit-elle au départ d'un Participant ? | Oui |
| A6 | `ModulesTest` refuse les cycles que la context map déclare | Les tolérer s'ils sont déclarés, **avant le premier écouteur dans `suivi`** |
| A8 | Publier `ReferentDesigne` vers `mise-en-relation` ? | Oui, par une tâche contrat |
| — | Enregistrements simultanés d'une même Adhesion | INV-SUI-008 ne les couvre pas : contrainte d'unicité en base, quand la persistance arrivera |
| I1 à I4 | Questions d'identité | Voir ADR-005 |

Q4 (adhésions) est tranchée : dans `suivi`, ADR-004. Q7 (Gradle ou Maven) est tranchée : Gradle.

### Projet et chaîne

| # | Question | Hypothèse actuelle |
|---|---|---|
| O1 | Les livrables « montrables » restent-ils des objectifs ? | Sous-produits de l'apprentissage |
| O2 | Refaire une partie de S1 à la main ? | Non, l'écart est noté au journal |
| O3 | Le reviewer lit-il le journal ? | Non tranché |
| — | Identité GitHub des agents en S2 | GitHub App ou `github.token` d'un workflow, **jamais le compte du propriétaire** |
| — | Vocabulaire interdit partout lisible par la machine | Aujourd'hui en prose dans `CLAUDE.md`, lu par la gate |
| — | Méthode de merge | Squash et merge commit tous deux autorisés ; à restreindre au squash si on veut un historique linéaire |
| — | PR « test seul » sur un comportement existant (règle 6) | Bloquée par la gate des tests rejoués, sans contournement possible. Piste : un label `test-sans-code-valide` posé par l'humain, à créer au premier cas réel |
| — | Voir rougir PIT et les tests rejoués automatiquement | Aujourd'hui vus en échec à la main seulement |
| — | Tests rejoués côté Angular (`*.spec.ts`) | Non rejoués : à faire quand le front aura du code de BC |
| — | PIT sur le seul BC modifié, seuil par BC (cœur ou support) | PIT mute tous les BC, seuil unique de 80 % |
| — | Orchestrateur de S2 | Claude Agent SDK, ou Claude Code headless lancé par la CI (cadrage) |

O4 (où le porteur du projet code-t-il lui-même) est tranchée le 24/11 : `Adhesion`, puis `Demande`, en TDD. A9 (qui applique INV-SUI-008) est tranchée le 26/11 : le domaine, par le port `Adhesions`.

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
2. `docs/adr/ADR-002-objectifs-du-projet.md`, puis ADR-001, ADR-003, ADR-004 et ADR-005 ;
3. la fin de `docs/journal-sdlc.md` ;
4. `CLAUDE.md` et `gates/README.md` ;
5. `contexts/context-map.yaml` et le `CONTEXT.md` du BC concerné.
