# orchestrate-unimarc-generation

## But

Orchestrer le pipeline complet de catalogage UNIMARC pour les deux profils supportés.

## Étapes obligatoires

1. Appeler `retrieve-knowledge`.
2. Appeler `retrieve-memory`.
3. Appeler `classify-profile`. Si profil incertain ou hors périmètre, arrêter en français.
4. Appeler `extract-metadata-json`.
5. Appeler `validate-json-schema`.
6. Appeler la compétence externe `search-records-sudoc` avec les deux phases décrites dans `/knowledge/sudoc/duplicate-check.md`.
7. Si doublon trouvé, arrêter avec le message requis.
8. Appeler la compétence externe `search-authorities-idref`.
9. Appeler `enrich-with-idref`.
10. Appeler `generate-unimarc-xml`.
11. Appeler `validate-unimarc`.
12. Export facultatif seulement : `convert-records-unimarc`.
13. Si correction, échec ou ambiguïté : `self-improve`, puis `update-wiki` uniquement après approbation.

## Sorties

- JSON validé.
- Rapport Sudoc/IdRef.
- UNIMARC/XML validé ou arrêt justifié.
