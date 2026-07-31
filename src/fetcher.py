from __future__ import annotations

import random
import time
from typing import Optional

import requests

RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


class Fetcher:

    def __init__(
        self,
        user_agent: str,
        accept_language: str,
        delay: float = 1.0,
        timeout: float = 30,
        max_retries: int = 4,
        backoff_factor: float = 1.0,
        logger=None,
    ) -> None:
        self.delay = max(0.0, delay)
        self.timeout = max(0.1, timeout)
        self.max_retries = max(1, max_retries)
        self.backoff_factor = max(0.0, backoff_factor)
        self.logger = logger
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": user_agent,
                "Accept-Language": accept_language,
                "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
            }
        )

    def _wait_before_request(self) -> None:
        if self.delay:
            time.sleep(self.delay)

    def _backoff_seconds(self, attempt: int, retry_after: str | None) -> float:
        if retry_after:
            try:
                return max(float(retry_after), 0.0)
            except ValueError:
                pass
        exponential = self.backoff_factor * (2 ** (attempt - 1))
        jitter = random.uniform(0, 0.25)
        return exponential + jitter

    def fetch_page(self, url: str) -> Optional[str]:
        for attempt in range(1, self.max_retries + 1):
            self._wait_before_request()
            try:
                if self.logger:
                    self.logger.info(
                        "GET %s | tentative %s/%s", url, attempt, self.max_retries
                    )

                response = self.session.get(
                    url,
                    timeout=self.timeout,
                    allow_redirects=True,
                )

                if response.status_code in RETRYABLE_STATUS_CODES:
                    if attempt == self.max_retries:
                        response.raise_for_status()
                    wait = self._backoff_seconds(
                        attempt, response.headers.get("Retry-After")
                    )
                    if self.logger:
                        self.logger.warning(
                            "HTTP %s pour %s ; nouvelle tentative dans %.2f s",
                            response.status_code,
                            url,
                            wait,
                        )
                    time.sleep(wait)
                    continue

                response.raise_for_status()
                response.encoding = response.apparent_encoding or response.encoding
                return response.text

            except (requests.Timeout, requests.ConnectionError) as error:
                if attempt < self.max_retries:
                    wait = self._backoff_seconds(attempt, None)
                    if self.logger:
                        self.logger.warning(
                            "Erreur réseau pour %s : %s ; retry dans %.2f s",
                            url,
                            error,
                            wait,
                        )
                    time.sleep(wait)
                    continue
                if self.logger:
                    self.logger.error("Échec réseau définitif pour %s : %s", url, error)

            except requests.RequestException as error:
                if self.logger:
                    self.logger.error("Échec HTTP non récupérable pour %s : %s", url, error)
                break

        return None

    def close(self) -> None:
        self.session.close()

    def __enter__(self) -> "Fetcher":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()