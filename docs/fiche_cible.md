# FICHE DE CIBLE – Parcs Canada

**Cible** : Parcs Canada – Liste des parcs nationaux

**URL de départ** : https://parks.canada.ca/pn-np/recherche-parcs-parks-search

**Date d'analyse** : 30/07/2026

**Analystes** : Anass Houdzi – Barakissa Koné

---

# 1. SOURCE

**Famille de site**

- Site institutionnel public.

**Preuves**

- Une requête HTTP GET permet de récupérer directement le contenu HTML de la page.
- Les liens vers les parcs sont présents dans le HTML de la page de recherche.
- Les pages de détail contiennent directement :
  - le nom du parc ;
  - le résumé ;
  - la province ;
  - le type ;
  - l'image principale.
- Aucun navigateur automatisé (Selenium, Playwright…) n'est nécessaire.

**Fichiers publiés**

| Ressource | Observation |
|-----------|-------------|
| robots.txt | URL testée → page **404** |
| sitemap.xml | Disponible (**HTTP 200**) |
| sitemap-index.xml | URL testée → **HTTP 404** |

**Nombre d'URL connues**

- 47 pages de parcs identifiées depuis la page de recherche.

---

# 2. SURFACE PORTEUSE DE LA DONNÉE

## HTML initial

**Oui**

- Les liens vers les parcs sont accessibles directement dans le HTML.
- Les pages de détail contiennent également :
  - le nom ;
  - le résumé ;
  - la province ;
  - le type ;
  - l'image.

## DOM après JavaScript

**Non nécessaire**

- JavaScript est utilisé pour :
  - la carte ;
  - les filtres ;
  - la recherche.
- Les informations utilisées par le scraper sont déjà présentes dans le HTML.

## Appels réseau

- Requête HTTP GET vers la page de recherche.
- Puis une requête HTTP GET vers chaque page de détail.
- Aucun endpoint JSON contenant les données des parcs n'a été observé.

## Format de réponse

- HTML (UTF-8)

## Champs disponibles

| Champ |
|--------|
| id |
| name |
| province |
| type |
| summary |
| url |
| image_url |
| collected_at |
| source_url |

## Couverture du contrat

- `id` est généré de manière stable.
- `province` est extraite depuis l'URL puis normalisée en majuscules.
- `url` et `image_url` sont converties en URLs absolues.
- `collected_at` est ajouté automatiquement lors de la collecte.
- `source_url` contient l'URL d'origine.

---

# 3. TECHNIQUE D'ACQUISITION RETENUE

## Niveau

**Niveau 4 – Acquisition HTTP directe**

## Valeur de source

- HTTP

## Bibliothèques utilisées

- `requests`
- `BeautifulSoup`

## Fonctionnement

1. `requests` envoie une requête HTTP GET.
2. Le serveur renvoie une page HTML.
3. `BeautifulSoup` analyse le HTML.
4. Les liens des parcs sont récupérés.
5. Chaque page de détail est ensuite analysée pour extraire les informations.

## Commande de référence

```bash
curl.exe "https://parks.canada.ca/pn-np/recherche-parcs-parks-search"
```

## En-têtes nécessaires

- User-Agent personnalisé
- Accept-Language

## Pagination

- Aucune pagination observée.
- Les liens sont récupérés directement depuis la page de recherche.

## Condition d'arrêt

- Fin de la liste des liens.
- Ou atteinte de `MAX_OBJECTS`.

## Nombre maximum

- 47 objets.

## Niveaux écartés

### Niveau 1

- Aucun fichier CSV ou JSON public contenant les données des parcs n'a été utilisé.

### Niveau 2

- Aucune API publique documentée n'a été utilisée.

### Niveau 3

- Aucun endpoint JSON contenant les données des parcs n'a été observé.

### Niveau 5

- Selenium ou Playwright ne sont pas nécessaires, les données étant présentes dans le HTML.

### Niveau 6

- OCR et vision artificielle inutiles, les informations sont textuelles.

---

# 4. COMPLEXITÉ

**Estimation**

- **S**

**Justification**

- Environ 47 parcs.
- Structure HTML relativement régulière.
- Aucune authentification.
- Aucune pagination.
- Aucune interaction utilisateur.
- JavaScript non nécessaire pour l'extraction.
- Collecte synchrone suffisante.

---

# 5. RISQUES ET CONTRAINTES

## Risques techniques

- Modification des classes HTML.
- Changement de la structure des pages.
- Modification des sélecteurs HTML.
- Certaines informations peuvent être absentes.
- La province dépend de la structure de l'URL.
- Les URLs des images peuvent évoluer.

## Contraintes juridiques

- Données publiques utilisées dans un cadre pédagogique.
- Aucune donnée personnelle collectée.
- Les conditions d'utilisation du site doivent être respectées.
- Aucun `robots.txt` exploitable n'a été trouvé à l'URL standard testée.

## Charge estimée

- Environ 48 requêtes.
- 1 requête pour la page de recherche.
- Puis 1 requête par parc.
- Délai de **1 seconde** entre les requêtes.
- Timeout de **30 secondes**.
- Aucune concurrence.

## Points de rupture

- Changement de la structure HTML.
- Modification des balises contenant le nom (`h1`).
- Modification des paragraphes de résumé.
- Modification de la structure des URLs.
- Suppression ou changement des images principales.

## Repli prévu

- Utiliser plusieurs sélecteurs HTML si nécessaire.
- Utiliser les métadonnées HTML (`og:image`, `og:description`) comme solution de secours.
- Utiliser le nom trouvé sur la page de recherche si celui de la page de détail est indisponible.
- Rejeter les objets incomplets.
- Enregistrer les erreurs dans les journaux (`logs`).