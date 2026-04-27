# Maintenance documentaire

Tu es l’agent de catalogage défini dans `agents/thesis-cataloging-agent/AGENTS.md`.

Mode : maintenance documentaire.

Ne fais pas de catalogage.

Contexte :
- `/raw` est déjà pré-rempli.
- `/knowledge` est la source opérationnelle.
- `/graphify-out` contient seulement des artefacts dérivés.

Tâches :
1. Lire `AGENTS.md`.
2. Lire `workflows/bootstrap-abes-unimarc.md`.
3. Vérifier si `/knowledge` couvre les règles utiles de `/raw/abes-unimarc`.
4. Proposer les mises à jour nécessaires.
5. Ne modifier `/knowledge` que si les règles sont vérifiées.
6. Journaliser dans `knowledge/log.md`.
7. Vérifier que Graphify est disponible.
8. Si la commande `graphify` est absente, installer Graphify avec `UV_CACHE_DIR=/root/.cache/uv uv tool install graphifyy`, puis exécuter `graphify install --platform claw`.
9. Générer les artefacts Graphify.

Commandes Graphify obligatoires :
```bash
command -v graphify || UV_CACHE_DIR=/root/.cache/uv uv tool install graphifyy
graphify install --platform claw
graphify run --input agents/thesis-cataloging-agent/knowledge --output agents/thesis-cataloging-agent/graphify-out
```

Si `uv` est absent ou si l'environnement interdit l'installation d'outils, ne pas présenter cela comme une simple absence de Graphify. Dire explicitement que l'environnement ne permet pas l'installation automatique et donner la commande manuelle à exécuter.

Sortie attendue :
- fichiers `/knowledge` modifiés
- artefacts `/graphify-out` générés
- règles incertaines
