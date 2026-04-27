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
7. Générer les artefacts Graphify.

Commandes Graphify :
UV_CACHE_DIR=/root/.cache/uv uv tool install graphifyy
graphify install --platform claw
graphify run --input agents/thesis-cataloging-agent/knowledge --output agents/thesis-cataloging-agent/graphify-out

Sortie attendue :
- fichiers `/knowledge` modifiés
- artefacts `/graphify-out` générés
- règles incertaines
