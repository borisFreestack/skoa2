# skoa — règles pour les agents

skoa est une plateforme d'entraide entre adhérents d'une structure : un adhérent demande un coup de main (transports, papiers, rendez-vous, café), d'autres adhérents proches le reçoivent par vagues, et le premier qui dit oui le rencontre.
Le domaine est découpé en bounded contexts décrits dans `contexts/`. Le périmètre et ses raisons sont dans `docs/adr/ADR-001-perimetre-poc.md`, qui prime sur `docs/cadrage-poc.md` pour tout ce qui touche au domaine.

## Ton contexte

Chaque tâche t'assigne **un seul** bounded context (BC) : `mise-en-relation`, `rencontre` ou `suivi`. Ton contexte se compose de :
- `contexts/<bc>/CONTEXT.md` : mission, responsabilités, hors-périmètre, agrégats, événements ;
- `contexts/<bc>/glossary.yaml` : le seul vocabulaire métier autorisé ;
- `contexts/<bc>/invariants.yaml` : les règles que ton code doit garantir et tes tests prouver ;
- `contexts/context-map.yaml` : les seuls événements que ton BC peut publier ou consommer.

## Règles (non négociables)

1. **Ne lis ni ne modifie jamais le code d'un autre BC que celui qui t'est assigné.** Tu ne connais les autres BC que par les événements que `contexts/context-map.yaml` déclare pour ton BC.
2. **N'emploie que les termes du `glossary.yaml` de ton BC**, dans le code (classes, méthodes, variables, tests), les messages de commit et les specs. Un terme listé dans `forbidden` ne doit jamais apparaître.
3. **Un nouveau terme métier est une proposition d'ajout, jamais un usage direct.** Décris-le (term, definition, forbidden, aggregate) dans la PR ou l'issue et attends sa validation humaine avant de l'employer.
4. **Les tests validés et tous les fichiers de `contexts/` sont en lecture seule.** Si un test ou un invariant te paraît faux, signale-le ; ne le modifie pas, ne l'affaiblis pas, ne le désactive pas.
5. **La communication entre BC passe uniquement par les événements déclarés dans `contexts/context-map.yaml`.** Aucun appel direct, aucun import de l'interne d'un autre BC, aucune table partagée. Un événement nouveau ou modifié est un changement de contrat : il passe par une tâche contrat et par la Gate 1.

## Vocabulaire interdit partout

`Patient`, `Client`, `Beneficiaire`, `Utilisateur`, `PairAidant`, `PairAidance`, `Aidant`, `Benevole`.
Le domaine n'emploie ni vocabulaire médical, ni vocabulaire commercial, ni « utilisateur » pour désigner une personne. « Coup de main » est un mot d'interface : dans le domaine, on dit Demande, Rencontre ou Abonnement.

## Données

Uniquement des données fictives. Aucune donnée de santé, aucun diagnostic, aucune situation personnelle réelle, nulle part : ni dans le code, ni dans les tests, ni dans les fixtures, ni dans les environnements de preview.
