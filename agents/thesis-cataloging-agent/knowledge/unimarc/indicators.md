# Indicateurs et sous-zones

Les indicateurs sont explicites. `#` représente un blanc.

| Zone | Indicateurs | Motif |
|---|---:|---|
| 029 | `##` | `$aFR` |
| 100 | `##` | `$a{date de traitement et année}` selon règles locales |
| 101 | `0#` | `$a{langue}` et éventuellement `$c/$d` selon résumé/langue originale |
| 102 | `##` | `$aFR` |
| 104 | `##` | `$ak$by$cy$dba$e0$ffre` pour thèse imprimée originale |
| 105 | `##` | valeur locale approuvée uniquement |
| 106 | `##` | `$ar` |
| 181 | `##` | `$P01$ctxt` |
| 182 | `##` | `$P01$cn` |
| 183 | `##` | `$P01$anga` |
| 200 | `1#` | `$a` titre, `$e` sous-titre, `$f` auteur, `$g` responsabilités secondaires |
| 214 | `#0` | `$d{année}` minimal si seul l’année est connue |
| 215 | `##` | collation si fournie ou vérifiée |
| 320 | `##` | bibliographie/index si présent explicitement |
| 328 | `#0` | `$b` diplôme, `$c` discipline, `$e` établissement, `$d` année |
| 330 | `##` | `$a` résumé |
| 608 | `##` | `$3027253139$aThèses et écrits académiques$2rameau` |
| 686 | `##` | `$a{code}$2TEF` |
| 700 | `#1` | `$3{PPN}$aNom$bPrénom$4070` si PPN fiable ; sans `$3` sinon |
| 701 | `#1` | collaborateurs : `$40727`, `$4003`, `$4956`, `$4958`, `$4555` selon rôle |
| 702 | `#1` | autres responsabilités si règle locale l’exige |
| 711 | `02` | collectivité : `$3{PPN}$aNom$4295/$4995/$4996/$4985` |
