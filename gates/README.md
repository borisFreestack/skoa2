# Gates DDD

Ces gates vérifient que le code reste fidèle aux artefacts de `contexts/`. Elles tournent en CI sur chaque push et chaque pull request, avec les mêmes règles pour un humain et pour un agent.

```sh
pip install -r gates/requirements.txt              # PyYAML, une seule fois
python3 gates/verifier.py                          # artefacts, langage, invariants
python3 gates/verifier.py langage                  # une seule gate
python3 -m unittest discover -s gates/tests -t gates/tests   # les gates savent-elles échouer ?
./gradlew :backend:test --tests org.skoa.ContextMapTest      # conformité à la context map
```

Chaque constat tient sur une ligne, `chemin:ligne: ERREUR|AVERTISSEMENT [gate] message`. Seules les erreurs font échouer la gate.

## Ce que chaque gate bloque

| Gate | Où | Ce qu'elle bloque |
|---|---|---|
| `artefacts` | `skoa_gates/artefacts.py` | YAML invalide ; glossaire hors de la fourchette de 15 à 30 termes ; terme en double, mal nommé ou interdit partout ; terme qui interdit un autre terme du même glossaire ; agrégat inconnu ; identifiant d'invariant mal formé ou en double ; `CONTEXT.md` dont les événements ou les agrégats divergent de la context map et du glossaire |
| `langage` | `skoa_gates/langage.py` | identifiant Java/TypeScript ou nom de contrat OpenAPI qui contient un terme interdit partout (CLAUDE.md) ou un synonyme refusé du glossaire de son BC |
| `invariants` | `skoa_gates/invariants.py` | agrégat écrit dont un invariant n'est cité par aucun test du BC ; citation d'un invariant inconnu ou d'un autre BC |
| conformité à la context map | `backend/src/test/java/org/skoa/ContextMapTest.java` | dépendance entre BC autre qu'un événement déclaré de l'amont vers l'aval ; type non déclaré dans un paquet `evenements` ; événement qui n'est pas un record ou dont les champs diffèrent du payload |

`artefacts` signale aussi, sans bloquer, un terme défini dans un BC et interdit dans un autre. C'est souvent voulu, mais il vaut mieux le savoir.

## Conventions que le code doit suivre

- **Événements publiés** : un record par événement, nommé comme dans `contexts/context-map.yaml`, dans `org.skoa.<bc>.evenements`. Ce paquet est déclaré `@NamedInterface("evenements")` dans son `package-info.java`. Les composants du record sont exactement les champs du payload. Un événement interne (non publié) vit ailleurs dans le BC.
- **Citer un invariant** : son identifiant figure dans le nom affiché d'un test du BC, par exemple `@DisplayName("INV-MER-005 …")` ou `it('INV-MER-005 …')`. Un commentaire ne compte pas.
- **Un invariant devient exigible** dès qu'une classe, un record, une interface ou un enum porte le nom de son agrégat dans `backend/src/main/java/org/skoa/<bc>/` (ADR-002).

## Sources de vérité

Les gates ne recopient aucune règle :
- la liste des BC et les événements viennent de `contexts/context-map.yaml` ;
- les termes et leurs synonymes refusés viennent de `contexts/<bc>/glossary.yaml` ;
- le vocabulaire interdit partout vient de la section « Vocabulaire interdit partout » de `CLAUDE.md` (les termes entre backquotes de son premier paragraphe).

Les fichiers analysés sont ceux que git suit ou verrait, hors `.gitignore`. Le code généré depuis `contracts/` n'est donc pas analysé ; c'est le contrat lui-même qui l'est.

## Limites connues

- **« Terme absent du glossaire » n'est pas détecté.** La gate de langage repère les mots interdits, pas les mots inventés. Un nom métier nouveau et neutre passe ; c'est à la review de le voir.
- **La règle 1 de CLAUDE.md est vérifiée sur les dépendances, pas sur la lecture.** Rien n'empêche un agent de lire un autre BC tant que l'assemblage du contexte (S2) ne le borne pas.
- **Le singulier est grossier** (s ou x final retiré au-delà de trois lettres) : il suffit pour « Clients », pas pour « Travaux ».
- **Les templates Angular (`.html`) et les messages de commit ne sont pas analysés.**
- **Un agrégat nommé autrement** (`DemandeEntity`) échappe à la gate d'invariants. L'annotation jMolecules `@AggregateRoot`, vérifiée contre les agrégats du glossaire, fermerait ce trou.
- **Le payload d'un événement envoyé à plusieurs BC est une union.** `DemandeAcceptee` porte `lieuDeRencontre` et `creneau` pour `rencontre`, donc `suivi` les reçoit aussi, alors que la context map ne les lui déclare pas.
