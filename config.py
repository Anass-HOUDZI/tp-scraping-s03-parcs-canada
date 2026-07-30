LIST_URL = (
    "https://parks.canada.ca/"
    "pn-np/recherche-parcs-parks-search"
)

SOURCE_URL = "https://parks.canada.ca/pn-np"

OUTPUT_JSONL = "samples/sample_output.jsonl"

LOG_FILE = "logs/scraper.log"

MAX_OBJECTS = 60
REQUEST_DELAY = 1
REQUEST_TIMEOUT = 30

USER_AGENT = (
    "TP-Scraping-S03/1.0 "
    "(projet pédagogique IPSSI)"
)

ACCEPT_LANGUAGE = (
    "en-CA,en;q=0.9,"
    "fr-CA;q=0.8,fr;q=0.7"
)