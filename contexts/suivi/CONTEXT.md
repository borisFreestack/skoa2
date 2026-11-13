# Suivi — support

## Mission
Donner au Referent de chaque Structure de quoi prendre soin des adhérents : savoir qui rappeler, et voir où l'entraide manque de monde.
Il ne décide rien de la mise en relation ni des rencontres : il écoute leurs événements et ne montre que ce qui aide à recontacter une personne ou à lire l'activité en chiffres.

## Responsabilités
- Créer une Structure (NomAffiche, IdentiteVisuelle, Referent, TelephoneDeLaStructure) et publier `StructureCreee`.
- Ouvrir un ElementATraiter quand un Retour exprime un BesoinDEnParler ou qu'une Demande expire, au nom de l'AdherentConcerne seulement.
- Permettre au Referent de marquer un ElementATraiter comme traité par un Rappel.
- Calculer les Indicateurs d'une Structure par Periode : demandes, rencontres faites, demandes expirées, temps moyen avant acceptation, ServiceEnManque, adhérents en pause ou invités à faire une pause.
- Décider si l'ActiviteDeLaStructure est affichée à l'accueil selon le SeuilAffichageActivite.

## HORS-PÉRIMÈTRE
- Le paramétrage du CatalogueDeServices et des ReglesEnvoi : cela relève de `mise-en-relation`, même si l'écran est partagé avec le Referent.
- Le contenu des Messages et le déroulé d'une Rencontre : cela relève de `rencontre`.
- Le signalement d'un adhérent, la suspension, la sanction : hors POC (ADR-001).
- Les événements de la Structure (balades, ateliers) et l'analyse de pratiques : hors POC (ADR-001).
- Les comptes, l'authentification et l'appartenance technique à une Structure : délégués à Keycloak.
- Tout diagnostic, toute situation personnelle ou de santé.

## Agrégats
| Agrégat | Racine de cohérence |
|---|---|
| `Structure` | NomAffiche, IdentiteVisuelle, Referent, TelephoneDeLaStructure, SeuilAffichageActivite |
| `ElementATraiter` | AdherentConcerne, Motif, date d'ouverture, Rappel, statut (AFaire, Rappele) |
| `Indicateurs` | modèle de lecture par Structure et par Periode, reconstruit à partir des événements consommés |

## Événements publiés
| Événement | Consommé par |
|---|---|
| `StructureCreee` | mise-en-relation |

## Événements consommés
| Événement | Émis par | Effet |
|---|---|---|
| `DemandeEnvoyee` | mise-en-relation | Indicateurs (demandes de la Periode) |
| `DemandeAcceptee` | mise-en-relation | Indicateurs (temps moyen avant acceptation) |
| `DemandeExpiree` | mise-en-relation | ElementATraiter (Motif DemandeExpiree) et Indicateurs, ServiceEnManque compris |
| `AbonnementEnregistre` | mise-en-relation | Indicateurs (adhérents qui proposent, par Service) |
| `AbonnementMisEnPause` | mise-en-relation | Indicateurs (adhérents en pause) |
| `AbonnementRepris` | mise-en-relation | Indicateurs (adhérents en pause) |
| `PauseProposee` | mise-en-relation | Indicateurs (adhérents invités à faire une pause) |
| `RetourDonne` | rencontre | ElementATraiter si le Ressenti est BesoinDEnParler |
| `RencontreTerminee` | rencontre | Indicateurs (rencontres faites) et ActiviteDeLaStructure |

## Événements internes (non publiés)
`ElementATraiterOuvert`, `RappelEffectue`, `ReferentDesigne`, `IdentiteModifiee`.
