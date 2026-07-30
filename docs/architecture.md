# Architecture

## Principe

Le projet est organisé en plusieurs modules afin de séparer les différentes tâches du scraper. Chaque fichier possède une responsabilité précise.

---

## Organisation

| Fichier | Rôle |
|---------|------|
| `main.py` | Lance le scraper et coordonne les différentes étapes. |
| `config.py` | Contient les paramètres du projet (URL, délais, chemins des fichiers, User-Agent, etc.). |
| `fetcher.py` | Envoie les requêtes HTTP et récupère les pages HTML. |
| `parser.py` | Analyse le HTML avec BeautifulSoup et extrait les informations des parcs. |
| `models.py` | Définit la structure des données d'un parc. |
| `exporter.py` | Exporte les données au format JSONL et CSV. |
| `logger.py` | Enregistre les messages d'information et les erreurs. |
| `verif.py` | Vérifie que les données générées respectent le contrat de données. |

---

## Fonctionnement

Le programme suit les étapes suivantes :

1. Télécharger la page de recherche.
2. Extraire les liens des parcs.
3. Télécharger chaque page de détail.
4. Extraire les informations de chaque parc.
5. Créer un objet représentant le parc.
6. Exporter les données.
7. Vérifier les données produites.

---

## Flux du projet

```text
main.py
    │
    ▼
fetcher.py
    │
    ▼
parser.py
    │
    ▼
models.py
    │
    ▼
exporter.py
    │
    ▼
verif.py
```

---

## Choix de l'architecture

Cette organisation permet de séparer les différentes responsabilités du projet :

- récupération des pages Web ;
- extraction des données ;
- représentation des données ;
- export des résultats ;
- validation des données.

Cette séparation rend le code plus lisible et facilite sa maintenance.