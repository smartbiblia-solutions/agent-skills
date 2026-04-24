# Profils locaux supportés

## `these_originale_imprimee`

Thèse doctorale originale imprimée.

### Inclus

- Thèse imprimée originale soutenue dans un établissement.
- Degré fermé admis : `Thèse d'État`, `Thèse de doctorat`, `Thèse de 3e cycle`, `Thèse d'université`, `Thèse de docteur-ingénieur`.

### Exclus

- Thèse électronique.
- Reproduction.
- Édition commerciale.
- Thèse d’exercice.
- HDR.
- Manuscrit.
- Cas incertain.

### Zones obligatoires minimales

- `008` selon profil local imprimé original, valeur à produire seulement si la règle locale complète est présente.
- `029 ##$aFR`
- `102 ##$aFR`
- `104 ##$ak$by$cy$dba$e0$ffre`
- `105` : règle locale spécialiste à confirmer dans `/knowledge/` avant génération définitive. Ne jamais utiliser `$bv` seulement parce que le document est un mémoire.
- `106 ##$ar`
- `181 ##$P01$ctxt`
- `182 ##$P01$cn`
- `183 ##$P01$anga`
- `200` titre et mentions de responsabilité.
- `214` publication/production et date.
- `328 #0` note de thèse obligatoire.
- `608 ##$3027253139$aThèses et écrits académiques$2rameau`
- `686 ##$a{discipline.code}$2TEF` obligatoire.
- `700` auteur principal.
- `711` établissement de soutenance.

## `memoire_original_imprime`

Mémoire/dissertation original(e) imprimé(e).

### Inclus

- Mémoire imprimé original.
- Degré fermé admis : `Mémoire de DEA`, `Mémoire de DES`, `Mémoire de DESS`, `Mémoire de DU`, `Mémoire de DIU`, `Mémoire de DUT`, `Mémoire de maîtrise`, `Mémoire de master professionnel 1re année`, `Mémoire de master professionnel 2e année`, `Mémoire de master recherche 1re année`, `Mémoire de master recherche 2e année`.

### Exclus

- Soumission électronique.
- Reproduction.
- HDR.
- Édition commerciale.
- Cas incertain.

### Zones obligatoires minimales

- Même logique imprimée texte que la thèse sauf exception locale explicite.
- `328 #0` obligatoire.
- `686` non automatique : ne le générer que si une règle locale approuvée l’exige.

## Arrêt obligatoire

Si le profil ne peut pas être classé avec une confiance élevée :

```text
Le document ne correspond pas avec certitude aux deux profils locaux supportés. Une revue par un catalogueur humain est nécessaire.
```
