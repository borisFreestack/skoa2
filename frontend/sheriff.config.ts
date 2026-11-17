import { noDependencies, sameTag, SheriffConfig } from '@softarc/sheriff-core';

// Un module Sheriff par bounded context, comme dans le backend (Spring Modulith).
// Un BC ne dépend d'aucun autre : ils ne se connaissent que par les événements
// de contexts/context-map.yaml, qui passent par le backend. Seul le shell (root) les compose.
export const config: SheriffConfig = {
  modules: {
    'src/app/<bc>': ['bc:<bc>'],
  },
  depRules: {
    root: ['bc:*'],
    'bc:*': [sameTag],
    noTag: noDependencies,
  },
};
