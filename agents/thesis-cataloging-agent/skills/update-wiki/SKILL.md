# update-wiki

## But

Mettre à jour `/knowledge/` avec des règles vérifiées ou approuvées par un humain.

## Contraintes

- Ne jamais modifier `/raw/`.
- Ne jamais modifier `/dataset/`.
- Règles atomiques, explicites, dédupliquées, en français, avec exemple si possible.
- Journaliser dans `knowledge/log.md`.

## Refus

Si la règle n’est pas vérifiée ou approuvée, ne pas modifier le wiki ; enregistrer seulement une proposition dans `/memory/`.
