"""Async HTTP client with User-Agent rotation, throttling, and retry logic."""

import asyncio
import logging
import random

import httpx

logger = logging.getLogger(__name__)

# Common browser User-Agent strings for rotation
USER_AGENTS: list[str] = [
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.2 Safari/605.1.15"
    ),
    ("Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0"),
]

# HTTP status codes that trigger a retry
RETRYABLE_STATUS_CODES: frozenset[int] = frozenset({429, 500, 502, 503, 504})

DEFAULT_TIMEOUT_SECONDS: float = 30.0
DEFAULT_THROTTLE_SECONDS: float = 2.0
DEFAULT_MAX_RETRIES: int = 3
DEFAULT_RETRY_BACKOFF_SECONDS: float = 5.0


def _random_user_agent() -> str:
    """Return a randomly selected User-Agent string."""
    return random.choice(USER_AGENTS)  # noqa: S311


class ScraperHttpClient:
    """HTTP client configured for web scraping with polite request patterns."""

    def __init__(
        self,
        *,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        throttle_seconds: float = DEFAULT_THROTTLE_SECONDS,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_backoff: float = DEFAULT_RETRY_BACKOFF_SECONDS,
    ) -> None:
        self._timeout = timeout
        self._throttle_seconds = throttle_seconds
        self._max_retries = max_retries
        self._retry_backoff = retry_backoff
        self._client: httpx.AsyncClient | None = None
        self._last_request_time: float = 0.0

    async def _ensure_client(self) -> httpx.AsyncClient:
        """Lazily create the async HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self._timeout),
                follow_redirects=True,
                headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                },
            )
        return self._client

    async def _throttle(self) -> None:
        """Enforce minimum delay between requests."""
        now = asyncio.get_event_loop().time()
        elapsed = now - self._last_request_time
        if elapsed < self._throttle_seconds:
            delay = self._throttle_seconds - elapsed
            logger.debug("Throttling request for %.2f seconds", delay)
            await asyncio.sleep(delay)
        self._last_request_time = asyncio.get_event_loop().time()

    async def fetch(self, url: str) -> str:
        """Fetch a URL and return the response body as text.

        Retries on transient failures with exponential backoff.

        Args:
            url: The URL to fetch.

        Returns:
            The response body text.

        Raises:
            httpx.HTTPStatusError: If the request fails after all retries.
        """
        client = await self._ensure_client()
        last_error: Exception | None = None

        for attempt in range(self._max_retries):
            await self._throttle()

            headers = {"User-Agent": _random_user_agent()}

            try:
                response = await client.get(url, headers=headers)

                if response.status_code in RETRYABLE_STATUS_CODES:
                    wait = self._retry_backoff * (2**attempt)
                    logger.warning(
                        "Retryable status %d for %s (attempt %d/%d), waiting %.1fs",
                        response.status_code,
                        url,
                        attempt + 1,
                        self._max_retries,
                        wait,
                    )
                    await asyncio.sleep(wait)
                    continue

                response.raise_for_status()
                return response.text

            except httpx.TimeoutException as exc:
                last_error = exc
                wait = self._retry_backoff * (2**attempt)
                logger.warning(
                    "Timeout for %s (attempt %d/%d), waiting %.1fs",
                    url,
                    attempt + 1,
                    self._max_retries,
                    wait,
                )
                await asyncio.sleep(wait)

            except httpx.HTTPStatusError as exc:
                # Non-retryable HTTP error
                logger.error("HTTP error %d for %s: %s", exc.response.status_code, url, exc)
                raise

            except httpx.HTTPError as exc:
                last_error = exc
                wait = self._retry_backoff * (2**attempt)
                logger.warning(
                    "HTTP error for %s (attempt %d/%d): %s, waiting %.1fs",
                    url,
                    attempt + 1,
                    self._max_retries,
                    exc,
                    wait,
                )
                await asyncio.sleep(wait)

        msg = f"Failed to fetch {url} after {self._max_retries} retries"
        logger.error(msg)
        if last_error:
            raise last_error
        raise httpx.HTTPError(msg)

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
