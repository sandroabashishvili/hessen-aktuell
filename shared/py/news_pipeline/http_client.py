from __future__ import annotations

from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_USER_AGENT = "HessenAktuellBot/0.1 (+local MVP source monitor)"


def fetch_text(url: str, timeout: int = 15) -> str | None:
    request = Request(url, headers={"User-Agent": DEFAULT_USER_AGENT})
    try:
        with urlopen(request, timeout=timeout) as response:
            content_type = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(content_type, errors="replace")
    except (HTTPError, URLError, TimeoutError, OSError):
        return None
