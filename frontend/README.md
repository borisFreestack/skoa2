# Frontend skoa

Angular 22, Node 24 (`nvm use` à la racine du repo).

```bash
npm ci
npm start        # serveur de dev
npm run lint     # ESLint + frontières Sheriff
npm test         # Vitest
npm run build    # build de production
```

Chaque commande régénère d'abord les clients depuis `../contracts/` (`npm run contrats`).

## Organisation

- `src/app/<bc>/` : un module Sheriff par bounded context (`mise-en-relation`, `rencontre`, `suivi`).
  - `index.ts` est son API publique : un import profond est refusé par le lint.
  - Un BC n'importe aucun autre BC. Seul le shell (`src/app/app.*`) les compose.
- `src/app/<bc>/api/` : client et modèles générés par ng-openapi-gen depuis `contracts/<bc>/openapi.yaml`. Non versionné, jamais modifié à la main.

## Styles en CSS, pas en SCSS

Angular compile le SCSS avec `sass-embedded`, dont la VM Dart exige macOS 14. Les styles sont donc en CSS (imbrication et variables CSS natives), ce qui garde le build utilisable sur des macOS plus anciens.
