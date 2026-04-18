# Règles métier

## Langue

- Comprendre le français
- Répondre en français
- Produire les explications en français

## Ordre d'exécution obligatoire

Le pipeline suit strictement l'ordre défini dans le cahier des charges.

## Séparation des couches

- `dataset/` ne doit jamais être modifié par l'agent
- `knowledge/` contient les règles catalographiques en Markdown
- `memory/` stocke les cas passés et corrections

## IdRef

- Interdiction d'halluciner un PPN
- Interdiction de forcer un appariement ambigu

## Sudoc

- Si un doublon est trouvé, arrêter le pipeline
