# POC Spec-to-Prod — Pair Aidants

Nov 12, 2026 · @Boris

## Objectif et livrables

Une issue écrite par un humain arrive en production sans qu'un humain touche au code, sauf à deux gates explicites. Chaque agent travaille dans le périmètre d'un seul bounded context, avec son ubiquitous language et la context map comme seul contexte.

Le projet support est **Pair Aidants** (Angular + Java), sur environ 3 semaines plus une semaine de modélisation.

Livrables montrables :

- un repo public avec la boucle complète et les artefacts DDD versionnés ;
- un pipeline CI/CD qui tourne : gates déterministes, preview par PR, déploiement, rollback ;
- un tableau de métriques comparant contexte complet et contexte borné au BC ;
- une démo enregistrée de 5 minutes et un README qui raconte les choix d'architecture.

Ce que ça prouve en entretien : la maîtrise de la CI/CD, de l'orchestration d'agents, et du context engineering adossé au design stratégique DDD.

## Domaine Pair Aidants

Le POC couvre 3 bounded contexts : Mise en relation et Échange (le cœur du produit) et Modération (support, où les associations jouent un rôle). Coaching, crédits entreprise et partenariats restent hors POC, car ils sont surtout de la monétisation et ajoutent peu à la démonstration.

&#91;embedded content: context map Pair Aidants · 3 BC dans le POC, 3 hors POC\]

Les BC ne communiquent que par événements publiés : aucun appel direct dans l'interne d'un autre. L'identité et les comptes sont un sous-domaine générique, délégué à Keycloak et non modélisé.

| BC | Type | Responsabilité | Termes clés |
| --- | --- | --- | --- |
| Mise en relation | cœur | rendre trouvable un pair aidant pour une situation, gérer la demande jusqu'à l'acceptation | PairAidant, PersonneAccompagnee, SituationVecue, DemandeDeMiseEnRelation |
| Échange | cœur | faire vivre la relation acceptée : messages, rendez-vous, clôture | Echange, Message, RendezVous |
| Modération | support | traiter les signalements, suspendre, déléguer aux modérateurs d'une association | Signalement, Suspension, ModerateurAssociatif |

À valider en S0 : le découpage est une proposition issue de ta description du produit, pas d'un event storming.

## Artefacts de contexte

Chaque BC a un dossier de contexte versionné avec le code, lisible par la machine et vérifié par la CI. Un document que rien ne contrôle dérive, et l'agent travaille alors sur un contexte faux.

```text
contexts/
  context-map.yaml              # BC, relations, contrats publiés, BC en aval
  mise-en-relation/
    CONTEXT.md                  # mission, responsabilités, hors-périmètre explicite
    glossary.yaml               # termes, définitions, synonymes interdits
    invariants.yaml             # règles métier, chacune liée à au moins un test
    decisions/                  # ADR locales
backend/                        # Spring Boot + Spring Modulith : 1 module = 1 BC
  src/main/java/.../miseenrelation/   # api/ = ports publiés, internal/ = invisible aux autres
frontend/                       # Angular, 1 lib par BC, frontières par tags lint
  libs/mise-en-relation/
```

Exemple de `glossary.yaml` :

```yaml
context: mise-en-relation
terms:
  - term: PairAidant
    definition: Personne ayant vécu une situation et qui propose d'accompagner un pair.
    forbidden: [Benevole, Aidant, Coach]
  - term: PersonneAccompagnee
    definition: Personne qui cherche le soutien d'un pair pour une situation qu'elle vit.
    forbidden: [Patient, Client, Beneficiaire]
  - term: SituationVecue
    definition: Expérience nommée (phobie scolaire, burn-out...) qui fonde l'appariement.
```

Le choix de vocabulaire n'est pas cosmétique ici : interdire `Patient` empêche l'agent de glisser vers un modèle médical que le produit refuse, et `Coach` appartient à un autre BC.

Outillage Java/Angular, côté vérification :

- **Spring Modulith** : `ApplicationModules.verify()` fait échouer le build si un module touche l'interne d'un autre ; il génère aussi la documentation des modules, à confronter à `context-map.yaml`.
- **jMolecules** : annotations DDD (`@AggregateRoot`, `@ValueObject`) que l'agent doit poser et que la CI vérifie.
- **ArchUnit** : règles hexagonales (le domaine ne dépend ni de Spring ni des adapters).
- **Angular** : une lib par BC avec tags, et une règle de frontières (Nx `enforce-module-boundaries` ou Sheriff) qui interdit l'import d'une lib d'un autre BC hors de son API publique.

