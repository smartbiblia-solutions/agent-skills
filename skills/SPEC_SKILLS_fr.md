# Spécification du hub de skills — Bibliothèques et recherche académique

> Référence allégée pour le nommage, la structure des manifestes et le routage agentique.
> Compatible avec les conventions AgentSkills.

---

## 1. Principes directeurs

- Un nom de skill est un **identifiant de routage**, pas un label marketing.
- Une skill exprime **une capacité dominante**.
- Le champ `description` est le **mécanisme de déclenchement principal** — il doit être suffisamment riche pour qu'un agent sélectionne la skill sans lire le corps du fichier.
- Tout le reste du manifeste sert à la désambiguïsation et à l'enchaînement, pas au routage.

---

## 2. Convention de nommage

### Patron

```
<verbe>-<objet>-<source>
```

- **verbe** — l'action principale réalisée
- **objet** — l'entité principale manipulée ou retournée
- **source** — le système ou corpus externe, quand le comportement en dépend

Le segment `source` est optionnel pour les skills indépendantes de la source :

```
<verbe>-<objet>
```

### Règles de caractères

- ASCII minuscules uniquement
- Traits d'union comme séparateurs, pas d'underscores
- Pas de suffixes de version dans le nom
- Pas de termes architecturaux : éviter `engine`, `agent`, `tool`, `runner`, `service`

### Verbes recommandés

| Verbe | Quand l'utiliser |
|-------|-----------------|
| `search` | Découvrir des items dans un corpus |
| `lookup` | Résoudre un identifiant connu |
| `fetch` / `retrieve` | Récupérer une ressource connue |
| `generate` | Créer un nouvel output |
| `extract` | Extraire des informations structurées d'un document |
| `summarize` | Condenser un document unique |
| `synthesize` | Intégrer analytiquement plusieurs documents |
| `screen` | Filtrer un ensemble selon des critères |
| `appraise` | Évaluer la qualité ou la pertinence |
| `classify` | Assigner des catégories ou sujets |
| `trace` | Documenter une exécution |
| `validate` | Vérifier la conformité à un schéma ou une règle |
| `convert` | Transformer un format ou une structure |
| `annotate` | Ajouter des métadonnées structurées à un contenu existant |
| `synthetize` |  |
| `orchestrate` | Orchester un pipeline complet |
| `run` | Alternative à `orchestrate` |

### Bons noms

```
generate-search-queries
search-works-openalex
search-records-sudoc
lookup-dois-crossref
extract-metadata-pdf
extract-metadata-unimarc
screen-studies-prisma
summarize-paper
synthesize-papers-thematic
appraise-study-quality
classify-text-openalex
trace-agent-execution
```

### Noms à éviter

```
academic-review-engine    → décrit l'architecture, pas l'action
literature-review-agent   → éviter "agent"
openakes                  → opaque
sru-sudoc                 → pas de verbe
search-screen-summarize-papers-openalex  → surchargé
```

---

## 3. Structure du manifeste

Le frontmatter doit rester **minimal**. L'agent lit `name` et `description` en premier —
tout le reste est secondaire.

### Champs requis

```yaml
name: search-works-openalex
description: >
  Recherche et récupère des travaux académiques depuis OpenAlex. Utilise cette
  skill dès que la tâche consiste à découvrir des articles scientifiques,
  résoudre des entités bibliographiques, ou récupérer des métadonnées structurées
  depuis le corpus OpenAlex. À préférer à la recherche web générique pour toute
  tâche de récupération académique. Retourne du JSON.
```

**Bien rédiger la description est la chose la plus importante du manifeste.**
Elle doit répondre à trois questions en 2 à 4 phrases :
- Que fait cette skill ?
- Quand un agent doit-il la choisir ?
- Que retourne-t-elle ?

### Champs recommandés

```yaml
metadata:
  version: 0.1.0
  author: smartbiblia
  maturity: experimental | beta | stable | deprecated
  preferred_output: json | markdown | text | csv | xml

selection:
  use_when:
    - La tâche consiste à récupérer des travaux académiques depuis OpenAlex.
  avoid_when:
    - La tâche consiste à synthétiser des articles déjà récupérés.
    - La tâche concerne un catalogue de bibliothèque plutôt que des articles scientifiques.
  prefer_over:
    - generic-web-search
  combine_with:
    - generate-search-queries
    - summarize-paper
    - synthesize-papers-thematic

tags:
  - openalex
  - scholarly
  - retrieval
```

### Champs optionnels

À ajouter uniquement s'ils portent une information réelle pour le registre du hub :

