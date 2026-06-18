from bs4 import BeautifulSoup
from urllib.parse import urlparse

html = """
<!DOCTYPE html>
<html>
<head>
    <title>My Docs</title>
</head>
<body>

<header>
    <nav>
        <a href="/">Home</a>
        <a href="/docs/getting-started">Getting Started</a>
        <a href="/docs/api">API Reference</a>
        <a href="/blog">Blog</a>
        <a href="https://github.com/example/project">GitHub</a>
    </nav>
</header>

<div class="layout">

    <aside class="sidebar">
        <ul>
            <li><a href="/docs/introduction">Introduction</a></li>
            <li><a href="/docs/installation">Installation</a></li>
            <li><a href="/docs/configuration">Configuration</a></li>
            <li><a href="/docs/authentication">Authentication</a></li>
            <li><a href="/docs/api/users">Users API</a></li>
            <li><a href="/docs/api/orders">Orders API</a></li>
            <li><a href="#current-section">Current Section</a></li>
            <li><a href="/search">Search</a></li>
        </ul>
    </aside>

    <main>

        <h1>Introduction</h1>

        <p>
            Welcome to the docs.
            <a href="/docs/tutorials/quickstart">
                Quickstart Tutorial
            </a>
        </p>

        <p>
            Download the SDK:
            <a href="/downloads/sdk.zip">SDK</a>
        </p>

        <p>
            OpenAPI spec:
            <a href="/openapi.json">spec</a>
        </p>

        <p>
            External resource:
            <a href="https://stackoverflow.com/questions">
                StackOverflow
            </a>
        </p>

        <img src="/assets/logo.png" />

    </main>

</div>

</body>
</html>
"""
PRIORITY_KEYWORDS = {
    "install": 3,
    "setup": 3,
    "getting-started": 3,
    "getting_started": 3,
    "quickstart": 3,
    "quick-start": 3,
    "usage": 2,
    "guide": 2,
    "tutorial": 2,
    "features": 2,
    "api": 1,
    "reference": 1,
}

def score_url_path(url: str) -> int:
    url = url.lower()
    parsed = urlparse(url)

    best_score = 0
    for p_word, score in PRIORITY_KEYWORDS.items():
        if p_word in parsed.path:
            best_score = max(best_score, score)
        else:
            best_score = best_score
    
    return best_score
        



def get_html_title(html: str, url: str = "") -> str:
    soup = BeautifulSoup(html, "lxml")

    for tag in ("title", "h1"):
        element = soup.find(tag)

        if element:
            text = element.get_text(strip=True)

            if text:
                return text

    return url
    
string = "/installation-guide/"
check = "install" in string
print(check)

