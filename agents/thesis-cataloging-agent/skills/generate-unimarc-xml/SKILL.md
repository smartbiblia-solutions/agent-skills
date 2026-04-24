# generate-unimarc-xml

## But

Générer une notice UNIMARC/XML à partir du JSON validé et des règles de `/knowledge/`.

## Règles

- Ne jamais générer depuis un JSON non validé.
- Utiliser `knowledge/unimarc/json-to-unimarc.md`.
- Respecter explicitement les indicateurs de `knowledge/unimarc/indicators.md`.
- Insérer `$3` uniquement pour les PPN IdRef fiables.
- Générer `686 ##$a{code}$2TEF` pour `these_originale_imprimee`; pour mémoire seulement si règle locale explicite.
- Si `008` ou `105` manque de règle locale approuvée, produire une erreur de validation plutôt qu’inventer.
