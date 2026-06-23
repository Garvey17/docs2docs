from bs4 import BeautifulSoup
import re
from openai import OpenAI
from config.config import settings
import logging
from typing import Literal
from crawler.schema import RawPage
from organiser.schema import OrganisedDocs, ClassifiedContent

logging.basicConfig(
    level="INFO"
)
logger = logging.getLogger(__name__)

client= OpenAI(
    api_key=settings.openai_api_key
)

CONTENT_KEYWORDS = [
    "content",
    "docs",
    "documentation",
    "main",
    "article",
    "markdown",
    "page",
]


def find_content_container(soup: BeautifulSoup):
    # Try semantic HTML first
    for selector in ["main", "article"]:
        element = soup.select_one(selector)
        if element:
            return element

    # Then search divs by id/class keywords
    for div in soup.find_all("div"):
        id_value = (div.get("id") or "").lower()

        class_value = " ".join(
            cls.lower()
            for cls in div.get("class", [])
        )

        searchable = f"{id_value} {class_value}"

        if any(
            keyword in searchable
            for keyword in CONTENT_KEYWORDS
        ):
            return div

    return None

def extract_clean_text(html: str) -> str:
    if not html or not html.strip():
        return ""
    soup = BeautifulSoup(html, "lxml")

    noise_tags = ["script", "style", "nav", "footer", "header", "aside"]
    for tag in noise_tags:
        for element in soup.find_all(tag):
            element.decompose()

    #main tag check
    container = find_content_container(soup) or soup.find("body") or soup
    text = container.get_text(separator="\n", strip=True)
    return re.sub(r"\n{3,}", "\n\n", text)

    

SYSTEM_PROMPT = """
You are a documentation page classifier.

Your task is to classify a documentation page into exactly one of the following categories:

installation
getting_started
features
discard

You will receive:

A page title
The page content

Classification rules:

installation
Return exactly:

installation

when the page primarily explains how to install, set up, configure, download, or initialize a package, library, framework, SDK, API, or technology.

Common indicators:

pip install
npm install
yarn add
pnpm add
cargo add
brew install
installation requirements
setup instructions
environment setup
prerequisites
getting_started
Return exactly:

getting_started

when the page is intended for new users and provides introductory guidance, quickstarts, tutorials, first examples, basic usage instructions, or onboarding material.

Common indicators:

Quick Start
Getting Started
First Application
Hello World
Basic Usage
Your First Project
Tutorial
features
Return exactly:

features

when the page describes one or more capabilities, modules, components, APIs, concepts, integrations, workflows, or functionality of the technology.

Examples:

Authentication
Routing
State Management
Memory
Agents
Tools
Vector Stores
Streaming
Middleware
Caching
Logging
discard
Return exactly:

discard

when the page does not clearly belong to installation, getting_started, or features.

Examples:

Blog posts
Marketing pages
Changelogs
Release notes
Careers pages
Pricing pages
Contact pages
Legal pages
Community pages

Priority rules:

Base the classification primarily on the content, not the title.
If both installation and getting_started are present, return installation.
If the page explains a specific capability or concept, return features.
If uncertain, return discard.

Output requirements:

Return exactly one word.
Do not explain your reasoning.
Do not include punctuation.
Do not include markdown.
Valid outputs are only:

installation
getting_started
features
discard
"""
def classify_page(title: str, text: str) -> Literal["installation", "getting_started", "features", "discard"]:

    text_input = f"Title: {title} \n\n {text [:2000]}"
    message = [
        {"role":"system", "content":SYSTEM_PROMPT},
        {"role":"user", "content":text_input}
    ]

    response = client.chat.completions.create(
        model="gpt-5-nano",
        messages=message,
    )

    category = response.choices[0].message.content.strip()
    if category == "installation":
        return "installation"
    elif category == "getting_started":
        return "getting_started"
    elif category == "features":
        return "features"
    else:
        return "discard"

#testing

# title = "Installing LangChain"
# text = """To install LangChain, run the following command:

#         pip install langchain

#         For OpenAI integrations:

#         pip install langchain-openai

#         Verify your installation by running:

#         python -c "import langchain; print(langchain.__version__)"

#         You can also install from source using:

#         git clone https://github.com/langchain-ai/langchain.git"""

# print(classify_page(title, text))


def organise(pages: list[RawPage]) -> OrganisedDocs | None:
    classified_contents: list[ClassifiedContent] = []
    for page in pages:
        try:

            url = page.url
            title = page.title
            html = page.html

            cleaned_text = extract_clean_text(html)

            section = classify_page(title=title, text=cleaned_text) 

            
            if section == "discard":
                continue

            classified_content = ClassifiedContent(
                url=url,
                section=section,
                raw_text=cleaned_text,
                source_title=title
            )

            classified_contents.append(classified_content)
        except Exception as e:
            logger.error(f"Failed to process {url}: {e}")
        
    
    organised = OrganisedDocs(installation= [content for content in classified_contents if content.section == "installation"],
        getting_started= [content for content in classified_contents if content.section == "getting_started" ],
        features= [content for content in classified_contents if content.section == "features"])
    if not any([organised.installation, organised.getting_started, organised.features]):
        logger.warning("Organiser produced no usable content from any page")
        return None
    
    logger.info(f"Organised: installation={len(organised.installation)}, getting_started={len(organised.getting_started)}, features={len(organised.features)}")
    return organised
    