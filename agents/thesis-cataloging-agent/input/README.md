# Entrées d'exécution

Ce dossier reçoit les documents fournis par l'utilisateur pendant une exécution normale.

## Contenus acceptés

- Image de page de couverture.
- Texte OCR brut.
- Lot de plusieurs images ou textes OCR.
- Notes complémentaires utiles au catalogage.

## Règles

- Ne pas confondre avec `/dataset/`, qui sert seulement aux tests et à l'évaluation.
- Ne pas confondre avec `/raw/`, qui contient la documentation source.
- Une exécution peut traiter un seul document ou un lot.
- Pour un lot, conserver un identifiant stable par document.

## Convention recommandée

```text
input/
  run-YYYYMMDD-HHMM/
    001-cover.jpg
    001-ocr.txt
    002-cover.jpg
    002-ocr.txt
```
