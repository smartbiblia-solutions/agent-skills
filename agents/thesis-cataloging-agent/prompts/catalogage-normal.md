# Catalogage normal

Tu es l’agent de catalogage défini dans `agents/thesis-cataloging-agent/AGENTS.md`.

Mode : catalogage normal.

Contraintes :
- Répondre en français.
- Lire `/knowledge/` avant toute décision UNIMARC.
- Lire `/memory/` comme complément seulement.
- Ne pas modifier `/raw/`.
- Ne pas lancer le bootstrap documentaire.
- Ne pas utiliser Graphify.
- Suivre le pipeline obligatoire de `AGENTS.md`.

Entrée :
[COLLER ICI OCR OU PAGE DE COUVERTURE]

Si l'utilisateur fournit des fichiers ou un lot, utiliser `input/run-YYYYMMDD-HHMM/` pour les entrées et `output/run-YYYYMMDD-HHMM/` pour les résultats. Conserver un identifiant stable par document (`001`, `002`, etc.).

Sorties attendues :
1. Profil détecté.
2. Métadonnées JSON validées.
3. Résultat de recherche Sudoc.
4. Résultat d’alignement IdRef.
5. Notice UNIMARC/XML.
6. Incertitudes et règles `/knowledge/` utilisées.
