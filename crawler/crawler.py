from playwright.async_api import async_playwright
import asyncio
from urllib.parse import urlparse
import logging
from datetime import datetime
from schema import RawPage
from utils import score_url_path, get_html_title


logging.basicConfig(
    level="INFO"
)
logger = logging.getLogger(__name__)


# from config.logging_config import get_logger

# logger= get_logger(__name__)
BLOCKED_EXTENSIONS = {
     ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".webp",
    ".pdf",
    ".zip",
    ".css",
    ".js",
    ".ico",
    ".xml",
    ".json",
    ".txt",
}

BLOCKED_PATHS ={
    "/login",
    "/signin",
    "/signup",
    "/register",
    "/logout",
    "/search",
    "/pricing",
    "/contact",
    "/blog",
    "/careers",
    "/jobs",
    "/changelog",
}

def is_valid_doc_link(url:str, base_domain:str) -> bool:
    try:
        parsed = urlparse(url)

        #Same domain check 
        if parsed.netloc != base_domain:
            return False
        
        path = parsed.path.lower()

        #Ignore homepage
        if path in {"", "/"}:
            return False
        
        #ignore fragments
        if parsed.fragment:
            return False
        
        #Ignore assets
        if any(path.endswith(ext) for ext in BLOCKED_EXTENSIONS):
            return False
        
        #Ignore non doc pages
        if any(blocked in path for blocked in BLOCKED_PATHS):
            return False
        
        return True
    except Exception:
        return False

async def discover_doc_links(url: str) -> list[str]:
    async with async_playwright() as p:
        #Starts a new browser instance with chromium

        browser = await p.chromium.launch(headless=True)

        try:
            page = await browser.new_page()

            await page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=60000
            )

            base_domain = urlparse(page.url).netloc

            links = await page.evaluate(
                """
            () => {
                const selectors = [
                    'nav a',
                    'aside a',
                    '[role="navigation"] a',
                    '.sidebar a',
                    '.menu a',
                    '.navigation a',
                    '.nav a',
                    '.toc a',
                    '.docs-sidebar a'
                ];

                const urls = new Set();

                for (const selector of selectors) {
                    document.querySelectorAll(selector).forEach(link => {
                        if (link.href) {
                            urls.add(link.href);
                        }
                    });
                }

                return Array.from(urls);
            }
            """
            )

            candidates = [link for link in links if is_valid_doc_link(link, base_domain)]

            scored = [(score_url_path(link), link) for link in candidates]
            scored = [(s,link) for s,link in scored if s > 0]

            scored.sort(reverse=True)

            return [link for _,link in scored]
        finally:
            await browser.close()

#Local disk caching 
from pathlib import Path
from hashlib import md5

CAHCE_DIR = Path("cache")
CAHCE_DIR.mkdir(exist_ok=True)

def cache_path(url: str) -> Path:
    """
    Convert URL to chache filename
    """
    return CAHCE_DIR / f"{md5(url.encode()).hexdigest()}.html"


async def get_html_then_cache(url: str) -> list[RawPage]:
    links: list[str] = await discover_doc_links(url)
    results: list[RawPage] = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        try:
            page = await browser.new_page()

            for link in links:
                page_cache_path = cache_path(link)

                if page_cache_path.exists():
                    html = page_cache_path.read_text(
                        encoding="utf-8"
                    )
                else:
                    try:
                        await page.goto(
                            link,
                            wait_until="domcontentloaded",
                            timeout=14000,
                        )

                        html = await page.content()

                        page_cache_path.write_text(
                            html,
                            encoding="utf-8",
                        )

                    except Exception as e:
                        logger.error(
                            f"Failed to fetch {link}: {e}"
                        )
                        continue

                title = get_html_title(html, link)

                results.append(
                    RawPage(
                        url=link,
                        title=title,
                        html=html,
                        fetched_at=datetime.now(),
                    )
                )

            return results

        finally:
            await browser.close()   

pages = asyncio.run(get_html_then_cache(
    "https://expressjs.com/en/5x/starter/hello-world/"
))

print(f"Pages fetched: {len(pages)}")

for page in pages[:3]:
    print("-" * 50)
    print(page.title)
    print(page.url)
    print(f"HTML length: {len(page.html)}")

# asyncio.run(get_html_then_cache("https://portfolioadebola.netlify.app/"))      
             


# print(asyncio.run(discover_doc_links("https://docs.crawl4ai.com/"))) #for testing
