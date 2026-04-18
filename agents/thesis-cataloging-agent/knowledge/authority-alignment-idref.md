# Authority alignment with IdRef

## Objectif

Stabiliser les points d'accès personnes et collectivités avant la production de la notice.

## Stratégie minimale

- Conserver le nom source tel qu'extrait.
- Produire une forme normalisée de type `Nom, Prénom`.
- Si un identifiant d'autorité est connu, le reporter en sous-champ de lien d'autorité.
- Si plusieurs autorités plausibles existent, marquer le cas comme ambigu et éviter l'affectation automatique d'un identifiant.

## Cas typiques

### Auteur
- Doit être présent.
- Un identifiant fort est souhaitable, mais le prototype peut fonctionner sans si la forme retenue est stable.

### Directeur / directrice
- Le rôle doit être conservé même sans autorité résolue.

### Jury, rapporteurs, président
- Les membres peuvent être portés comme contributeurs secondaires si les règles locales de catalogage le prévoient.

## Politique d'ambiguïté

- En cas d'homonymie, ne pas forcer un PPN.
- Retourner une explication exploitable par l'opérateur.
