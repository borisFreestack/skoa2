# ADR-003 — Agent reviewer : Devstral via l'API Mistral, en commentaires non bloquants

Date : 2026-11-17
Statut : Proposé

## Contexte

Le cadrage prévoit en S2 un agent reviewer « avec la grille DDD/ADR, commentaires dans la PR ». Il fixe ce que le reviewer voit (diff, glossaire, ADR, règles d'archi) et ce qu'il ne voit pas (l'historique de l'agent code). Il ne dit ni quel modèle le fait tourner, ni où il tourne, ni si son verdict bloque le merge.

Le reste de la boucle repose sur Claude : l'orchestrateur est prévu sur le Claude Agent SDK, et les agents tests et code sont des agents Claude. Un reviewer du même modèle partage les angles morts de l'agent qu'il relit. Il risque de trouver correct ce que l'agent code a trouvé correct, pour les mêmes raisons. Le cadrage nomme déjà ce risque pour le raisonnement (« ne pas lui donner le raisonnement de l'agent code évite qu'il valide un diff parce que l'explication était convaincante »). Le choix du modèle est le même risque, à un autre niveau.

La règle 2 d'arbitrage de l'ADR-002 n'admet un outil dans la chaîne que s'il répond à un risque nommé ou à un apprentissage explicite. Ici, il répond aux deux :
- **risque** : « l'agent contourne les gates » (cadrage, section Risques). Les gates déterministes voient la forme : un terme interdit, un import, un invariant sans test. Elles ne voient pas le sens : un terme du glossaire employé à contresens, un test qui cite un invariant sans le prouver ;
- **apprentissage** : ce que change un reviewer d'une autre famille de modèles, en coût, en bruit et en défauts trouvés.

## Décision

### Modèle et hébergement

Le reviewer tourne sur **Devstral**, le modèle de code de Mistral, appelé par **l'API de La Plateforme Mistral** depuis GitHub Actions. La version du modèle est épinglée dans le workflow. On n'utilise pas l'alias « latest », pour la raison donnée dans le journal (« une gate n'est fiable que si son environnement est figé »).

La clé est un secret de dépôt `MISTRAL_API_KEY`. Elle n'apparaît ni dans le code, ni dans les logs.

### Sortie de données

C'est la décision explicite qu'exige l'entrée du journal « Confidentialité des outils de la chaîne » : **le diff des PR et les fichiers de `contexts/` partent vers Mistral.** C'est acceptable parce que les données du dépôt sont fictives (règle « Données » de `CLAUDE.md`) et que le dépôt est destiné à devenir public. Avant le premier appel, on vérifie dans La Plateforme le réglage de réutilisation des données pour l'entraînement, et on le note dans le journal.

### Ce que le reviewer voit

| Voit | Ne voit pas |
| --- | --- |
| le diff de la PR | la description de la PR et les messages de commit, qui portent le raisonnement de l'agent code |
| la spec validée en Gate 1 (commentaire d'issue) | l'historique et les itérations de l'agent code |
| `CONTEXT.md`, `glossary.yaml` et `invariants.yaml` des BC touchés par le diff | les fichiers des BC que le diff ne touche pas |
| `contexts/context-map.yaml`, les ADR, les règles de `CLAUDE.md` | `docs/journal-sdlc.md` (question O3 de l'ADR-002, toujours ouverte) |
| les rapports des gates déterministes de la PR | |

Il reçoit les rapports des gates pour ne pas refaire leur travail. Sa grille porte sur ce qu'un script ne voit pas :
1. vocabulaire : un terme du glossaire est-il employé avec sa définition ? Un terme métier absent du glossaire mais neutre, que la gate de langage laisse passer, est-il employé sans proposition d'ajout (règle 3 de `CLAUDE.md`) ?
2. invariants : le test qui cite un invariant le prouve-t-il vraiment, ou se contente-t-il de le nommer ?
3. frontières : le diff fait-il passer une information entre BC autrement que par un événement de la context map, par exemple une donnée copiée ou un identifiant interprété ?
4. affaiblissement : une assertion vidée, un cas retiré, un `@Disabled`, même dans un fichier non protégé ;
5. conformité à la spec : chaque critère d'acceptation est-il couvert ?

### Rôle dans la PR

Le reviewer est **consultatif**. Il publie une review GitHub avec des commentaires ancrés aux lignes et un verdict (`approuve`, `changements demandés`). Son job ne fait jamais échouer la PR. La Gate 2 reste une décision humaine.

Le verdict peut devenir bloquant plus tard, par un nouvel ADR, quand le journal aura de quoi en juger : nombre de PR relues, part de commentaires utiles et de faux positifs, défauts trouvés que les gates n'avaient pas vus.

### Alternatives écartées

- **Claude en reviewer** : même famille de modèles que l'agent code, donc des angles morts corrélés. C'est justement ce que cet ADR veut mesurer.
- **Devstral via OpenRouter** : plus simple pour changer de modèle, mais un intermédiaire de plus par lequel passent les données, sans besoin actuel.
- **Devstral Small en local avec Ollama** : rien ne sort du poste. Mais le modèle tient mal dans les 16 Go du poste et ne tourne pas sur un runner GitHub. La review ne serait donc pas faite en CI, alors que « toute PR, humaine ou agent, passe les mêmes gates ».
- **Verdict bloquant d'emblée** : on ne connaît pas encore le taux de faux positifs. Un reviewer qui bloque à tort renvoie l'agent code itérer pour rien et lui fait consommer ses trois itérations.

## Conséquences

- **Écart au cadrage, à noter dans le journal** : la boucle n'est plus mono-fournisseur. L'orchestrateur et les agents tests et code restent sur Claude ; le reviewer est sur Mistral.
- **Expérience A/B de S3** : « même modèle » s'applique à l'agent code. Le reviewer reste identique en configurations A et B. Il fait partie des gates, pas de la variable mesurée.
- **Traces** : chaque review produit les mêmes traces que les autres agents (tokens, coût, durée, verdict) pour les mesures de S3.
- **Un canal de sortie de plus** : tout ajout au contexte du reviewer (par exemple le journal, si O3 est tranchée par oui) part aussi chez Mistral et repasse par cette section.
- **Le reviewer emploie le vocabulaire du domaine** : ses commentaires sont soumis aux mêmes termes interdits que le reste. Une dérive de sa part est une friction à consigner, pas à filtrer en silence.
- **Une PR venue d'un fork ne reçoit pas la review**, faute d'accès au secret. Sans effet tant qu'un seul humain contribue.

## Questions ouvertes

| # | Question | Hypothèse actuelle |
|---|---|---|
| R1 | Quelle variante de Devstral, et dans quelle version épinglée ? | La plus capable disponible sur La Plateforme au moment de l'implémentation, choisie sur un essai de quelques PR |
| R2 | Le reviewer tourne-t-il dès S1, sur les PR écrites à la main, ou seulement en S2 avec la boucle ? | Dès qu'il est implémenté : les PR humaines donnent une base de comparaison |
| R3 | Format de sortie : review GitHub avec commentaires ancrés, ou un seul commentaire récapitulatif ? | Review ancrée, à partir d'une sortie JSON structurée que le script valide avant de la publier |
| R4 | Faut-il un budget de tokens par review ? | Oui, comme pour les autres agents (cadrage, risque « agent qui boucle ») ; on fixe le plafond après les premiers essais |
