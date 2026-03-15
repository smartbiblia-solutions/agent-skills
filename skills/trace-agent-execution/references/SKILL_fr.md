---
name: agent-trace
description: >
  Génère une trace d'exécution lisible à partir du log brut d'un run agentique,
  indépendamment du framework utilisé (Claude Code, LangChain, AgentMD, etc.).
  Utilise cette skill dès qu'un utilisateur mentionne un log d'exécution, un run
  agentique, un historique de tâche automatisée, ou qu'il demande à "comprendre
  ce que l'agent a fait", "avoir un résumé du run", "documenter l'exécution" ou
  "produire un rapport d'audit". Fonctionne aussi en amont : si l'utilisateur
  demande comment tracer ou documenter ses workflows agentiques, propose ce format.
metadata:
  version: 0.1.0
  author: smartbiblia
---

# Agent Trace

Transforme un log brut d'exécution agentique en document `.run.md` lisible,
auditable et commitable — quel que soit le framework source.

L'objectif est le même que pour un notebook Jupyter sauvegardé : quelqu'un qui
n'était pas là pendant le run doit pouvoir comprendre ce qui s'est passé, pourquoi,
et avec quel résultat.

---

## 1. Identifier le mode de sortie

Avant de générer la trace, détermine qui va la lire :

| Mode | Lecteur cible | Niveau de détail |
|------|---------------|-----------------|
| `audit` | Développeur, ops | Toutes les étapes, commandes, exit codes, durées |
| `narrative` | Chef de projet, non-codeur | Décisions et résultats en langage naturel, pas de commandes |
| `compact` | CI/CD, archivage | Tableau de synthèse uniquement |

Si le mode n'est pas précisé, utilise `audit` par défaut et propose les autres en fin de document.

---

## 2. Extraire les informations du log brut

Quel que soit le format source (JSON, texte libre, output terminal, XML), extrais :

- **Identité du run** : nom du workflow, timestamp de début, durée totale
- **Statut global** : success / failure / partial
- **Séquence des steps** : dans l'ordre d'exécution
- **Pour chaque step** : nom ou id, statut, durée si disponible, output significatif
- **Décisions de l'agent** : conditions évaluées, branches choisies, retries
- **Rollbacks éventuels** : lesquels ont été déclenchés et pourquoi
- **Variables capturées** : valeurs importantes produites en cours de run
- **Erreurs** : messages d'erreur, exit codes non-zéro, timeouts

Si une information est absente du log (durée, exit code…), laisse le champ vide
plutôt que d'inventer une valeur.

---

## 3. Structure du fichier `.run.md`

TOUJOURS utiliser ce template exact :

```markdown
# Trace : <nom-du-workflow> — <timestamp ISO 8601>

## Résultat global

**Statut** : ✓ success | ✗ failure | ⚠ partial  
**Durée** : <durée totale>  
**Framework** : <Claude Code | LangChain | AgentMD | inconnu>  

<Une phrase résumant ce que le run a accompli ou pourquoi il a échoué.>

---

## Étapes

| # | Étape | Statut | Durée |
|---|-------|--------|-------|
| 1 | <nom> | ✓ | <durée> |
| 2 | <nom> | ✗ | <durée> |

---

## Détail des étapes

### 1. <nom de l'étape>

**Statut** : ✓ success  
**Durée** : 14.2s  

<Ce que cette étape a fait, en une ou deux phrases.>

**Output significatif** (si pertinent) :
\```
<extrait de l'output, tronqué à ~10 lignes>
\```

---

### 2. <nom de l'étape>

...

---

## Variables capturées

| Variable | Valeur |
|----------|--------|
| VERSION | v1.4.2 |
| SERVICE_URL | http://... |

*(Section omise si aucune variable capturée)*

---

## Erreurs et avertissements

*(Section omise si le run est un succès complet)*

### <nom de l'étape en échec>

**Cause** : <message d'erreur ou description>  
**Action prise** : stopped | continued | rollback déclenché  

---

## Rollbacks exécutés

*(Section omise si aucun rollback)*

| Rollback | Pour le step | Statut |
|----------|-------------|--------|
| <nom> | <step compensé> | ✓ |

---

## Notes

<Observations importantes qui ne rentrent pas dans les sections ci-dessus :
comportements inattendus, retries, décisions conditionnelles notables.>
```