```yaml
metadata:
  domain: scholarly-communication | research-workflows | libraries | bibliometrics
  category: retrieval | generation | extraction | synthesis | screening | appraisal
  source: openalex | crossref | sudoc | pubmed
  interface: cli | api | mcp
  requires_network: true
  supports_validation: true
```

### Ce qu'il faut omettre

Champs à supprimer sauf raison concrète de les renseigner :
`deterministic`, `scope`, `subcategory`, `entrypoint`, `package_manager`,
`requires_auth`, `input_modes`, `output_modes`, `languages`.
Des métadonnées périmées sont pires que pas de métadonnées.

---

## 4. Structure du corps SKILL.md

Garder le frontmatter concis. L'usage détaillé appartient au corps du fichier.

Adapter les sections au type de skill — toutes les skills n'ont pas besoin de toutes les sections.

```markdown
--- FRONTMATTER YAML ---

# Titre de la skill

## Objectif
Un paragraphe. Quel problème cette skill résout et pour qui.

## Quand l'utiliser / Quand ne pas l'utiliser
Reprend le bloc `selection`, mais en prose. Ajoute les nuances que le YAML ne peut pas porter.

## Entrée
Ce que la skill attend : format, champs requis, contraintes.

## Sortie
Ce que la skill retourne : format, schéma, exemple.

## Commandes
Comment invoquer la skill (CLI, commande prompt, appel API).

## Exemples
1 à 2 paires entrée/sortie concrètes.

## Conseils de composition
Ce qui précède et suit typiquement cette skill dans un pipeline.

## Modes d'échec         ← seulement si non évident
Conditions d'échec connues et comment les gérer.

## Validation           ← seulement pour les skills à contrat
Commande de schéma, commande de validation, politique de retry.
```

---

## 5. Guidance de sélection pour l'agent

### Règle de désambiguïsation

Quand plusieurs skills peuvent s'appliquer, préférer dans cet ordre :

1. La skill la plus **spécifique à la source** compatible
2. La skill la plus **atomique**
3. La skill avec **validation explicite**
4. Le fallback plus générique

**Exemple** — l'utilisateur demande : *"Trouve des articles sur l'indexation multilingue en bibliothèque."*

```
1. generate-search-queries          ← traduire d'abord la question
2. search-openalex                  ← récupérer depuis le corpus académique
3. search-sudoc-sru                 ← seulement si des preuves catalogue sont aussi nécessaires
4. recherche web générique          ← dernier recours
```

### Guidance d'enchaînement

Documenter ce qui précède et suit chaque skill.
Exemple de pipeline pour une revue systématique :

```
generate-search-queries
  → search-openalex
  → screen-studies-prisma
  → summarize-paper
  → appraise-study-quality
  → synthesize-papers-thematic
```

---

## 6. Exemple de manifeste complet

```yaml
name: generate-search-queries
description: >
  Génère des requêtes de recherche académiques structurées à partir d'une question
  de recherche en langage naturel. Utilise cette skill dès que la tâche implique
  de construire une stratégie de recherche, d'étendre une question de revue en
  expressions interrogeables, ou de concevoir des requêtes bilingues pour des
  revues systématiques. À utiliser systématiquement avant toute récupération de
  notices dans un corpus. Retourne du JSON validé.

metadata:
  version: 0.1.0
  author: smartbiblia
  maturity: beta
  preferred_output: json
  supports_validation: true

selection:
  use_when:
    - La tâche consiste à traduire une question de recherche en expressions interrogeables.
    - L'utilisateur a besoin d'une stratégie de recherche bilingue ou multi-bases.
  avoid_when:
    - Les notices ont déjà été récupérées.
    - L'utilisateur n'a besoin que d'un mot-clé unique, pas d'une requête structurée.
  prefer_over:
    - generic-keyword-generator
  combine_with:
    - search-openalex
    - search-sudoc-sru

tags:
  - systematic-review
  - search-strategy
  - scholarly
```

---

## 7. Résumé des règles

### Requis
- Nom en minuscules avec traits d'union, commençant par un verbe
- Patron `<verbe>-<objet>-<source>` quand la source est déterminante
- `description` riche répondant à : quoi / quand / ce que ça retourne

### Fortement recommandé
- Bloc `selection` avec `use_when`, `avoid_when`, `combine_with`
- `metadata.maturity` et `metadata.preferred_output`
- Documentation des enchaînements dans le corps du SKILL.md

### À éviter
- Termes architecturaux dans les identifiants (`engine`, `agent`, `tool`, `runner`)
- Noms opaques ou trop orientés marque
- Noms multi-actions surchargés
- Suffixes de version dans les noms
- Renseigner des champs optionnels avec des valeurs par défaut sans les avoir réfléchis