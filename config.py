from __future__ import annotations

import os

LIST_URL = os.getenv(
    "PARKS_LIST_URL",
    "https://parks.canada.ca/pn-np/recherche-parcs-parks-search",
)
SOURCE_URL = os.getenv("PARKS_SOURCE_URL", "https://parks.canada.ca/pn-np")

OUTPUT_JSONL = os.getenv("PARKS_OUTPUT_JSONL", "data/parcs_canada.jsonl")
SAMPLE_JSONL = os.getenv("PARKS_SAMPLE_JSONL", "samples/sample_output.jsonl")
LOG_FILE = os.getenv("PARKS_LOG_FILE", "logs/scraper.log")

MAX_OBJECTS = int(os.getenv("PARKS_MAX_OBJECTS", "60"))
REQUEST_DELAY = float(os.getenv("PARKS_REQUEST_DELAY", "1.0"))
REQUEST_TIMEOUT = float(os.getenv("PARKS_REQUEST_TIMEOUT", "30"))
MAX_RETRIES = int(os.getenv("PARKS_MAX_RETRIES", "4"))
BACKOFF_FACTOR = float(os.getenv("PARKS_BACKOFF_FACTOR", "1.0"))

CONTACT_EMAIL = os.getenv("PARKS_CONTACT_EMAIL", "student.scraping@example.com")
USER_AGENT = os.getenv(
    "PARKS_USER_AGENT",
    f"IPSSI-S03-ParksCanada/1.0 (+mailto:{CONTACT_EMAIL})",
)
ACCEPT_LANGUAGE = os.getenv("PARKS_ACCEPT_LANGUAGE", "fr-CA,fr;q=0.9")