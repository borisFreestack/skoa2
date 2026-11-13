# Rencontre — cœur

## Mission
Faire vivre en confiance la Rencontre née d'une Demande acceptée : convenir d'une heure, s'écrire, se retrouver, puis donner un Retour sans note.
Chaque Participant peut s'en retirer à tout moment sans se justifier, et ce qu'il confie dans son Retour n'est jamais montré à l'autre.

## Responsabilités
- Ouvrir une Rencontre à la réception de `DemandeAcceptee`, avec ses deux Participants : le Demandeur et le Preneur.
- Révéler le Prenom de chaque Participant à l'autre, et seulement à lui (traduction de l'identité Keycloak par l'ACL).
- Gérer les PropositionDHeure dans le Creneau de la Demande jusqu'à une HeureConvenue.
- Porter les Messages entre les deux Participants.
- Enregistrer une Annulation (par le Demandeur) ou un Desistement (par le Preneur), sans motif obligatoire.
- Recueillir le Retour de chaque Participant après l'HeureConvenue : Ressenti et Presence.
- Afficher le TelephoneDeLaStructure comme recours pendant la Rencontre.

## HORS-PÉRIMÈTRE
- Le choix du Preneur, les vagues, les Abonnements et les Sollicitations : cela relève de `mise-en-relation`.
- Le rappel d'un Participant qui a exprimé un BesoinDEnParler, et les indicateurs : cela relève de `suivi`. Ce BC publie le Retour et ne décide rien de sa suite.
- Toute note, étoile, avis public ou classement de Participant.
- Tout diagnostic, toute situation personnelle ou de santé.
- L'envoi technique des notifications et des emails (infrastructure).
- Les numéros d'urgence (3114, 15) : contenu statique d'interface, pas un objet du domaine.

## Agrégats
| Agrégat | Racine de cohérence |
|---|---|
| `Rencontre` | Participants (Demandeur, Preneur), Service, LieuDeRencontre, Creneau, PropositionDHeure, HeureConvenue, Messages, Retours, statut (Ouverte, Convenue, Annulee, Desistee, Terminee) |

## Événements publiés
| Événement | Consommé par |
|---|---|
| `DesistementSignale` | mise-en-relation |
| `RencontreAnnulee` | mise-en-relation |
| `RetourDonne` | suivi |
| `RencontreTerminee` | suivi |

## Événements consommés
| Événement | Émis par | Effet |
|---|---|---|
| `DemandeAcceptee` | mise-en-relation | ouverture d'une Rencontre entre le Demandeur et le Preneur |

## Événements internes (non publiés)
`RencontreOuverte`, `HeureProposee`, `HeureConvenue`, `MessageEnvoye`.
