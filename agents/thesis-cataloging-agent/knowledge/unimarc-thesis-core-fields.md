# UNIMARC thesis core fields

## Socle minimal recommandé

### 101 — Langue
- `$a` code langue sur 3 lettres.
- Exemple: `fre`, `eng`.

### 200 — Titre et mention de titre
- `$a` titre propre
- `$e` complément du titre / sous-titre si pertinent

### 210 — Publication, diffusion, date
- Pour ce prototype, seule la date `$d` est utilisée comme année de soutenance quand aucune modélisation plus fine n'est disponible.

### 328 — Note de thèse
- Exprime le type de diplôme / nature académique.
- Exemples: `Thèse de doctorat`, `Thèse d'exercice`, `Habilitation à diriger des recherches`.

### 330 — Résumé
- `$a` texte du résumé.

### 686 — Indice / discipline locale
- Utilisé ici pour porter une discipline contrôlée de type Dewey + libellé local.

### 700 — Auteur personne physique
- `$a` forme d'accès retenue, de préférence sous la forme `Nom, Prénom`
- `$3` identifiant d'autorité si disponible

### 701 — Autre auteur / contributeur principal
- Utilisé ici pour directeur / directrice de thèse dans le prototype.

### 702 — Contributeur secondaire
- Utilisé ici pour président du jury, rapporteurs, autres membres.

### 712 — Collectivité secondaire
- Peut porter l'établissement de soutenance.

## Règles de qualité

- Une notice générée doit contenir au minimum: `101`, `200`, `700`.
- `328` est fortement recommandée pour éviter l'ambiguïté sur la nature de la ressource.
- Les zones personnes doivent avoir au moins un sous-champ `$a`.
