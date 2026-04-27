# Sorties d'exécution

Ce dossier reçoit les artefacts produits pendant une exécution normale.

## Sorties attendues

Pour chaque document traité :

- métadonnées JSON extraites et validées ;
- rapport de vérification Sudoc ;
- rapport d'alignement IdRef ;
- notice UNIMARC/XML ;
- rapport d'incertitudes et de règles `/knowledge/` utilisées.

## Règles

- Ne pas écrire les sorties normales dans `/examples/`.
- Ne pas écrire les sorties normales dans `/dataset/`.
- Ne pas utiliser `/output/` comme source de vérité documentaire.
- Pour un lot, produire une sortie séparée par document.

## Convention recommandée

```text
output/
  run-YYYYMMDD-HHMM/
    001-metadata.json
    001-sudoc-check.md
    001-idref-alignment.md
    001-record.xml
    001-report.md
    002-metadata.json
    002-sudoc-check.md
    002-idref-alignment.md
    002-record.xml
    002-report.md
```
