# Zones statiques et conditionnelles

## Communes aux imprimés texte supportés

- `029 ##$aFR` : code pays de publication/production France lorsque le profil local le confirme.
- `102 ##$aFR` : pays associé.
- `106 ##$ar` : forme matérielle imprimée.
- `181 ##$P01$ctxt` : forme du contenu texte.
- `182 ##$P01$cn` : type de médiation sans médiation.
- `183 ##$P01$anga` : type de support volume.
- `608 ##$3027253139$aThèses et écrits académiques$2rameau` : forme/genre RAMEAU.

## Thèse originale imprimée

- `104 ##$ak$by$cy$dba$e0$ffre`
- `328 #0$b{degree}$c{discipline}$e{institution}$d{year}`
- `686 ##$a{code}$2TEF`

## Mémoire original imprimé

- `328 #0$b{degree}$c{discipline}$e{institution}$d{year}`
- `686` seulement si `/knowledge/` contient une règle locale explicite.

## Zones à ne pas improviser

- `008` et `105` exigent la règle locale complète. Si absente, produire une erreur de validation demandant validation humaine plutôt qu’inventer.