---

## 4. Règles de rédaction par mode

### Mode `audit`
- Inclure toutes les sections du template, même si certaines sont vides (marquer "aucun")
- Conserver les extraits d'output significatifs (erreurs, valeurs clés)
- Préciser les exit codes pour les étapes en échec
- Ne pas paraphraser les messages d'erreur — les retranscrire tels quels

### Mode `narrative`
- Remplacer le tableau "Étapes" par un paragraphe narratif fluide
- Dans le détail des étapes, décrire l'action en langage naturel sans termes techniques
- Omettre les exit codes, commandes shell, et stack traces
- Formuler les erreurs comme des constats ("L'envoi a échoué car le serveur était indisponible")
- Omettre les sections "Variables capturées" et "Rollbacks" sauf si critiques pour la compréhension

### Mode `compact`
- Une seule section : le tableau de synthèse + le résultat global
- Pas de détail par étape
- Adapté pour être embarqué dans un email ou un ticket

---

## 5. Nom de fichier et emplacement

Proposer systématiquement le nom de fichier :

```
<nom-du-workflow>.<YYYYMMDD-HHMM>.run.md
```

Exemple : `deploy-staging.20241115-1432.run.md`

Si plusieurs runs du même workflow existent, ils s'accumulent naturellement
par ordre chronologique dans le même répertoire.

---

## 6. Ce que la skill ne fait pas

- Elle ne réexécute pas le workflow
- Elle n'interprète pas les intentions de l'agent au-delà de ce que le log contient
- Elle ne corrige pas les erreurs du run — elle les documente
- Si le log est trop fragmentaire pour reconstituer une séquence cohérente,
  elle le signale explicitement plutôt que de combler les trous par inférence

---

## Exemple

**Input (log brut terminal) :**
```
[14:32:01] check-workspace: OK
[14:32:01] ecr-login: running...
[14:32:08] ecr-login: done (exit 0, 7.2s)
[14:32:08] build: running...
[14:32:22] build: done (exit 0, 14.1s)
[14:32:22] push-image: running...
[14:32:31] push-image: FAILED (exit 1, 8.9s)
[14:32:31] stderr: denied: User: arn:aws:iam::123 is not authorized
[14:32:31] rollback: delete-ecr-tag running...
[14:32:33] rollback: delete-ecr-tag done (exit 0)
[14:32:33] workflow FAILED — rollback complete
```

**Output généré (mode `audit`) :**

```markdown
# Trace : deploy-staging — 2024-11-15T14:32:01Z

## Résultat global

**Statut** : ✗ failure  
**Durée** : 32s  
**Framework** : inconnu  

Le déploiement a échoué lors du push de l'image sur ECR faute de permissions IAM.
Un rollback a été exécuté avec succès.

---

## Étapes

| # | Étape | Statut | Durée |
|---|-------|--------|-------|
| 1 | check-workspace | ✓ | — |
| 2 | ecr-login | ✓ | 7.2s |
| 3 | build | ✓ | 14.1s |
| 4 | push-image | ✗ | 8.9s |

---

## Détail des étapes

### 1. check-workspace
**Statut** : ✓ success

Vérification préliminaire du workspace.

### 2. ecr-login
**Statut** : ✓ success  
**Durée** : 7.2s

Authentification auprès d'Amazon ECR.

### 3. build
**Statut** : ✓ success  
**Durée** : 14.1s

Construction de l'image Docker.

### 4. push-image
**Statut** : ✗ failure  
**Durée** : 8.9s  
**Exit code** : 1

Tentative d'envoi de l'image sur ECR.

**Erreur** :
\```
denied: User: arn:aws:iam::123 is not authorized
\```

---

## Erreurs et avertissements

### push-image

**Cause** : `denied: User: arn:aws:iam::123 is not authorized`  
**Action prise** : rollback déclenché

---

## Rollbacks exécutés

| Rollback | Pour le step | Statut |
|----------|-------------|--------|
| delete-ecr-tag | push-image | ✓ |
```