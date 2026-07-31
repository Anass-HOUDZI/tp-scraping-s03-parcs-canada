# Architecture du scraper S03

## Flux de données

```text
Page de liste publique
        |
        v
Fetcher : GET + Session + délai + timeout + retry exponentiel
        |
        v
Parser de liste : ancres sémantiques + URL absolues + déduplication
        |
        v
Pages détail publiques
        |
        v
Parser de détail : h1 / main / meta Open Graph + stratégies de repli
        |
        v
ProtectedPlace.clean() : espaces, N/A, province, horodatage UTC
        |
        v
Validation : champs obligatoires + ID déjà vu
        |
        v
Exporter : un objet JSON par ligne
        |
        v
parcs_canada.jsonl + traces
```

## Choix d'architecture

### Séparation des responsabilités

`Fetcher` ne connaît pas la structure HTML. Le parseur ne réalise aucune requête réseau. Le modèle concentre les règles de qualité. L'exporteur ne décide pas si un objet est valide. Cette séparation réduit le couplage et permet de tester chaque niveau indépendamment.

### Robustesse réseau

Les codes 429, 500, 502, 503 et 504 sont considérés comme temporaires. Le retry applique un délai exponentiel `facteur × 2^(tentative-1)` avec un jitter. Le header `Retry-After` est prioritaire lorsqu'il est fourni par le serveur. Les erreurs 4xx non temporaires ne sont pas répétées inutilement.

### Ancrage sémantique

Les sélecteurs principaux reposent sur des éléments ayant un sens documentaire : liens `<a>`, titre `<h1>`, zone `<main>`, paragraphes `<p>` et métadonnées Open Graph. Les classes CSS sont volontairement évitées, car elles sont plus susceptibles de changer lors d'une refonte graphique.

### Qualité des données

La dataclass distingue une information absente (`None`) d'une valeur présente mais vide (`""`). La méthode `clean()` supprime les espaces parasites, convertit les marqueurs `N/A` en `None`, normalise la province et impose un horodatage UTC ISO 8601.

### Vérification reproductible

`verif.py` travaille uniquement avec des fichiers versionnés. Il reparcourt la page locale avec le vrai parseur et rejoue les règles de rejet à partir de fixtures contrôlées. La correction reste donc possible sans accès internet et sans dépendre de l'état futur du site.
