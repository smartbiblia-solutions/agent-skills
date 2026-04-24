# Agent de catalogage UNIMARC — thèses et mémoires imprimés

Dépôt GitAgent-compatible pour un agent AgentDesk/Nanobot/OpenClaw de catalogage en français.

## Périmètre

- `these_originale_imprimee`
- `memoire_original_imprime`

Tout autre document déclenche une revue humaine.

## Utilisation

L’agent suit le pipeline défini dans `AGENTS.md` et s’appuie sur les compétences internes dans `/skills/`. Les compétences externes sont déclarées mais non vendorizées.

## Sorties d’exemple

- `examples/example-metadata.json`
- `examples/example-these-originale-imprimee.xml`
- `examples/example-memoire-original-imprime.xml`

## Maintenance documentaire

Voir `workflows/bootstrap-abes-unimarc.md`.
