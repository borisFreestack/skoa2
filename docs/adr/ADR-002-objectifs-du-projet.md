# ADR-002 — Objectifs du projet : une application qui marche, une chaîne SDLC AI-native qu'on apprend, et une montée en compétence

Date : 2026-11-17
Statut : Accepté, amendé le 2026-11-17 (objectif 3)

## Contexte

Le cadrage (`docs/cadrage-poc.md`) présente le projet comme un POC « spec-to-prod ». Une issue écrite par un humain doit arriver en production sans qu'un humain touche au code, sauf à deux gates. Il le justifie par ce qu'il permet de montrer : « ce que ça prouve en entretien ».

L'ADR-001 et `CLAUDE.md` ne parlent que du domaine. Aucun artefact lu par un agent ne dit pourquoi la chaîne existe. Elle ne passe donc que pour un moyen de livrer l'application.

Le 2026-11-17, le porteur du projet a formulé deux ambitions :

1. créer une application fonctionnelle, conforme à ce qui est décrit ;
2. appréhender par la pratique les difficultés, les choix, les configurations possibles et l'architecture d'une chaîne SDLC AI-native, dans un contexte simplifié.

La seconde ne se ramène pas à « prouver ». Apprendre suppose de voir les frictions. Une chaîne qui marche parce qu'on a contourné ses difficultés en silence ne sert pas cet objectif.

Le même jour, une troisième dimension a été ajoutée. Le porteur du projet a une longue expérience de Java, Spring et Angular, interrompue pendant deux ans, et il découvre DDD et TDD. Le projet doit aussi lui servir à se remettre à niveau sur la pile et à apprendre ces deux pratiques, sur du code réel plutôt que sur des exercices.

## Décision

Le projet poursuit **trois objectifs de même rang**. Aucun n'est un simple moyen de servir les autres.

| | Objectif 1 — Application | Objectif 2 — Chaîne SDLC AI-native | Objectif 3 — Montée en compétence |
|---|---|---|---|
| Ce qu'on livre | skoa : les trois BC de l'ADR-001, conformes à la maquette v0.2 | une boucle issue → planner → agents de BC → gates → prod, avec deux gates humaines | une remise à niveau Java / Spring / Angular et une pratique de DDD et de TDD, ancrées dans le code de skoa |
| Atteint quand | la fonctionnalité de bout en bout de chaque sprint tourne et passe ses gates | chaque maillon de la chaîne a été mis en place, éprouvé, et son retour d'expérience écrit | chaque concept employé dans skoa est expliqué, situé dans le code, et le porteur du projet sait le réexpliquer et l'appliquer seul |
| Source de vérité | ADR-001, `contexts/`, maquette v0.2 | ce document, le cadrage (sections boucle, gates, mesures, backlog), `docs/journal-sdlc.md` | `docs/apprentissage.md` |

### Ce que « contexte simplifié » veut dire

Les simplifications sont volontaires. Elles ne doivent pas être prises pour des limites de la chaîne :
- trois bounded contexts, un seul dépôt, un seul humain qui tient les deux gates ;
- des données fictives, aucune personne réelle et aucune vraie production ;
- un poste de dev contraint (macOS 12, pas de Docker pour le front) ;
- un budget d'agents borné par l'abonnement.

Chaque fois qu'une conclusion dépend d'une de ces simplifications, le journal le note. Par exemple : « avec une équipe, la Gate 1 ne serait plus un label posé par une seule personne ».

### Règles d'arbitrage

Quand les objectifs tirent dans des sens opposés :

1. **Ne pas masquer une difficulté de la chaîne pour avancer l'application.** Si une gate bloque à tort, on la corrige et on note pourquoi ; on ne la désactive pas. Si un agent sort de son BC, on le consigne avant de corriger.
2. **Ne pas ajouter de complexité qui n'apprend rien.** Un outil ou une étape n'entre dans la chaîne que s'il répond à un risque nommé (cadrage, section Risques) ou s'il fait l'objet d'un apprentissage explicite. Le contexte reste simplifié.
3. **Un écart au plan est une donnée.** Un maillon prévu et pas fait, fait autrement ou fait par un agent alors qu'il était prévu à la main va dans le journal, avec sa raison.
4. **Préférer la forme qui enseigne, à coût comparable.** Entre deux façons équivalentes d'écrire le code, on choisit celle qui rend le concept visible : DDD tactique explicite (agrégats, value objects, événements), tests écrits d'abord. Mais on ne gonfle pas le code au-delà de ce que le domaine demande : un concept qui n'a pas de raison d'être dans skoa s'apprend ailleurs.

## Conséquences

- **`docs/journal-sdlc.md` devient un livrable.** Il trace, sprint par sprint, les choix de chaîne, les alternatives écartées, les frictions et les leçons. Il est rédigé au fil de l'eau, pas reconstitué à la fin.
- **Les choix structurants de la chaîne ont leur ADR**, au même titre que le domaine : orchestrateur, assemblage du contexte borné, protection des fichiers, stratégie de preview et de déploiement. Le journal renvoie aux ADR. Les ADR ne racontent pas le vécu.
- **L'expérience A/B du cadrage (contexte complet contre contexte borné) sert l'objectif 2.** Un résultat négatif ou mitigé est un résultat. Il ne dit pas que le projet a échoué.
- **Les agents ne poursuivent que l'objectif 1.** `CLAUDE.md` reste centré sur le domaine et les règles de BC. En revanche, un agent qui rencontre une friction de la chaîne (gate ambiguë, contexte insuffisant, règle contradictoire) la signale dans sa PR ou son issue plutôt que de la contourner. Cela découle déjà de la règle 4 de `CLAUDE.md`.
- **`docs/apprentissage.md` devient un livrable.** Il est rédigé en même temps que le code, une fiche par concept : ce que c'est, où le trouver dans skoa, le piège classique, et ce qui a changé récemment pour la pile. Le journal raconte la chaîne, ce fichier explique la technique et les pratiques ; ils se renvoient l'un à l'autre sans se répéter.
- **L'assistant explique au fil de l'eau.** Quand il emploie ou met en place un concept, il le signale dans sa réponse par une rubrique « À retenir », puis le reporte dans `docs/apprentissage.md`.
- **Le cadrage reste la référence pour la chaîne.** Ses sections « boucle d'agents », « gates CI/CD », « mesures » et « backlog » restent valables, sauf écart noté dans le journal ou dans un ADR.

## Questions ouvertes

| # | Question | Hypothèse actuelle |
|---|---|---|
| O1 | Les livrables « montrables » du cadrage (repo public, démo de 5 minutes, post de retour d'expérience) restent-ils des objectifs, ou deviennent-ils des sous-produits de l'apprentissage ? | Sous-produits : le journal en fournit la matière |
| O2 | S1 était prévue « sans agent » ; elle a été réalisée avec un agent généraliste qui voit tout le dépôt. Faut-il refaire une partie de S1 à la main pour garder une base de comparaison ? | Non. On le note dans le journal comme un écart, et la comparaison A/B de S3 sert de référence |
| O3 | Faut-il faire relire le journal par l'agent reviewer en S2, pour qu'il apprenne des frictions passées ? | Non tranché : risque d'élargir le contexte du reviewer |
| O4 | L'objectif 1 veut qu'aucun humain ne touche au code, alors que l'objectif 3 s'apprend mieux en écrivant. Où le porteur du projet code-t-il lui-même ? | Non tranché. Piste : il écrit à la main, en TDD, une partie de la fonctionnalité de bout en bout de S1 (par exemple l'agrégat `Demande` et ses invariants), et les agents prennent le relais en S2 |
