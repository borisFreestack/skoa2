# ADR-004 — Les adhésions vivent dans `suivi`

Date : 2026-11-23
Statut : Accepté

Répond à la question Q4 de la synthèse S0. Complète l'ADR-001.

Validé par le porteur du projet le 23/11 : `suivi` porte les adhésions, le terme `Adhesion`, l'entrée par le Referent, la sortie par l'Adherent seul.

## Contexte

Aucun BC ne disait qui est Adherent d'une Structure. `suivi` déléguait « l'appartenance technique » à Keycloak, et `mise-en-relation` définissait l'Adherent comme « personne membre d'une Structure » sans moyen de le savoir. La fonctionnalité de bout en bout de S1 en dépend : s'abonner à un service suppose d'être Adherent.

La maquette v0.2 ne tranche pas. Sur les écrans relus (accueil, page de l'asso, abonnements, réglages, suivi), personne n'entre dans une structure ni n'en sort.

## Décision

| Option | Pour | Contre |
|---|---|---|
| **`suivi`** (retenue) | Porte déjà `Structure` et le Referent ; 19 termes sur 30 avant cet ADR | Élargit un BC qui ne faisait qu'écouter, et renforce la boucle avec `mise-en-relation` |
| `mise-en-relation` | Premier consommateur, aucun événement à ajouter | 27 termes sur 30, et déjà la complexité du cœur |
| Un BC dédié | Le découpage le plus net | Une dizaine de termes, pour un plancher de 15 dans la gate `artefacts` ; un quatrième BC pour un POC |
| `identite`, avec les comptes | Compte et appartenance au même endroit | Mélange « qui es-tu ? » et « de quelle Structure fais-tu partie ? » ; règles métier hors des gates |

### `Adhesion` est un agrégat à part

Aucun invariant ne lie les adhésions de deux personnes : rien n'oblige à les charger ensemble. Dans `Structure`, chaque entrée verrouillerait la Structure entière. Séparée, `Adhesion` s'extraira aussi plus facilement si un BC dédié devient nécessaire.

### Règles

- Le Referent de la Structure enregistre l'Adhesion.
- L'Adherent seul y met fin, sans motif. Si le Referent le pouvait, ce serait une exclusion, hors POC selon l'ADR-001.
- Un Adherent a au plus une Adhesion en cours dans une même Structure (INV-SUI-008).
- Une Adhesion terminée n'est jamais rouverte ; revenir crée une nouvelle Adhesion.

### Événements de `suivi` vers `mise-en-relation`

`AdhesionEnregistree` et `AdhesionTerminee`, décrits dans `contexts/context-map.yaml`.

- `mise-en-relation` tient à jour ses `Adherent`, terme déjà à son glossaire. Il n'a aucun terme à ajouter (INV-MER-015, INV-MER-016).
- À la fin d'une Adhesion, l'Abonnement est supprimé et non mis en Pause : la Pause est choisie par l'Adherent seul.
- `rencontre` ne consomme rien : `DemandeAcceptee` lui donne les deux Participants et la Structure.
- Les événements peuvent être reçus plusieurs fois sans effet double.
- Entre un départ et sa réception, une Sollicitation peut encore partir ; l'acceptation est revérifiée.

## Conséquences

- **La mission de `suivi` s'élargit** : il tient les Structures et leurs Adhesions, en plus d'écouter. Son nom reste.
- **`suivi` résout le prénom et l'email**, pour le Referent seulement (ADR-005). Le Referent connaît un email, pas l'identifiant opaque qu'exige une Adhesion.
- **Portée de S1** : enregistrer une Adhesion, publier `AdhesionEnregistree`, la consommer. Trois tâches, puisqu'un agent ne voit qu'un BC : contrat (cette PR), `suivi`, `mise-en-relation`.
- **La fin d'Adhesion vient après S1.** L'événement est déclaré, mais ses deux invariants (jamais rouverte, terminée par l'Adherent seul) ne le sont pas : la gate `invariants` les exigerait dès que la classe `Adhesion` existe. La tâche qui code la fin commence par les ajouter.

## Problèmes découverts, non résolus ici

### La context map actuelle ne peut pas être codée en entier

`ModulesTest` refuse tout cycle entre modules, même par événements ; `ContextMapTest` accepte toute dépendance déclarée. Essai du 23/11, dans une copie jetable :

| Dépendances | Résultat |
|---|---|
| `mise-en-relation` écoute `StructureCreee` de `suivi` | vert |
| et `suivi` écoute `AbonnementMisEnPause` de `mise-en-relation` | **rouge** : `Cycle detected` dans `ModulesTest` |

La boucle entre `mise-en-relation` et `rencontre` a la même forme et devrait échouer aussi (non essayée). S1 n'est pas bloquée tant que `suivi` n'écoute pas `mise-en-relation`.

### `mise-en-relation` ne sait pas qui est le Referent

Il doit l'autoriser à régler le CatalogueDeServices et les ReglesEnvoi, mais `ReferentDesigne` est interne à `suivi`.

## Questions ouvertes

| # | Question | Hypothèse actuelle |
|---|---|---|
| A4 | Plusieurs structures par personne (Q1) ? | Permis par le modèle, une seule à l'écran ; le PlafondHebdomadaire vaut alors par Structure |
| A5 | Une Rencontre en cours survit-elle au départ d'un Participant ? | Oui |
| A6 | Que faire du cycle entre modules ? | Le tolérer si ses deux sens sont dans la context map, par une PR à part, avant le premier écouteur dans `suivi` |
| A8 | Publier `ReferentDesigne` vers `mise-en-relation` ? | Oui, par une tâche contrat, avant l'écran de réglages |
