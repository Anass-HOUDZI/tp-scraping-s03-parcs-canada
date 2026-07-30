import time
from typing import Optional

import requests


class Fetcher:
    """
    Client HTTP chargé de télécharger les pages.
    """

    def __init__(
        self,
        user_agent: str,
        accept_language: str,
        delay: float = 1.0,
        timeout: int = 30,
        logger=None,
    ) -> None:
        self.delay = max(0.0, delay)
        self.timeout = timeout
        self.logger = logger

        self.session = requests.Session()

        self.session.headers.update(
            {
                "User-Agent": user_agent,
                "Accept-Language": accept_language,
                "Accept": (
                    "text/html,"
                    "application/xhtml+xml"
                ),
            }
        )

    def fetch_page(self, url: str) -> Optional[str]:
        """
        Télécharge une page et retourne son HTML.
        """

        if self.delay:
            time.sleep(self.delay)

        try:
            if self.logger:
                self.logger.info(
                    "Téléchargement : %s",
                    url,
                )

            response = self.session.get(
                url,
                timeout=self.timeout,
                allow_redirects=True,
            )

            response.raise_for_status()

            response.encoding = (
                response.apparent_encoding
                or response.encoding
            )

            return response.text

        except requests.RequestException as error:
            if self.logger:
                self.logger.error(
                    "Échec HTTP pour %s : %s",
                    url,
                    error,
                )

            return None

    def close(self) -> None:
        self.session.close()