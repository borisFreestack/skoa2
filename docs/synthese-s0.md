# Synthèse S0 — design stratégique skoa

Mise à jour : 2026-11-13
Objet : reprendre le travail au même point. Ce fichier liste l'état, les décisions, ce qui reste ouvert et les incertitudes. Les artefacts eux-mêmes font foi : `contexts/`, `docs/adr/`, `CLAUDE.md`.

## Où on en est

S0 est terminée côté artefacts. L'event storming en interview a abouti à 3 bounded contexts, validés puis écrits et commités :

| Livrable | Fichier | Contenu |
|---|---|---|
| Context map | `contexts/context-map.yaml` | 3 BC + identité générique (Keycloak), relations par événements |
| Mise en relation (cœur) | `contexts/mise-en-relation/` | 27 termes, INV-MER-001 à 014 |
| Rencontre (cœur) | `contexts/rencontre/` | 19 termes, INV-REN-001 à 010 |
| Suivi (support) | `contexts/suivi/` | 19 termes, INV-SUI-001 à 007 |
| Périmètre | `docs/adr/ADR-001-perimetre-poc.md` | pivot vers la maquette v0.2, hors POC |
| Règles des agents | `CLAUDE.md` | 5 règles, vocabulaire interdit global |

Contrôles passés :
- tous les YAML se chargent ;
- chaque glossaire a entre 15 et 30 termes ;
- les identifiants d'invariants sont valides ;
- chaque événement de la context map est déclaré publié et consommé dans les `CONTEXT.md` concernés ;
- les termes interdits n'apparaissent que dans les listes `forbidden`.

Pas encore fait :
- relire les artefacts avec un regard extérieur ;
- trancher les questions ouvertes ;
- démarrer S1 (walking skeleton + CI/CD).

## Décisions prises (13/11/2026)

