"""
Government Session Adapter for KrishiMitra AI.
Provides:
- Resilient SSL handling for state government websites with legacy ciphers (SECLEVEL=1)
- Automatic fallback for internal/NIC self-signed certificates
- Politeness delay & per-domain rate limiting
- Automatic robots.txt compliance checking
- Exponential backoff retry logic
"""

import time
import ssl
import urllib.robotparser
from urllib.parse import urlparse, urljoin
from typing import Dict, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import urllib3
from core.config import (
    CRAWLER_USER_AGENT,
    CRAWLER_TIMEOUT_SECONDS,
    CRAWLER_POLITENESS_DELAY,
    CRAWLER_MAX_RETRIES
)
from core.logger import get_logger

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logger = get_logger("krishimitra.crawler.session")

class GovernmentTLSAdapter(HTTPAdapter):
    """
    Custom HTTPAdapter configured with relaxed SSL security level (SECLEVEL=1)
    to support older Kerala government servers using 1024-bit DH keys.
    """
    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        try:
            ctx.set_ciphers("DEFAULT:@SECLEVEL=1")
        except Exception:
            pass
        kwargs["ssl_context"] = ctx
        return super().init_poolmanager(*args, **kwargs)

class GovernmentSession:
    def __init__(self):
        self.last_request_times: Dict[str, float] = {}
        self.robots_cache: Dict[str, urllib.robotparser.RobotFileParser] = {}
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        s = requests.Session()
        retries = Retry(
            total=CRAWLER_MAX_RETRIES,
            backoff_factor=1.0,
            status_forcelist=[429, 500, 502, 503, 504],
            raise_on_status=False
        )

        adapter = GovernmentTLSAdapter(max_retries=retries)
        s.mount("https://", adapter)
        s.mount("http://", adapter)

        s.headers.update({
            "User-Agent": CRAWLER_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,ml;q=0.8",
            "Connection": "keep-alive"
        })
        return s

    def _wait_for_politeness(self, domain: str):
        now = time.time()
        if domain in self.last_request_times:
            elapsed = now - self.last_request_times[domain]
            if elapsed < CRAWLER_POLITENESS_DELAY:
                time.sleep(CRAWLER_POLITENESS_DELAY - elapsed)
        self.last_request_times[domain] = time.time()

    def is_allowed_by_robots(self, url: str) -> bool:
        """Checks if URL path is permitted by robots.txt."""
        parsed = urlparse(url)
        domain = f"{parsed.scheme}://{parsed.netloc}"
        if domain not in self.robots_cache:
            rp = urllib.robotparser.RobotFileParser()
            robots_url = urljoin(domain, "/robots.txt")
            try:
                resp = self.session.get(robots_url, timeout=5, verify=False)
                if resp.status_code == 200:
                    rp.parse(resp.text.splitlines())
                else:
                    rp.allow_all = True
            except Exception:
                rp.allow_all = True
            self.robots_cache[domain] = rp

        rp = self.robots_cache[domain]
        allowed = rp.can_fetch(CRAWLER_USER_AGENT, url)
        if not allowed:
            logger.warning(f"URL disallowed by robots.txt: {url}")
        return allowed

    def get(self, url: str, timeout: Optional[int] = None, check_robots: bool = True, **kwargs) -> requests.Response:
        """Performs a polite, resilient GET request."""
        parsed = urlparse(url)
        domain = parsed.netloc

        if check_robots and not self.is_allowed_by_robots(url):
            raise PermissionError(f"Crawling forbidden by robots.txt: {url}")

        self._wait_for_politeness(domain)
        to = timeout or CRAWLER_TIMEOUT_SECONDS

        try:
            return self.session.get(url, timeout=to, verify=False, allow_redirects=True, **kwargs)
        except (ssl.SSLError, requests.exceptions.SSLError) as ssl_err:
            logger.warning(f"SSL issue for {url}: {ssl_err}. Resetting session and retrying once...")
            self.session = self._create_session()
            return self.session.get(url, timeout=to, verify=False, allow_redirects=True, **kwargs)
        except Exception as e:
            logger.warning(f"Request failed for {url}: {e}")
            raise e
