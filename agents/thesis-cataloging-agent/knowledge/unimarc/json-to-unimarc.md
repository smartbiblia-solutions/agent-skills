# Mapping JSON → UNIMARC

- `title` → `200 $a`
- `subtitle` → `200 $e`
- `author` → `200 $f` et `700 $4070`
- `advisor` → `200 $g` précédé par `sous la direction de`; aussi `701 $4727` pour directeur de thèse ou `701 $4003` pour directeur de mémoire selon profil
- `defense_year` → `100 $a`, `214 $d`, `328 $d`
- `abstract` → `330 $a`
- `jury_president` → `701 $4956`
- `reviewers` → `701 $4958`
- `committee_members` → `701 $4555`
- `granting_institution` → `711 $4295`
- `co_tutelle_institutions` → `711 $4995`
- `doctoral_school` → `711 $4996`
- `partner_institutions` → `711 $4985`
- `discipline.code` → `686 $a` quand le profil actif requiert `686`

## Règles de répétition

- Répéter `701` pour chaque personne et rôle distinct.
- Répéter `711` pour chaque collectivité et rôle distinct.
- Injecter `$3` uniquement si l’alignement IdRef est fort.