### Produit et source de vérité
- Le produit s'appelle **skoa**. « Pair Aidants » n'est plus utilisé.
- **La maquette « Coups de main entre adhérents » v0.2 fait foi** (https://claude.ai/artifact/5U58G3tFfHH3i83KAECtTz). Elle prime sur `docs/cadrage-poc.md` pour tout ce qui touche au domaine.
- Le cadrage n'est pas réécrit. L'ADR-001 note ce qui y est dépassé.

### Vocabulaire
- Jamais « pair-aidant » ni « pair-aidance » : la pratique est trop encadrée. On parle de pair, de soutien, d'entraide.
- Termes interdits partout : Patient, Client, Beneficiaire, Utilisateur, PairAidant, PairAidance, Aidant, Benevole.
- « Aide » et « accompagnement » restent admis dans les phrases, mais ne sont pas des termes du glossaire.
- « Coup de main » est un mot d'interface. Le domaine dit **Demande** (ce qu'on envoie), **Rencontre** (l'aide acceptée, jusqu'au retour) et **Abonnement** (ce qu'un adhérent propose).
- « Rendez-vous » ne désigne qu'un Service. **Preneur** désigne l'adhérent qui a dit oui.

### Règles métier
- Les demandes sont envoyées **par vagues** : les adhérents les plus proches d'abord, puis les moins sollicités récemment. **L'envoi s'arrête au premier oui.**
- L'anonymat est total jusqu'à l'acceptation. Ensuite, seul le prénom est révélé.
- Un **désistement** du Preneur relance les vagues sur la même Demande.
- Les **messages** d'une Rencontre peuvent être stockés. La mention « aucun contenu enregistré » de la maquette n'est pas une règle.
- Il n'y a **ni signalement ni suspension**. Le retour « J'aimerais en parler » et les demandes expirées vont au Référent, qui rappelle la personne.
- Le retour se fait sans note : Ressenti (Bien / Bof / BesoinDEnParler) et Presence. Il n'est jamais montré à l'autre participant.

### Périmètre
- **Hors POC :**
  - les événements de la structure ;
  - l'analyse de pratiques ;
  - le signalement et la suspension ;
  - le coaching, les crédits entreprise et les partenariats ;
  - l'envoi technique des emails ;
  - l'authentification (Keycloak).
- **Dans le POC :** plusieurs structures (tout est cloisonné par Structure) et l'identité visuelle de la structure.

### Décisions abandonnées
Ces réponses de l'interview ont été remplacées par la maquette :
- appariement sur une SituationVecue ;
- PairSoutien validé par une association ;
- plusieurs échanges par demande ;
- dialogue avant acceptation ;
- modération par signalement.

## Questions ouvertes

| # | Question | Hypothèse actuelle | Impact |
|---|---|---|---|
| Q1 | Un adhérent peut-il appartenir à plusieurs structures ? | Cloisonnement par Structure en place, règle d'appartenance non définie | Abonnement, ACL identité |
| Q2 | Le Retour est-il donné par les deux participants ? | Un Retour par participant est autorisé (la maquette ne montre que le demandeur) | INV-REN-007 |
| Q3 | L'heure se convient-elle seulement après l'acceptation ? | Oui, PropositionDHeure dans Rencontre | Frontière MER / REN |
| Q4 | Où vivent les adhésions (entrée d'un adhérent dans une structure) ? | Nulle part : ni Keycloak ni Suivi ne la portent | Trou de modélisation |
| Q5 | `docs/cadrage-poc.md` doit-il être mis à jour (nom, BC, fonctionnalité S1) ? | Non réécrit, dépassé selon l'ADR-001 | Contexte du planner |
| Q6 | Corriger les écarts de vocabulaire de la maquette (« côté aidant », « Tu accompagnes ») ? | À corriger, non modifié | UI, lint de langage |
| Q7 | Le build est en Gradle alors que le cadrage parle de `mvn verify`. Lequel retenir ? | Non traité | Gates CI de S1 |

## Incertitudes de design

1. **La boucle entre mise-en-relation et rencontre.** `DemandeAcceptee` va dans un sens, `DesistementSignale` et `RencontreAnnulee` dans l'autre : les deux cœurs dépendent l'un de l'autre. L'alternative serait de garder le désistement dans mise-en-relation, mais le cycle de vie de la Demande déborderait alors sur la Rencontre.
2. **Le paramétrage est réparti entre deux BC.** Services et règles d'envoi sont dans mise-en-relation ; identité, référent et seuil d'affichage sont dans suivi. L'écran « Réglages de la structure » mélange les deux. `StructureCreee` (suivi → mise-en-relation) ajoute une dépendance.
3. **Rencontre est classée cœur.** Sans signalement, elle ressemble à un BC de support. Je l'ai classée cœur parce que la confiance (anonymat, retour sans note, désistement libre) fait le produit.
4. **Mise en relation a le glossaire le plus chargé** (27 termes, pour un plafond de 30). Si de nouveaux termes arrivent, il faudra envisager d'en sortir Abonnement ou les règles d'envoi.

## Écarts au plan validé

- J'ai ajouté `AbonnementEnregistre` et `AbonnementRepris` aux événements de mise-en-relation vers suivi. Ils sont nécessaires pour compter, par service, les adhérents qui proposent leur aide.
- Deux commits correctifs : le YAML de Suivi était invalide, et Annulation / Desistement s'interdisaient mutuellement.

## Prochaines étapes

1. Trancher Q1 à Q7, en priorité Q4 (adhésions) et Q7 (build).
2. Relire les glossaires et les invariants à froid. Chaque invariant devra être lié à au moins un test (gate « invariants couverts »).
3. **S1 :**
   - squelette Spring Boot + Spring Modulith (1 module par BC) et Angular (1 lib par BC) ;
   - fonctionnalité de bout en bout : s'abonner à un service et recevoir une Sollicitation pour une Demande proche (remplace « déclarer une situation vécue » du cadrage) ;
   - scripts de gates DDD (conformité à la context map, lint de langage, couverture des invariants), en reprenant les contrôles déjà faits en S0.

## Pour reprendre

Lire, dans l'ordre :
1. ce fichier ;
2. `docs/adr/ADR-001-perimetre-poc.md` ;
3. `contexts/context-map.yaml` ;
4. les trois `contexts/<bc>/CONTEXT.md`.

Consulter la maquette pour toute question de comportement. En cas de conflit entre la maquette et le cadrage, la maquette l'emporte.
