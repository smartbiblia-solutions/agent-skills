# validate-unimarc

## But

Vérifier la cohérence bibliographique et technique de l’UNIMARC/XML.

## Contrôles

- XML bien formé.
- Présence des zones obligatoires du profil.
- Indicateurs conformes au wiki.
- Codes de fonction cohérents.
- `686` présent/absent selon profil.
- Aucun PPN inventé.
- Pas de zone issue d’un profil non supporté.

## Sortie

Rapport français : valide, avertissements, erreurs bloquantes.
