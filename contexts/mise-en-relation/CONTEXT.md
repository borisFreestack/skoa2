# Mise en relation — cœur

## Mission
Faire qu'une Demande d'un Adherent trouve un Preneur proche et disponible, vague après vague, jusqu'au premier oui ou jusqu'à l'Echeance.
Le faire sans jamais sur-solliciter personne, sans pénaliser l'absence de réponse et sans révéler l'identité de quiconque avant l'acceptation.

## Responsabilités
- Recevoir une Demande (Service, LieuDeRencontre, Creneau) et vérifier qu'elle respecte le CatalogueDeServices et le DelaiMinimum.
- Choisir les Sollicites de chaque Vague selon les ReglesEnvoi : les plus proches d'abord, puis les moins sollicités récemment, en excluant les Abonnements en Pause ou au PlafondHebdomadaire.
- Respecter les HeuresCalmes, la TailleDeVague et l'IntervalleEntreVagues.
- Enregistrer l'acceptation du premier Sollicite qui dit oui, arrêter les vagues et publier `DemandeAcceptee`.
- Faire expirer la Demande à l'Echeance ou quand plus aucun Sollicite n'est possible.
- Tenir les Abonnements : services proposés, PointDeReference arrondi, Rayon, PlafondHebdomadaire, Pause.
- Proposer une Pause (jamais l'imposer) après un nombre de SollicitationSansReponse fixé par les ReglesEnvoi.
- Permettre au Referent de paramétrer le CatalogueDeServices et les ReglesEnvoi de sa Structure.

## HORS-PÉRIMÈTRE
- L'identité des personnes (prénom, email, compte) : identifiants opaques uniquement, via l'ACL Keycloak.
- Tout ce qui suit l'acceptation : heure convenue, messages, annulation, désistement, retour. Cela relève de `rencontre`.
- L'envoi technique des emails (infrastructure). Ce BC décide *qui* solliciter et *quand*, pas *comment* on transporte le message.
- Les indicateurs, les éléments à traiter et le Referent en tant que personne à recontacter : cela relève de `suivi`.
- L'identité visuelle de la Structure et ses événements (balades, ateliers).
- Tout diagnostic, toute situation personnelle ou de santé : la Demande ne porte qu'un Service.

## Agrégats
| Agrégat | Racine de cohérence |
|---|---|
| `Demande` | Service, LieuDeRencontre, Creneau, Echeance, Vagues et Sollicitations, statut (EnCours, Acceptee, Expiree, Annulee, Close) |
| `Abonnement` | Services proposés, PointDeReference, Rayon, PlafondHebdomadaire, Pause, compteur de SollicitationSansReponse |
| `CatalogueDeServices` | Services de la Structure, chacun actif ou non, avec son DelaiMinimum |
| `ReglesEnvoi` | TailleDeVague, IntervalleEntreVagues, HeuresCalmes, règle d'Echeance, plafond par défaut, rayon maximum, seuil de pause |

## Événements publiés
| Événement | Consommé par |
|---|---|
| `DemandeEnvoyee` | suivi |
| `DemandeAcceptee` | rencontre, suivi |
| `DemandeExpiree` | suivi |
| `AbonnementEnregistre` | suivi |
| `AbonnementMisEnPause` | suivi |
| `AbonnementRepris` | suivi |
| `PauseProposee` | suivi |

## Événements consommés
| Événement | Émis par | Effet |
|---|---|---|
| `DesistementSignale` | rencontre | la Demande reprend ses vagues ; le Preneur désisté n'est plus sollicité pour elle |
| `RencontreAnnulee` | rencontre | la Demande passe à Close, définitivement |
| `StructureCreee` | suivi | création du CatalogueDeServices et des ReglesEnvoi par défaut |

## Événements internes (non publiés)
`VagueLancee`, `SollicitationEnvoyee`, `SollicitationDeclinee`, `DemandeAnnulee` (annulée avant toute acceptation), `ServiceActive`, `ServiceDesactive`, `ReglesEnvoiModifiees`.