## La boucle d'agents

Chaque agent reçoit un contexte assemblé par l'orchestrateur, jamais le repo entier. Toi, tu tiens les deux décisions qui engagent : ce qui doit être construit (spec et vocabulaire) et ce qui part en production (merge).

&#91;embedded content: boucle d'agents · de l'issue au déploiement, 2 gates humaines\]

Une issue inter-BC est découpée par le planner en une sous-tâche par BC, plus une tâche contrat si un événement ou une API publiés changent. La tâche contrat passe en premier et repasse par la Gate 1.

| Agent | Voit | Ne voit pas | Produit |
| --- | --- | --- | --- |
| Planner | `context-map.yaml`, les `CONTEXT.md`, l'issue | le code, les glossaires détaillés | BC ciblés, spec avec critères d'acceptation, termes à ajouter au glossaire |
| Agent tests | spec validée, glossaire et invariants du BC, ports du BC | l'implémentation, les autres BC | tests de comportement aux ports, qui doivent échouer |
| Agent code | spec, tests (lecture seule), code du BC, ports amont déclarés dans la context map | l'interne des autres BC | implémentation dans un worktree, PR |
| Agent reviewer | diff, glossaire, ADR, règles d'archi | l'historique de l'agent code | commentaires de review, verdict |

Remarque sur l'agent reviewer : ne pas lui donner le raisonnement de l'agent code évite qu'il valide un diff parce que l'explication était convaincante.

## Gates CI/CD

Toute PR, humaine ou agent, passe les mêmes gates dans GitHub Actions. Un échec renvoie le rapport à l'agent du BC, au plus 3 itérations, puis l'issue repasse à un humain.

| Gate | Outil | Ce qu'elle bloque |
| --- | --- | --- |
| Build + tests backend | `mvn verify`, JUnit 5, Testcontainers | régression, test cassé |
| Tests écrits d'abord | les nouveaux tests rejoués sur la branche de base | un test qui passe déjà sans le code, donc qui ne teste rien |
| Qualité réelle des tests | PIT (mutation testing) sur le BC modifié | tests complaisants écrits par l'agent |
| Frontières de BC | Spring Modulith `verify()`, ArchUnit, lint de frontières Angular | import dans l'interne d'un autre BC, domaine dépendant de Spring |
| Conformité à la context map | script : dépendances réelles vs `context-map.yaml` | relation entre BC non déclarée |
| Ubiquitous language | script sur le diff : synonymes interdits, termes absents du glossaire | dérive de vocabulaire, terme métier non validé |
| Invariants couverts | script : chaque invariant référencé par au moins un test | règle métier sans preuve |
| Contrat publié | diff OpenAPI (et events) entre base et PR | changement cassant non signalé aux BC en aval |
| Fichiers protégés | CODEOWNERS + check de chemins | modification par l'agent des tests validés, des gates, du glossaire |
| Frontend | `ng lint`, `ng test`, build prod | erreurs Angular |
| Image | Jib (backend), build Docker (frontend), scan Trivy | image non construite ou vulnérable |
| Preview | namespace Kubernetes par PR (Helm), e2e Playwright | parcours utilisateur cassé |
| Déploiement | Helm upgrade, readiness et health checks, `helm rollback` automatique | prod dégradée après merge |

Le cluster de preview peut être un k3d dans le runner pour démarrer, puis un cluster managé (Scaleway Kapsule par exemple) quand la boucle tourne. C'est aussi l'endroit où la montée en compétence Kubernetes se fait en conditions réelles.

## Mesures et expérience comparative

L'hypothèse à tester : un contexte borné au BC donne plus de PR vertes, moins de tokens et moins de violations qu'un accès au repo entier. On la vérifie, on ne la suppose pas.

Protocole :

1. Constituer un jeu de 15 à 20 issues réelles du backlog Pair Aidants, de difficulté variée : intra-BC simple, intra-BC avec invariant, inter-BC avec changement de contrat.
2. Lancer chaque issue dans deux configurations, même modèle et mêmes gates : **A** accès au repo complet avec le CLAUDE.md global, **B** contexte borné au BC (dossier `contexts/<bc>`, code du BC, ports amont).
3. Répéter 3 fois chaque couple, les agents n'étant pas déterministes.

