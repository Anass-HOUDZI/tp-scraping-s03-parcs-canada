# TP Scraping S03 – Parcs Canada

## Présentation

Ce projet a été réalisé dans le cadre du module **Web Scraping** à l'IPSSI.

L'objectif est de développer un scraper permettant de collecter automatiquement les informations des parcs nationaux du Canada à partir du site officiel de Parks Canada.

Le programme récupère la liste des parcs disponibles, visite chaque page de détail afin d'extraire les informations utiles, puis exporte les données dans des formats exploitables.

---

## Objectifs

Le projet permet de :

- récupérer automatiquement les liens des parcs nationaux ;
- visiter les pages de détail de chaque parc ;
- extraire les informations demandées ;
- nettoyer et normaliser les données ;
- exporter les résultats au format JSONL et CSV ;
- vérifier automatiquement la qualité des données collectées.

---

## Technologies utilisées

- Python 3
- Requests
- BeautifulSoup
- Dataclasses
- Logging
- JSON Lines (JSONL)
- CSV

---

## Source des données

Les données proviennent du site officiel de Parks Canada :

https://parks.canada.ca/pn-np/recherche-parcs-parks-search

Le scraper utilise des requêtes HTTP GET pour récupérer le contenu HTML des pages. Les informations nécessaires étant directement présentes dans le HTML, aucun navigateur automatisé (Selenium ou Playwright) n'est utilisé.

---

## Données collectées

Pour chaque parc, le programme récupère les informations suivantes :

| Champ | Description |
|--------|-------------|
| id | Identifiant unique |
| name | Nom du parc |
| province | Province canadienne |
| type | Type du parc |
| summary | Description du parc |
| url | URL de la page du parc |
| image_url | URL de l'image principale |
| collected_at | Date de collecte |
| source_url | URL de la page source |

---

## Installation

Cloner le dépôt :

```bash
git clone https://github.com/<repository>.git
```

Créer un environnement virtuel :

```bash
python -m venv .venv
```

Activer l'environnement virtuel :

Sous Windows :

```bash
.venv\Scripts\activate
```

Sous Linux ou macOS :

```bash
source .venv/bin/activate
```

Installer les dépendances :

```bash
pip install -r requirements.txt
```

---

## Exécution

Pour lancer le scraper :

```bash
python main.py
```

Le programme effectue les étapes suivantes :

1. télécharge la page de recherche ;
2. récupère les liens des parcs ;
3. visite chaque page de détail ;
4. extrait les informations ;
5. nettoie les données ;
6. exporte les résultats.

---

## Vérification

Le projet contient un script permettant de vérifier automatiquement les données produites.

Exécuter :

```bash
python verif.py
```

Les vérifications portent notamment sur :

- la présence des champs obligatoires ;
- la normalisation des provinces ;
- les URLs absolues ;
- l'absence de doublons ;
- le respect du contrat de données.

---

## Résultats

Les données sont exportées dans les fichiers suivants :

```text
data/parcs_canada.jsonl
```

et

```text
data/parcs_canada.csv
```

---

## Limites

Le scraper dépend de la structure HTML du site. Les principaux risques sont :

- modification des balises HTML ;
- changement des sélecteurs utilisés ;
- modification des URLs ;
- disparition de certaines informations.

---

## Cadre d'utilisation

Ce projet est réalisé dans un cadre pédagogique dans le cadre du module de Web Scraping de l'IPSSI.

Les données collectées proviennent d'un site public et sont utilisées uniquement à des fins d'apprentissage.

---

## Etudiants 

- Anass Houdzi
- Barakissa Koné

