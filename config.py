"""
Configuration locale du scraper Parcs Canada.
"""

# Page contenant la liste des parcs
LIST_URL = "https://parks.canada.ca/pn-np/recherche-parcs-parks-search"

# URL de référence
SOURCE_URL = "https://parks.canada.ca/pn-np"

# Fichier d'export attendu
OUTPUT_JSONL = "samples/sample_output.jsonl"

# Journalisation
LOG_FILE = "logs/scraper.log"

# Nombre maximal de parcs à collecter
MAX_OBJECTS = 47

# Paramètres réseau
REQUEST_DELAY = 1.0
REQUEST_TIMEOUT = 30

# User-Agent
USER_AGENT = (
    "TP-Scraping-S03/1.0 "
    "(projet pedagogique IPSSI)"
)

# Langue souhaitée
ACCEPT_LANGUAGE = (
    "en-CA,en;q=0.9,"
    "fr-CA;q=0.8,"
    "fr;q=0.7"
)