# ADR-001 — Périmètre du POC : trois bounded contexts issus de la maquette v0.2

Date : 2026-11-13
Statut : Accepté

## Contexte

Le POC doit démontrer une boucle d'agents spec → prod où chaque agent ne voit que le contexte d'un seul bounded context. La qualité des frontières et du langage conditionne donc toute la suite.

Le cadrage initial (`docs/cadrage-poc.md`, 12/11/2026) proposait un produit « Pair Aidants » et trois BC : Mise en relation, Échange (cœurs) et Modération (support). Les personnes y étaient appariées sur une situation vécue (phobie scolaire, burn-out). Ce découpage n'était pas issu d'un event storming.

L'event storming de la session S0 a fait apparaître trois faits qui le remettent en cause :

1. **Le vocabulaire « pair-aidant » est refusé.** Il renvoie à une pratique trop encadrée. Le produit s'appelle **skoa**, et le domaine ne parle jamais de pair-aidance.
2. **La maquette fait foi.** La maquette « Coups de main entre adhérents » v0.2 (https://claude.ai/artifact/5U58G3tFfHH3i83KAECtTz, 27/10/2026) est la référence produit. Elle décrit un autre domaine que le cadrage :
   - des adhérents d'une **structure** s'entraident à partir d'une **liste fermée de services** (transports, papiers, rendez-vous, café) ;
   - aucun diagnostic n'est demandé ;
   - l'envoi se fait par **vagues** et s'arrête au premier oui ;
   - l'anonymat est total jusqu'à l'acceptation ;
   - le retour se fait sans note ;
   - un **référent** recontacte les personnes qui en ont besoin.
3. **La maquette ne prévoit ni signalement ni suspension.** La sécurité repose sur le référent, le retour « J'aimerais en parler » et le recours au téléphone de la structure.

Les réponses de l'interview qui contredisaient la maquette ont été abandonnées : appariement sur situation vécue, pair validé par une association, plusieurs échanges par demande, dialogue avant acceptation, modération par signalement.

## Décision

Le POC couvre trois bounded contexts, décrits dans `contexts/` et reliés uniquement par les événements déclarés dans `contexts/context-map.yaml` :

| BC | Type | Mission |
|---|---|---|
| `mise-en-relation` | cœur | Faire qu'une Demande trouve un Preneur par vagues, sans sur-solliciter ni exposer personne |
| `rencontre` | cœur | Faire vivre la Rencontre acceptée (heure, messages, annulation, désistement) jusqu'au Retour sans note |
| `suivi` | support | Donner au Referent les éléments à traiter et les indicateurs de sa Structure |

L'identité et les comptes forment un sous-domaine générique, délégué à Keycloak et traduit par une ACL dans chaque BC.

Décisions de langage :
- « coup de main » est un mot d'interface ; le domaine dit **Demande** (ce qu'on envoie), **Rencontre** (l'aide acceptée) et **Abonnement** (ce qu'un adhérent propose) ;
- « rendez-vous » ne désigne qu'un Service ;
- sont interdits partout : Patient, Client, Beneficiaire, Utilisateur, PairAidant, PairAidance, Aidant, Benevole.

Décisions de règles :
- **Messages :** les Messages d'une Rencontre peuvent être stockés. La mention « aucun contenu d'échange n'est enregistré » de la maquette n'est pas une règle métier.
- **Désistement :** un désistement relance les vagues sur la même Demande.

**Hors POC :**
- les événements de la structure (balades, ateliers, « y aller avec quelqu'un ») ;
- l'analyse de pratiques ;
- le signalement et la suspension d'un adhérent ;
- les crédits entreprise, le coaching et les partenariats du cadrage ;
- l'envoi technique des emails (infrastructure) ;
- l'authentification (Keycloak).

**Dans le POC :** plusieurs structures (tout est cloisonné par Structure) et l'identité visuelle de la structure.

## Conséquences

- **Le cadrage n'est pas réécrit.** Pour le domaine, cet ADR et `contexts/` priment sur `docs/cadrage-poc.md` : noms de BC, termes clés, exemple de glossaire et fonctionnalité de bout en bout de S1. La fonctionnalité de S1 devient : « s'abonner à un service et recevoir une sollicitation pour une demande proche ».
- **Modération disparaît au profit de Suivi.** Il n'existe aucun modèle de sanction. Si un signalement devient nécessaire, il fera l'objet d'un nouvel ADR, et probablement d'un BC dédié.
- **Mise en relation concentre la complexité du cœur.** On y trouve le choix des sollicités, l'équité, les heures calmes et l'arrêt au premier oui. C'est là que la mutation testing et la couverture des invariants comptent le plus.
- **Mise en relation et Rencontre ont une relation bidirectionnelle.** `DemandeAcceptee` va dans un sens, `DesistementSignale` et `RencontreAnnulee` dans l'autre. C'est un point de couplage à surveiller : un changement de contrat d'un côté impose une tâche contrat de l'autre.
- **Le paramétrage est réparti entre deux BC.** L'écran « Réglages de la structure » de la maquette relève de `mise-en-relation` (services, règles d'envoi, limites) et de `suivi` (identité, référent, téléphone, seuil d'affichage). Le frontend le compose à partir des deux.
- **La maquette contient encore des écarts de vocabulaire** : « Confirmé, côté aidant », « Tu accompagnes ». Ils sont à corriger dans la maquette et ne doivent pas être repris dans le code.
