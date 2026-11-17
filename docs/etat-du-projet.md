# État du projet skoa

Mis à jour : 2026-11-17, en fin de session.

Ce fichier dit où on en est, pour reprendre au même point. Il est réécrit à chaque fin de session, pas complété : l'historique est dans Git, le vécu dans `docs/journal-sdlc.md`. Les artefacts eux-mêmes font foi : `contexts/`, `docs/adr/`, `CLAUDE.md`, `gates/`.

`docs/synthese-s0.md` reste l'état de fin de S0, figé au 2026-11-13.

## En une phrase

S0 (modélisation) est terminée. S1 (walking skeleton et CI/CD) est à mi-chemin : le squelette, les contrats, la CI, les gates DDD et la protection des fichiers sont en place et bloquants. Il reste PIT, les tests rejoués sur la branche de base, la fonctionnalité de bout en bout, les images et la preview.

## Les trois objectifs (ADR-002)

1. **Application** : livrer skoa, conforme à la maquette v0.2 et à l'ADR-001.
2. **Chaîne SDLC AI-native** : apprendre en pratique ce qu'elle coûte et impose. Trace : `docs/journal-sdlc.md`.
3. **Montée en compétence** : remise à niveau Java / Spring / Angular, découverte de DDD et TDD. Trace : `docs/apprentissage.md`. Cet objectif est ajouté par la PR #3, pas encore fusionnée.

## Ce qui est en place

| Brique | Où | État |
|---|---|---|
| Modèle du domaine : 3 BC, glossaires, invariants, context map | `contexts/` | stable depuis S0 |
| Backend Spring Boot 4.1 + Spring Modulith 2.1, un module par BC | `backend/` | squelette vide, sans code métier |
| Frontend Angular 22, zoneless, Vitest, un module Sheriff par BC | `frontend/` | squelette vide |
| Contrats OpenAPI par BC, code généré à chaque build | `contracts/` | contrats vides (`paths: {}`) |
| CI : backend, frontend, contrats (oasdiff), gates DDD | `.github/workflows/ci.yml` | vert |
| Gates DDD : artefacts, langage, invariants (Python), context map (Java) | `gates/`, `backend/src/test/java/org/skoa/ContextMapTest.java` | vertes, chacune vue en échec |
| Fichiers protégés : CODEOWNERS + check en `pull_request_target` + label | `.github/CODEOWNERS`, `.github/workflows/fichiers-proteges.yml` | vu en échec et en succès sur GitHub (PR #2) |
| Dépôt public et ruleset de `main` | GitHub | PR obligatoire, 7 checks obligatoires, aucun contournement |

## En cours

- **PR #3** (https://github.com/borisFreestack/skoa2/pull/3) : ADR-002 amendé (objectif 3) et `docs/apprentissage.md`. Elle touche `docs/adr/`, donc elle attend le label `modification-protegee-validee` puis le merge.
- **ADR-003** (agent reviewer Devstral via l'API Mistral, non bloquant) : statut « Proposé », questions R1 à R4 ouvertes. Prévu pour S2, ou dès S1 selon R2.

## Prochaines étapes (ordre du backlog S1)

1. PIT (mutation testing) et ArchUnit.
2. Gate « tests rejoués sur la branche de base » : un nouveau test doit échouer sans le code qu'il accompagne.
3. Fonctionnalité de bout en bout : s'abonner à un service et recevoir une Sollicitation pour une Demande proche. Si O4 est tranchée dans ce sens, le porteur du projet l'écrit en partie à la main, en TDD.
4. Images (Jib, Docker), preview Helm sur k3d, e2e Playwright, déploiement et rollback.

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
| — | Orchestrateur de S2 | Claude Agent SDK, ou Claude Code headless lancé par la CI (cadrage) |

## Comment on travaille

- **Rien ne va directement sur `main`.** Une branche, une PR, les 7 checks verts, puis le merge.
- **Fichier protégé modifié** (liste dans `.github/CODEOWNERS`) : le check « Fichiers protégés » échoue jusqu'à ce que le propriétaire pose le label `modification-protegee-validee`. Seul l'humain pose ce label, jamais l'agent. Chaque nouveau commit le retire.
- **En local avant de pousser :**
  - `python3 gates/verifier.py` ;
  - `python3 -m unittest discover -s gates/tests -t gates/tests` ;
  - `JAVA_HOME=$(/usr/libexec/java_home -v 21) ./gradlew build`.
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
