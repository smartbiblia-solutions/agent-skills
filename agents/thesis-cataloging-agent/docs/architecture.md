# Architecture

## Topologie

Pipeline séquentiel unique.

## Composants

- Ingestion image ou OCR
- Récupération des règles depuis `/knowledge/`
- Récupération de cas depuis `memory/`
- Extraction JSON (`extract-metadata-json-thesis`)
- Validation (`validate-json-schema-thesis`)
- Détection de doublon Sudoc (`search-records-sudoc`)
- Recherche d'autorités IdRef (`search-authorities-idref`)
- Enrichissement PPN (`enrich-with-idref`)
- Génération UNIMARC XML (`generate-unimarc-xml-thesis`)
- Validation UNIMARC (`validate-unimarc`)
- Conversion de sérialisations (`convert-records-unimarc`)
- Auto-amélioration (`self-improve-cataloging`)
- Mise à jour du wiki (`update-wiki-cataloging`)
