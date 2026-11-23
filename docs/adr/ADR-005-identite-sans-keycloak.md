# ADR-005 — Identité : un serveur d'autorisation Spring, sans Keycloak

Date : 2026-11-23
Statut : Accepté

Décidé par le porteur du projet le 23/11 : pas de Keycloak, un serveur d'autorisation Spring, une application séparée, les accès à l'annuaire ci-dessous, et la connexion après la première fonctionnalité de S1. Remplace l'ADR-001 pour Keycloak. Les adhésions sont dans l'ADR-004.

## Contexte

L'ADR-001 délègue l'identité et les comptes à Keycloak, traduit par une ACL dans chaque BC. Keycloak rendait deux services :

1. **la connexion** : prouver qui se connecte ;
2. **l'annuaire** : retrouver le prénom ou l'email d'une autre personne. `rencontre` montre le Prenom de l'autre Participant, `suivi` nomme l'AdherentConcerne, et les Sollicitations partent par email.

Sans Keycloak, skoa doit rendre les deux. L'OAuth seul ne couvre que le premier.

## Décision

### Serveur d'autorisation Spring

skoa est son propre fournisseur d'identité, avec `spring-boot-starter-security-oauth2-authorization-server`, fourni par Spring Boot 4.1.2 (Spring Security 7.1.2).

- Le front obtient un jeton par le flux *authorization code* avec PKCE, comme client public.
- Le backend est un serveur de ressources : il vérifie la signature du jeton et n'en lit que `sub`.
- `sub` est l'identifiant opaque, le seul que les BC manipulent.

### Une application séparée

`identite` est un sous-projet Gradle et une application à part, pas un module du monolithe. Essais du 23/11 dans une copie jetable :

| Emplacement | Résultat |
|---|---|
| Module `org.skoa.identite`, non utilisé | **rouge** : `ModulesTest` (exactement trois modules) et `ArchitectureTest` (couches d'un BC) |
| Le même, utilisé par `rencontre` | **rouge** aussi dans `ContextMapTest` |
| Application séparée | tests du backend et gates DDD verts ; l'application démarre, publie sa configuration OpenID, émet un jeton et refuse un scope non accordé |

Les BC gardent la relation déclarée dans la context map : une ACL, sans événement. Seul le système derrière l'ACL change. `identite` reste un sous-domaine générique, remplaçable : le domaine ne connaît que ses ports.

### Comptes et annuaire

`identite` conserve, pour chaque personne : identifiant opaque, prénom, email, mot de passe haché. Rien d'autre : ni Structure, ni Referent, ni Adhesion, qui sont des faits métier.

Chaque BC qui a besoin de l'annuaire est un client distinct, limité à son scope (flux *client credentials*) :

| Consommateur | Scope | Donnée |
|---|---|---|
| `rencontre` | `prenom.lire` | le prénom |
| `suivi` | `contact.lire` | le prénom et l'email, pour le Referent de la Structure, sans les stocker |
| envoi des emails (infrastructure) | `email.lire` | l'email |
| `mise-en-relation` | aucun | identifiant opaque uniquement |

Aucune de ces données n'entre dans un événement. Les mots de passe, secrets de clients et clés de signature ne sont jamais dans le dépôt, qui est public. Les comptes sont fictifs.

### Alternatives écartées

- **Keycloak** : écarté par le porteur du projet. Un système de plus à faire tourner.
- **Client OAuth d'un fournisseur externe** : aucun mot de passe à gérer, mais chaque adhérent doit avoir un compte chez ce fournisseur, et l'annuaire reste à construire.
- **Module du monolithe** : un seul processus, mais trois gates protégées à assouplir.

## Conséquences

- **Coût** : mots de passe oubliés, réinitialisation, blocage des essais répétés et rotation des clés sont à notre charge. Ce travail n'a pas de valeur métier ; il sert l'objectif d'apprentissage de Spring (ADR-002).
- **Deux applications** à lancer, à déployer et à prévisualiser, au lieu d'une.
- **`identite` échappe à la gate `langage`**, qui ne lit que `backend/` et `frontend/` (vérifié avec un terme interdit). Les conventions des BC et PIT ne s'y appliquent pas non plus. À étendre si ce code grossit.
- **Connaître le Referent** : le jeton ne porte pas ce rôle. `suivi` le sait, mais `mise-en-relation` doit aussi le savoir pour autoriser le réglage du CatalogueDeServices et des ReglesEnvoi, et aucun événement ne le lui dit (`ReferentDesigne` est interne). C'est un trou de la context map (A8 de l'ADR-004).
- **S1** : la fonctionnalité de bout en bout se fait avec des identifiants fictifs fixes. `identite` vient ensuite, avant toute preview accessible de l'extérieur.

Les mentions de Keycloak sont retirées de `contexts/` et de `docs/apprentissage.md` avec cet ADR. Le sous-projet sera déclaré dans `settings.gradle.kts` et la CI le moment venu.

`docs/cadrage-poc.md` et `docs/synthese-s0.md` ne changent pas : ce sont des documents figés.

## Questions ouvertes

| # | Question | Hypothèse actuelle |
|---|---|---|
| I1 | Qui crée un compte ? | Le Referent enregistre une personne par son email ; elle choisit ensuite son mot de passe |
| I2 | Où le front garde-t-il le jeton : dans le navigateur, ou dans une session côté serveur ? | Non tranché ; à décider avant d'écrire le front |
| I3 | Que deviennent les données d'un compte supprimé ? | Non traité |
| I4 | `identite` doit-elle passer les mêmes gates que les BC ? | Build et tests oui ; gates de domaine non |
