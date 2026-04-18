---
name: enrich-with-idref
description: >
  Enrichir les personnes d'une thèse avec des alignements IdRef et préparer
  l'injection des PPN dans les zones UNIMARC 700/701/702 via le sous-champ `$3`.
  Utiliser cette compétence après `search-authorities-idref` (généralement via le sous-commande CLI `search`) et avant la génération
  UNIMARC. Déclencheurs typiques : "aligner avec IdRef", "ajouter les PPN",
  "enrichir les personnes de la notice". Retourne un JSON enrichi.
metadata:
  {
    "version": "0.1.0",
    "author": "agent-skills",
    "maturity": "experimental",
    "preferred_output": "json",
    "openclaw": { "requires": {} },
  }

selection:
  use_when:
    - Des personnes extraites doivent être alignées avec IdRef.
    - Le pipeline doit injecter des PPN dans les zones d'autorité UNIMARC.
  avoid_when:
    - La tâche consiste à interroger l'autorité IdRef elle-même — utiliser `search-authorities-idref` avec la sous-commande CLI adaptée (`search`, `get` ou `references`).
    - La tâche consiste déjà à sérialiser la notice finale en XML — utiliser generate-unimarc-xml-thesis.
  prefer_over:
    - generic-entity-linking
  combine_with:
    - search-authorities-idref (subcommand `search`)
    - generate-unimarc-xml-thesis
    - validate-unimarc

tags:
  - idref
  - authority-control
  - unimarc
  - thesis
---

## Purpose

Cette compétence prend les candidats IdRef déjà récupérés et applique la logique décisionnelle métier : correspondance forte, ambiguïté explicitée, ou absence de correspondance pertinente. Elle ne doit jamais halluciner un PPN ni imposer un match fragile.

## When to use / When not to use

Utiliser cette compétence pour transformer des résultats de recherche IdRef en personnes enrichies prêtes à être injectées dans la notice bibliographique.

Ne pas l'utiliser comme moteur de requête IdRef ni comme générateur UNIMARC.

## CLI usage

```bash
uv run skills/enrich-with-idref/scripts/cli.py \
  --json-file ./metadata.json \
  --ambiguous-names "Nom Ambigu"
```

| Flag | Type | Required | Notes |
|---|---|---|---|
| `--json-file` | path | yes | JSON de métadonnées ; la CLI accepte soit un objet racine, soit un objet contenant la clé `metadata` |
| `--ambiguous-names` | list[string] | no | Noms à forcer en cas ambigu pour les tests ou scénarios contrôlés |

Cette CLI actuelle produit un enrichissement local simulé, utile pour le pipeline et les tests, en attendant un branchement IdRef pleinement opérationnel.

## Rules

- Évaluer les candidats par discipline, titres de travaux existants et domaines de recherche.
- Si la correspondance est forte, assigner le PPN.
- Si le cas est ambigu, choisir le meilleur candidat et expliquer le raisonnement.
- Si aucun candidat pertinent n'existe, retourner `aucune autorité IdRef pertinente trouvée`.
- Interdiction d'halluciner un PPN.

## Output

```jsonc
{
  "persons": [
    {
      "role": "author",
      "name": "Prénom Nom",
      "normalized_form": "Nom, Prénom",
      "ppn": "123456789",
      "match_confidence": "strong",
      "explanation": "Correspondance cohérente avec le domaine et les travaux recensés."
    }
  ],
  "error": null
}
```

## Composition hints

```text
search-authorities-idref (subcommand `search`)
  → enrich-with-idref             ← cette compétence
  → generate-unimarc-xml-thesis
  → validate-unimarc
```
