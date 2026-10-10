## REMOVED Requirements

### Requirement: Concept list renders from the lightweight index
**Reason**: The legacy concept list fetched `data/concepts-index.json`; that file and the `concept-cards.js` view are deleted with `data/`.
**Migration**: The vault-native website loads `indexes/concepts.json` lazily as specified by `vault-native-review-web` ("Load vault-native publication data lazily").

### Requirement: Concept detail is lazy-loaded and cached
**Reason**: Concept detail was fetched from `data/concepts/<slug>.json`, which is retired.
**Migration**: Concept detail is served from `records/concept/<id>.json` plus the raw note through `js/content-store.js`, covered by `vault-native-review-web`.
