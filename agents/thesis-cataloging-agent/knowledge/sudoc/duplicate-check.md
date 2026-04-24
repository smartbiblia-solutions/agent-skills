# Vérification des doublons Sudoc

La vérification Sudoc précède toute génération de notice.

## Phase 1 — Notice imprimée

Chercher uniquement les thèses/mémoires imprimés, en excluant autant que possible les ressources électroniques, reproductions et profils non supportés.

Ordre obligatoire :

1. strict : titre + auteur + année de soutenance ;
2. relâché : titre + auteur ;
3. secours : titre seul.

Si une notice imprimée probable est trouvée, arrêter :

```text
Une notice existe déjà dans le Sudoc. PPN : {ppn}
```

## Phase 2 — Version électronique

Si aucune notice imprimée n’est trouvée, chercher la version électronique du même travail intellectuel.

Ordre obligatoire :

1. strict : titre + auteur + année de soutenance ;
2. relâché : titre + auteur ;
3. secours : titre seul.

Si une version électronique probable est trouvée, arrêter :

```text
Une notice existe déjà pour la version électronique dans le Sudoc. PPN : {ppn}
```

Sinon, continuer le pipeline.