Ce qui est tracé pour chaque run :

| Métrique | Source |
| --- | --- |
| PR verte sans intervention (oui/non) | statut CI |
| Itérations avant le vert | logs de l'orchestrateur |
| Tokens et coût en euros | sortie JSON de claude -p (tokens, coût estimé) |
| Durée issue → PR verte | horodatages |
| Violations par gate (frontières, UL, contrat, mutation) | rapports CI |
| Gate humaine refusée, et pourquoi | ta décision, notée dans la PR |

Le résultat s'affiche dans un tableau de bord par configuration et par type d'issue. C'est la pièce à montrer en entretien, y compris si l'hypothèse est démentie sur certains cas : savoir dire où le contexte borné échoue vaut autant que le résultat positif.

## Backlog

L'ordre est volontaire : le domaine d'abord, puis la CI/CD sans agents, puis les agents. Chaque semaine se termine sur quelque chose de montrable.

**S0 — Modélisation (Pair Aidants)**

- [ ] Event storming léger en solo : événements métier du parcours « je cherche un pair » → « un échange a lieu »
- [ ] Trancher les 3 BC du POC et leurs relations, écrire `context-map.yaml`
- [ ] `CONTEXT.md`, glossaire (15 à 30 termes) et invariants pour chaque BC
- [ ] ADR-001 : périmètre du POC et BC laissés hors POC

**S1 — Walking skeleton + CI/CD, sans agent**

- [ ] Squelette Spring Boot + Spring Modulith (1 module par BC) et Angular (1 lib par BC)
- [ ] Une fonctionnalité de bout en bout codée à la main : déclarer une situation vécue et être proposé comme pair aidant
- [ ] GitHub Actions : build, tests, Modulith/ArchUnit, lint Angular, PIT
- [ ] Scripts de gates DDD : conformité context map, lint UL, couverture des invariants
- [ ] Images (Jib, Docker), preview Helm sur k3d, e2e Playwright, déploiement et rollback

**S2 — La boucle d'agents**

- [ ] Orchestrateur (Claude Agent SDK) : routage planner → agent de BC, assemblage du contexte borné
- [ ] Gate 1 : la spec et les ajouts de glossaire arrivent en commentaire d'issue, tu valides par label
- [ ] Agent tests puis agent code dans un worktree, fichiers protégés, 3 itérations max
- [ ] Agent reviewer avec la grille DDD/ADR, commentaires dans la PR
- [ ] Découpage des issues inter-BC en sous-tâches avec tâche contrat

**S3 — Mesure et démo**

- [ ] Traces par run (tokens, coût, itérations, gate en échec) vers un stockage simple
- [ ] Expérience A/B sur 15 à 20 issues, 3 runs chacune
- [ ] Tableau de bord des résultats
- [ ] README d'architecture, démo enregistrée de 5 minutes, post LinkedIn de retour d'expérience

## Risques et décisions ouvertes

| Risque | Parade |
| --- | --- |
| Trop de cérémonie DDD, le POC n'avance pas | 3 BC maximum, glossaire de 30 termes au plus, S0 limitée à une semaine |
| Artefacts de contexte qui dérivent du code | tout artefact a une gate ; sinon il sort du contexte de l'agent |
| L'agent contourne les gates (tests modifiés, assertions vidées) | fichiers protégés, tests rejoués sur la base, mutation testing |
| Agent qui boucle et brûle des tokens | 3 itérations max, budget de tokens par issue, arrêt avec rapport |
| Données sensibles (situations personnelles, santé) | uniquement des données fictives dans le POC, rien de réel en preview |
| Kubernetes ralentit S1 | k3d dans le runner d'abord, cluster managé seulement en S3 |

Décisions à prendre :

- [ ] Orchestrateur : Claude Agent SDK en Java ou TypeScript, ou Claude Code lancé en mode headless par la CI
- [ ] Facturation des agents : décidé, abonnement Max via CLAUDE\_CODE\_OAUTH\_TOKEN (crédit Agent SDK mensuel) ; déclenchement des agents réservé à ton compte
- [ ] Hébergement du repo et visibilité : public dès le départ ou à la fin
- [ ] Les 3 BC du POC : confirmer ou ajuster la proposition de la section Domaine
- [ ] Angular : Nx ou workspace Angular simple avec Sheriff pour les frontières