# Contrats HTTP

Un fichier `openapi.yaml` par bounded context. Chaque fichier est **la source de vérité** de l'API que le BC expose au frontend :

- le backend en génère les interfaces Spring et les DTO (`backend/build/generated/openapi/<bc>`), que ses contrôleurs implémentent ;
- le frontend en génère le client Angular et les modèles TypeScript (`frontend/src/app/<bc>/api`).

Le code généré n'est pas versionné : il est régénéré à chaque build, donc il ne peut pas diverger du contrat. Une dérive casse la compilation, côté backend comme côté frontend.

## Règles

- Ces fichiers sont protégés, comme `contexts/`. Une modification est un changement de contrat : elle passe par une tâche contrat et par la Gate 1.
- Les noms (chemins, schémas, propriétés) n'emploient que les termes du `glossary.yaml` du BC.
- La CI compare le contrat de la PR à celui de la branche de base (oasdiff) et échoue sur un changement cassant.
- Un BC n'expose ici que sa propre API. Les échanges entre BC restent des événements déclarés dans `contexts/context-map.yaml`.
