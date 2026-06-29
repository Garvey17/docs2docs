# Docs to Docs

An AI pipeline that scrapes any documentation site and converts it into a compact, downloadable Word guide covering installation, getting started, and features.

---

## Overview

Docs to Docs takes a documentation URL, crawls the relevant pages, classifies content using an LLM, rewrites it into a structured guide, and delivers a formatted `.docx` file — all in one click from a Chrome extension.

---

## Architecture

```
Chrome Extension
      │ POST /generate { url, package_name }
      ▼
AWS Application Load Balancer
      │
      ▼
AWS ECS Fargate (FastAPI + Playwright + Pipeline)
      │
      ├── Crawler       → discovers and fetches doc pages
      ├── Organiser     → classifies pages into sections
      ├── Writer        → rewrites content into guide format
      └── Output Service → renders .docx file
                │
                ▼
          AWS S3 → presigned URL → Chrome Extension download
```

---

## Pipeline Stages

**Crawler** — Launches headless Chromium, discovers sidebar/nav links, scores URLs by relevance keywords (`install`, `quickstart`, `features`), fetches and caches the highest-scoring pages.

**Organiser** — Strips noise (nav, footer, scripts), extracts main content, classifies each page via LLM into `installation`, `getting_started`, `features`, or `discard`. Discards irrelevant pages.

**Writer** — Generates a draft per section, runs each through a critic that checks quality criteria (code blocks, numbered steps, usage examples), revises once if needed.

**Output Service** — Renders a formatted `.docx` with title page, section headings, code blocks, and lists. Uploads to S3 and returns a presigned download URL.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Web framework | FastAPI |
| Browser automation | Playwright (Chromium) |
| HTML parsing | BeautifulSoup4 + lxml |
| LLM | OpenAI GPT |
| Document generation | python-docx |
| Cloud storage | AWS S3 |
| Deployment | AWS ECS Fargate + ECR + ALB |
| Frontend | Chrome Extension (Manifest V3) |

---

## Project Structure

```
docs_to_docs/
├── main.py                  # FastAPI entry point
├── pipeline.py              # Pipeline orchestration
├── config/config.py         # pydantic-settings config
├── crawler/                 # Playwright crawler + URL scoring
├── organiser/               # Content extraction + LLM classification
├── writer/                  # Draft generation + critic/revision loop
├── services/                # .docx rendering + S3 upload
├── extension/               # Chrome extension (popup + background)
├── Dockerfile
└── requirements.txt
```

---

## Getting Started

```bash
# Clone and setup
git clone https://github.com/yourusername/docs-to-docs.git
cd docs-to-docs
python -m venv .venv && .venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium

# Configure
cp .env.example .env  # fill in your keys

# Run
python main.py
# Visit http://localhost:8000/docs
```

---

## Configuration

| Variable | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | Yes | OpenAI API key |
| `AWS_ACCESS_KEY_ID` | Yes | AWS access key |
| `AWS_SECRET_ACCESS_KEY` | Yes | AWS secret key |
| `AWS_REGION` | No (default `us-east-1`) | AWS region |
| `S3_BUCKET_NAME` | Yes | S3 bucket for output files |
| `MAX_PAGES` | No (default `30`) | Max pages to crawl per run |

---

## API Reference

### `GET /health`
Health check. Returns `{ "message": "Health check passes, app is healthy" }`.

### `POST /generate`

**Request:**
```json
{ "url": "https://docs.crawl4ai.com", "package_name": "crawl4ai" }
```

**Response:**
```json
{
  "status": "200",
  "package_name": "crawl4ai",
  "download_url": "https://your-bucket.s3.amazonaws.com/guides/crawl4ai_guide.docx?..."
}
```

`package_name` is optional — derived from the URL domain if omitted. Requests take 2-5 minutes. Download URL is valid for 1 hour.

---

## Chrome Extension

1. `chrome://extensions` → enable **Developer mode** → **Load unpacked** → select `extension/`
2. Navigate to any docs site → click the extension icon → click **Generate Guide**
3. A browser notification appears when ready and the file downloads automatically

---

## Deployment

```bash
# Build and push to ECR
docker build -t docs-to-docs .
aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.eu-west-2.amazonaws.com
docker tag docs-to-docs:latest <account-id>.dkr.ecr.eu-west-2.amazonaws.com/docs-to-docs:latest
docker push <account-id>.dkr.ecr.eu-west-2.amazonaws.com/docs-to-docs:latest
```

To deploy a new version: ECS → Services → `docs-to-docs-service` → **Update** → check **Force new deployment**.

---

## Limitations

- Sites that actively block headless browsers (Cloudflare-protected) may return incomplete content
- Presigned download URLs expire after 1 hour
- Only one pipeline run executes at a time per server instance
- Output is currently English-only
- Very large documentation sites (500+ pages) are capped at `MAX_PAGES` to control cost and latency

---

## License

MIT