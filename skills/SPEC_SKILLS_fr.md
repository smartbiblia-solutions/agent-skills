# Spécification du Hub de Skills — Workflows Savants & Bibliothéconomiques

> Référence légère pour la nomenclature, la structure des manifestes et le routage agent.
> Compatible avec les conventions AgentSkills et le format OpenClaw/ClawHub.

---

## 0. Notes de compatibilité

Cette spec cible le format **AgentSkills** tel qu'implémenté par **OpenClaw**.
Contraintes imposées par le parser OpenClaw :

- Le champ `name` dans le frontmatter YAML doit être en **snake_case**.
- Le champ `metadata` doit être un **objet JSON sur une seule ligne** (pas d'imbrication YAML multi-niveaux).
- Le bloc `selection` est une **extension AgentDesk uniquement** : OpenClaw l'ignore sans erreur ;
  AgentDesk l'utilise pour son UI de recommandation de skills et son constructeur de pipelines.
- Le nom du dossier (utilisé comme slug ClawHub) reste en **kebab-case** — il est indépendant du champ `name`.

**Nom du dossier** (slug, kebab-case) → `search-works-openalex`  
**Champ `name`** (snake_case, identifiant runtime) → `search_works_openalex`

---

## 1. Principes de conception

- Un nom de skill est un **identifiant de routage**, pas un label marketing.
- Un skill exprime **une capacité dominante unique**.
- Le champ `description` est le **mécanisme de déclenchement principal** — il doit être
  suffisamment riche pour qu'un agent sélectionne le skill sans lire le corps du fichier.
- Tout le reste du manifeste sert la désambiguïsation et le chaînage, pas le routage.

---

## 2. Convention de nommage

### Patron

```
<verbe>-<objet>-<source>
```

- **verbe** — l'action principale réalisée
- **objet** — l'entité principale manipulée ou retournée
- **source** — le système externe ou le corpus, quand le comportement en dépend

Le segment `source` est optionnel pour les skills indépendants de la source :

```
<verbe>-<objet>
```

### Règles de caractères

- ASCII minuscules uniquement
- **Nom du dossier et slug ClawHub** : tirets comme séparateurs (kebab-case)
- **Champ `name` en YAML** : underscores comme séparateurs (snake_case) — exigence OpenClaw
- Pas de suffixes de version dans les noms
- Pas de termes architecturaux : éviter `engine`, `agent`, `tool`, `runner`, `service`

### Verbes recommandés

| Verbe | Utiliser quand |
|-------|----------------|
| `search` | Découvrir des items dans un corpus |
| `lookup` | Résoudre un identifiant connu |
| `fetch` / `retrieve` | Récupérer une ressource connue |
| `generate` | Créer un nouvel output |
| `extract` | Extraire de l'information structurée d'un document |
| `summarize` | Condenser un document unique |
| `synthesize` | Intégrer analytiquement plusieurs documents |
| `screen` | Filtrer un ensemble selon des critères |
| `appraise` | Évaluer la qualité ou la pertinence |
| `classify` | Assigner des catégories ou des sujets |
| `trace` | Documenter une exécution |
| `validate` | Vérifier la conformité à un schéma ou une règle |
| `convert` | Transformer un format ou une structure |
| `annotate` | Ajouter des métadonnées structurées à du contenu existant |
| `orchestrate` | Orchestrer un pipeline de bout en bout |
| `run` | Alternative à `orchestrate` pour les pipelines simples |

### Bons noms

```
Dossier / slug (kebab)         →  champ name (snake_case)
──────────────────────────────────────────────────────────
generate-search-queries        →  generate_search_queries
search-works-openalex          →  search_works_openalex
search-records-sudoc           →  search_records_sudoc
lookup-dois-crossref           →  lookup_dois_crossref
extract-metadata-pdf           →  extract_metadata_pdf
extract-metadata-unimarc       →  extract_metadata_unimarc
screen-studies-prisma          →  screen_studies_prisma
summarize-paper                →  summarize_paper
synthesize-papers-thematic     →  synthesize_papers_thematic
appraise-study-quality         →  appraise_study_quality
classify-text-openalex         →  classify_text_openalex
trace-agent-execution          →  trace_agent_execution
```

### Noms à éviter

```
academic-review-engine   → décrit l'architecture, pas l'action
literature-review-agent  → éviter "agent"
openalex                 → opaque
sru-sudoc                → pas de verbe
search-screen-summarize-papers-openalex  → surchargé
```

---

## 3. Structure du manifeste

Le frontmatter doit rester **minimal et compatible single-line**.
Le parser OpenClaw ne supporte pas les valeurs YAML multi-niveaux sous `metadata`.

### Champs obligatoires

```yaml
name: search_works_openalex
description: >
  Rechercher et récupérer des travaux savants depuis OpenAlex. Utiliser ce skill
  quand la tâche est de découvrir des articles académiques, résoudre des entités
  bibliographiques, ou récupérer des métadonnées structurées depuis le corpus
  OpenAlex. Préférer ce skill à une recherche web générique pour toute tâche
  de récupération savante. Retourne du JSON.
```

**Rédiger une bonne description est la chose la plus importante du manifeste.**
Elle doit répondre à trois questions en 2–4 phrases :
- Que fait ce skill ?
- Quand un agent doit-il le sélectionner ?
- Que retourne-t-il ?

### Champs recommandés

Le champ `metadata` doit être un **objet JSON sur une seule ligne** fusionnant :
- Vos métadonnées hub (`version`, `author`, `maturity`, `preferred_output`, etc.)
- Le sous-objet `openclaw` pour le gating et le comportement runtime

```yaml
metadata: {"version": "0.1.0", "author": "smartbiblia", "maturity": "beta", "preferred_output": "json", "openclaw": {"emoji": "🔬", "requires": {"env": ["OPENALEX_API_KEY"]}}}
```

Pour les skills ne nécessitant aucun binaire externe ni variable d'environnement, `openclaw` peut être omis :

```yaml
metadata: {"version": "0.1.0", "author": "smartbiblia", "maturity": "beta", "preferred_output": "json"}
```

Le bloc `selection` est une **extension YAML multi-niveaux** pour AgentDesk et les lecteurs humains.
OpenClaw l'ignore. Le conserver quand il apporte de la valeur pour le routage ou le chaînage.

```yaml
selection:
  use_when:
    - La tâche est de récupérer des travaux savants depuis OpenAlex.
  avoid_when:
    - La tâche est de synthétiser des articles déjà récupérés.
    - La tâche concerne un catalogue de bibliothèque plutôt que des articles savants.
  prefer_over:
    - generic-web-search
  combine_with:
    - generate-search-queries
    - summarize-paper
    - synthesize-papers-thematic

tags:
  - openalex
  - savant
  - récupération
```

---

## 4. Gating (filtres au chargement OpenClaw)

OpenClaw filtre les skills au chargement via `metadata.openclaw`.
Déclarer les gates pour que l'agent ne tente jamais d'utiliser un skill dont
les dépendances sont absentes de l'environnement.

### `requires.bins`

Liste de binaires qui doivent exister sur `PATH`. Le skill est silencieusement
exclu si un binaire manque.

```yaml
metadata: {"openclaw": {"requires": {"bins": ["uv", "curl"]}}}
```

### `requires.env`

Liste de noms de variables d'environnement qui doivent être définies (ou fournies via config).

```yaml
metadata: {"openclaw": {"requires": {"env": ["OPENALEX_API_KEY"]}}}
```

### `requires.anyBins`

Au moins un binaire de la liste doit exister. Utiliser pour les outils avec des
implémentations alternatives.

```yaml
metadata: {"openclaw": {"requires": {"anyBins": ["curl", "wget"]}}}
```

### `requires.config`

Liste de chemins de config `openclaw.json` qui doivent être truthy.

```yaml
metadata: {"openclaw": {"requires": {"config": ["browser.enabled"]}}}
```

### `primaryEnv`

La variable d'environnement canonique pour la clé API de ce skill. Active la
commodité `skills.entries.<n>.apiKey` dans `openclaw.json`.

```yaml
metadata: {"openclaw": {"primaryEnv": "OPENALEX_API_KEY", "requires": {"env": ["OPENALEX_API_KEY"]}}}
```

### `os`

Restreindre le skill à des plateformes spécifiques.

```yaml
metadata: {"openclaw": {"os": ["darwin", "linux"]}}
```

### `install`

Spécification d'installation optionnelle pour le macOS Skills UI et la configuration automatisée.
Types supportés : `brew`, `node`, `go`, `uv`, `download`.

```yaml
metadata: {"openclaw": {"requires": {"bins": ["uv"]}, "install": [{"id": "uv-pip", "kind": "uv", "package": "scholarly", "bins": ["scholarly"], "label": "Installer scholarly (uv)"}]}}
```

### Table de référence du gating

| Champ | Type | Rôle |
|-------|------|------|
| `requires.bins` | string[] | Tous doivent exister sur PATH |
| `requires.anyBins` | string[] | Au moins un doit exister sur PATH |
| `requires.env` | string[] | Tous doivent être définis dans l'environnement ou la config |
| `requires.config` | string[] | Tous les chemins de config doivent être truthy |
| `primaryEnv` | string | Nom canonique de la variable de clé API |
| `os` | string[] | `darwin`, `linux`, `win32` — restreindre par plateforme |
| `install` | object[] | Spécifications d'installation pour la configuration automatisée |
| `always` | boolean | Mettre `true` pour court-circuiter tous les autres gates |
| `emoji` | string | Emoji pour le macOS Skills UI |

---

## 5. Structure du corps du SKILL.md

Garder le frontmatter concis. L'usage détaillé appartient au corps.
Adapter les sections au type de skill — toutes les sections ne sont pas nécessaires pour chaque skill.

```markdown
--- FRONTMATTER YAML ---

# Titre du skill

## Objectif
Un paragraphe. Quel problème ce skill résout et pour qui.

## Quand utiliser / Quand ne pas utiliser
Reflète le bloc `selection`, mais en prose. Ajouter la nuance que le YAML ne peut pas porter.

## Entrée
Ce que le skill attend : format, champs obligatoires, contraintes.

## Sortie
Ce que le skill retourne : format, schéma, exemple.

## Commandes
Comment invoquer le skill (CLI, commande prompt, appel API).

## Exemples
1–2 paires entrée/sortie concrètes.

## Conseils de composition
Ce qui précède et suit typiquement ce skill dans un pipeline.

## Modes d'échec         ← uniquement si non évident
Conditions d'échec connues et comment les gérer.

## Validation           ← uniquement pour les skills basés sur des contrats
Commande de schéma, commande de validation, politique de retry.
```

---

## 6. Guidance de sélection agent

### Règle de désambiguïsation

Quand plusieurs skills pourraient s'appliquer, préférer dans cet ordre :

1. Skill le plus **spécifique à la source** compatible
2. Skill le plus **atomique**
3. Skill avec **validation explicite**
4. Fallback plus général

**Exemple** — l'utilisateur demande : *"Trouver des articles sur l'indexation sujet multilingue en bibliothèques."*

```
1. generate-search-queries   ← traduire la question d'abord
2. search-works-openalex     ← récupérer depuis le corpus savant
3. search-records-sudoc      ← seulement si des preuves du catalogue sont aussi nécessaires
4. recherche web générique   ← dernier recours
```

### Guidance de chaînage

Documenter ce qui précède et suit chaque skill.
Exemple de pipeline pour une revue systématique :

```
generate-search-queries
  → search-works-openalex
  → screen-studies-prisma
  → summarize-paper
  → appraise-study-quality
  → synthesize-papers-thematic
```

---

## 7. Exemple complet de manifeste

```yaml
name: generate_search_queries
description: >
  Générer des requêtes de recherche savante structurées à partir d'une question
  de recherche en langage naturel. Utiliser ce skill chaque fois que la tâche
  implique de construire une stratégie de recherche, d'étendre une question de
  revue en expressions interrogeables, ou de concevoir des requêtes bilingues
  pour des revues systématiques. Toujours utiliser ce skill avant de récupérer
  des notices depuis un corpus quelconque. Retourne du JSON validé.

metadata: {"version": "0.1.0", "author": "smartbiblia", "maturity": "beta", "preferred_output": "json", "domain": "scholarly-communication", "category": "generation", "openclaw": {"emoji": "🔎", "requires": {}}}

selection:
  use_when:
    - La tâche est de traduire une question de recherche en expressions interrogeables.
    - L'utilisateur a besoin d'une stratégie de recherche bilingue ou multi-bases.
  avoid_when:
    - Des notices ont déjà été récupérées.
    - L'utilisateur n'a besoin que d'un seul mot-clé, pas d'une requête structurée.
  prefer_over:
    - generic-keyword-generator
  combine_with:
    - search-works-openalex
    - search-records-sudoc

tags:
  - revue-systematique
  - strategie-recherche
  - savant
```

Nom du dossier : `generate-search-queries/SKILL.md`

---

## 8. Publication sur ClawHub

ClawHub est le registre public de skills pour OpenClaw. Le nom du dossier est le slug.

```bash
# Publier un skill unique
clawhub publish ./generate-search-queries \
  --slug generate-search-queries \
  --name "Generate Search Queries" \
  --version 0.1.0 \
  --tags latest

# Synchroniser tous les skills du repo en une fois
clawhub sync --all --bump patch
```

Le dépôt Github reste la source de vérité.
`clawhub sync` est l'étape d'automatisation de la publication.

---

## 9. Notes d'import AgentDesk

Quand AgentDesk importe un skill depuis le registre Github :

1. **Transformation `metadata`** — le YAML multi-niveaux lisible par les humains que les
   contributeurs *peuvent* écrire dans le repo est normalisé vers le format JSON single-line
   requis par OpenClaw à l'installation. Les contributeurs peuvent écrire dans l'un ou l'autre
   style ; AgentDesk normalise à l'import.
2. **Bloc `selection`** — parsé et stocké comme métadonnée AgentDesk pour l'UI de recommandation
   de skills (`combine_with`, constructeur de pipelines). Non transmis au runtime agent.
3. **Gating** — `metadata.openclaw.requires` est évalué par rapport à l'environnement local
   à l'installation. Les binaires ou variables d'environnement manquants génèrent un
   avertissement dans l'UI AgentDesk.

---

## 10. Récapitulatif des règles

### Obligatoire
- Nom du dossier : kebab-case minuscule commençant par un verbe (`search-works-openalex`)
- Champ `name` : version snake_case du nom du dossier (`search_works_openalex`)
- Patron `<verbe>-<objet>-<source>` quand la source est déterminante
- `description` riche répondant à : quoi / quand / ce que ça retourne
- `metadata` sous forme d'objet JSON single-line

### Fortement recommandé
- `metadata.openclaw.requires` pour tout skill nécessitant des binaires, variables d'environnement ou clés de config
- `metadata.openclaw.primaryEnv` pour les skills avec une clé API canonique
- Bloc `selection` avec `use_when`, `avoid_when`, `combine_with`
- `metadata.maturity` et `metadata.preferred_output`
- Documentation du chaînage dans le corps du SKILL.md

### À éviter
- Termes architecturaux dans les IDs de skills (`engine`, `agent`, `tool`, `runner`)
- Noms opaques ou ressemblant à des marques
- Noms multi-actions surchargés
- Suffixes de version dans les noms
- Imbrication YAML multi-niveaux sous `metadata` (casse le parser OpenClaw)
- Remplir les champs de métadonnées optionnels avec des valeurs placeholder
