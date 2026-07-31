# TP Web Scraping S03 — Parcs Canada

**Étudiants :** Barakissa Koné et Anass Houdzi  
**Organisation :** projet réalisé en binôme conformément aux consignes données en cours  
**Formation :** Mastère IA, Développement & Data — IPSSI Lille  
**Objet métier :** `ProtectedPlace`  
**Cible :** `https://parks.canada.ca/pn-np`

## Objectif

Collecter au maximum 60 lieux protégés publiés par Parcs Canada, transformer le HTML public en objets structurés, contrôler leur qualité puis les exporter au format JSON Lines.

Le site délivre le contenu utile dans le HTML initial : `requests` suffit pour l'acquisition et `BeautifulSoup` pour le parsing. Selenium n'apporterait ici qu'un coût supplémentaire sans bénéfice fonctionnel.

## Données produites

Chaque objet contient :

- `id` : identifiant stable dérivé de l'URL ;
- `name` : nom du lieu ;
- `province` : code territorial normalisé en majuscules ;
- `type` : type de lieu protégé ;
- `summary` : résumé ;
- `url` : URL absolue ;
- `image_url` : URL absolue de l'image, si disponible ;
- `collected_at` : horodatage UTC ;
- `source_url` : source de référence.

## Architecture

```text
config.py                Paramètres centralisés et surchargeables par environnement
main.py                  Orchestration du pipeline
verif.py                 Vérification hors ligne
src/
  fetcher.py             Session HTTP, délai, timeout, retry exponentiel
  parser.py              Sélecteurs sémantiques et stratégies de repli
  models.py              Dataclass, nettoyage et validation
  exporter.py            Export JSONL
  logger.py              Traces INFO / WARNING / ERROR
docs/
  architecture.md        Flux de données et décisions techniques
  AI_USAGE.md            Déclaration transparente de l'usage de l'IA
samples/
  sample_page.html       Copie locale de la page de liste
  sample_output.jsonl    Sortie JSONL vérifiable de 47 objets
```

## Installation

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Configuration

Les valeurs par défaut sont définies dans `config.py`. Elles peuvent être surchargées par des variables d'environnement.

```powershell
$env:PARKS_CONTACT_EMAIL="prenom.nom@exemple.fr"
$env:PARKS_MAX_OBJECTS="60"
$env:PARKS_REQUEST_DELAY="1.0"
```

Le `User-Agent` identifie clairement le scraper et contient un contact. Le header `Accept-Language` force la préférence française : `fr-CA,fr;q=0.9`.

## Exécution complète

```powershell
python main.py
```

Sorties :

```text
data/parcs_canada.jsonl
samples/sample_output.jsonl
logs/scraper.log
```

Le fichier `data/` est une sortie locale complète. L'échantillon placé dans `samples/` est versionné pour permettre la correction hors ligne.

## Vérification hors ligne

```powershell
python verif.py
```

Le script ne réalise aucune requête réseau. Il :

1. reparcourt `samples/sample_page.html` avec le vrai parseur de liens ;
2. contrôle les URL absolues et les provinces normalisées ;
3. injecte un doublon et un objet incomplet pour vérifier leur rejet ;
4. affiche le tableau `Vus / Exportés / Rejetés / Doublons / Champs manquants`.

Résultat attendu :

```text
Vus : 49 | Exportés : 47 | Rejetés : 2 | Doublons : 1 | Champs manquants : 2
3/3 contrôles réussis
```

## Fiche descriptive de la cible S03

- **Nature :** site institutionnel public, bilingue français/anglais.
- **Rendu :** contenu accessible dans le HTML initial ; JavaScript non requis.
- **Méthode HTTP :** GET uniquement.
- **Volume :** plafond strict de 60 objets ; le jeu observé contient 47 parcs.
- **Politesse :** délai entre les requêtes, session persistante, timeout, retry exponentiel sur 429 et erreurs serveur temporaires.
- **Sélecteurs :** ancres HTML, `h1`, `main`, paragraphes et métadonnées Open Graph ; aucune dépendance principale à une classe CSS volatile.
- **Éthique :** aucune authentification, aucun CAPTCHA contourné, aucune donnée personnelle, aucune écriture sur le site.

## Limites

Le parseur dépend malgré tout de la structure éditoriale du site. Un changement des balises sémantiques ou des conventions d'URL peut imposer une adaptation. La province est déduite de l'URL ; cette règle doit être réévaluée si le routage du site change.

## Commandes utiles avant remise

```powershell
python -m compileall .
python verif.py
git status
git log -1 --oneline
```
