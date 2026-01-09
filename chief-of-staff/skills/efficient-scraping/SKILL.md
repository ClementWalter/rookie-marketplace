---
name: Efficient Web Scraping
description: This skill should be used when agents need to extract data from websites, APIs, or web pages. Use when scraping content, fetching structured data, or processing web responses. Key principle: always use programmatic extraction with uv scripts instead of reading thousands of lines into context.
version: 1.0.0
---

# Efficient Web Scraping for Agents

Extract data from websites efficiently using uv scripts. Never bloat context by reading raw HTML/JSON into conversation.

## Core Principle

### Programmatic extraction > Reading thousands of lines

| Approach                      | Tokens  | Quality   | Speed |
| ----------------------------- | ------- | --------- | ----- |
| Read raw HTML into context    | 50,000+ | Poor      | Slow  |
| uv script + structured output | ~200    | Excellent | Fast  |

## When This Applies

- Scraping website content (articles, profiles, feeds)
- Fetching API responses
- Extracting data from web services
- Processing RSS/JSON feeds
- Crawling multiple pages

## The Pattern

### 1. Identify Target Data

Before writing code, specify exactly what you need:

```markdown
**Target**: LinkedIn profile data
**Fields needed**: name, headline, recent posts (last 5)
**Output format**: JSON
```

### 2. Write a uv Script

Create a single-file Python script using uv inline metadata:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests", "beautifulsoup4", "lxml"]
# ///
"""
Extract specific data from [target].
Output: Structured JSON to stdout.
"""
import json
import sys
import requests
from bs4 import BeautifulSoup

def extract_data(url: str) -> dict:
    """Extract target fields from URL."""
    response = requests.get(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; research)"
    })
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")

    # Extract ONLY the fields you need
    return {
        "title": soup.find("h1").get_text(strip=True) if soup.find("h1") else None,
        "description": soup.find("meta", {"name": "description"})["content"]
                       if soup.find("meta", {"name": "description"}) else None,
        # Add only needed fields
    }

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else None
    if not url:
        print("Usage: script.py <url>", file=sys.stderr)
        sys.exit(1)

    result = extract_data(url)
    print(json.dumps(result, indent=2, ensure_ascii=False))
```

### 3. Run and Use Output

```bash
uv run script.py "https://example.com/page" > output.json
```

Then read only the small JSON output (~200 tokens) instead of the full page (~50,000 tokens).

## Common Patterns

### Pattern A: API with Authentication

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests"]
# ///
import json
import os
import requests

def fetch_from_api(endpoint: str) -> dict:
    token = os.environ.get("API_TOKEN")
    response = requests.get(
        endpoint,
        headers={"Authorization": f"Bearer {token}"}
    )
    response.raise_for_status()

    # Extract only needed fields from potentially large response
    data = response.json()
    return {
        "items": [
            {"id": item["id"], "title": item["title"]}
            for item in data.get("items", [])[:10]  # Limit
        ],
        "total": data.get("total_count", 0)
    }
```

### Pattern B: Multiple Pages

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests", "beautifulsoup4"]
# ///
import json
import sys
import requests
from bs4 import BeautifulSoup

def scrape_list_page(url: str) -> list[dict]:
    """Scrape paginated list, return structured data."""
    results = []
    page = 1

    while len(results) < 50:  # Hard limit
        response = requests.get(f"{url}?page={page}")
        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.select(".item-class")  # Adjust selector

        if not items:
            break

        for item in items:
            results.append({
                "title": item.select_one(".title").get_text(strip=True),
                "link": item.select_one("a")["href"],
            })

        page += 1

    return results

if __name__ == "__main__":
    print(json.dumps(scrape_list_page(sys.argv[1]), indent=2))
```

### Pattern C: Browser-Required Sites (Playwright)

For JavaScript-rendered content:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright"]
# ///
import json
import sys
from playwright.sync_api import sync_playwright

def extract_dynamic_content(url: str) -> dict:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_selector(".content-loaded")

        # Extract only what you need
        result = {
            "title": page.title(),
            "content": page.locator(".main-content").text_content()[:1000],
        }

        browser.close()
        return result

if __name__ == "__main__":
    print(json.dumps(extract_dynamic_content(sys.argv[1]), indent=2))
```

## Best Practices

### DO

- **Specify exact fields needed** before writing script
- **Limit results** (e.g., `[:10]`, `< 50 items`)
- **Output structured JSON** for easy parsing
- **Handle errors gracefully** with try/except
- **Add rate limiting** for multiple requests
- **Use selectors** (CSS/XPath) not regex for HTML

### DON'T

- Read full page HTML into context
- Fetch data you won't use
- Skip error handling
- Make unlimited requests
- Parse HTML with regex

## Script Location

Reusable scraping scripts are in this skill's scripts directory:

```text
chief-of-staff/skills/efficient-scraping/scripts/
└── web-extract.py    # Generic web content extractor
```

### Using web-extract.py

```bash
# Basic metadata extraction
uv run scripts/web-extract.py "https://example.com"

# Extract specific elements
uv run scripts/web-extract.py "https://example.com" --selector ".article" --fields "text,href"
```

Output is always minimal JSON - no raw HTML in context.

## Error Handling

Always wrap scraping in try/except and return structured errors:

```python
try:
    result = extract_data(url)
    print(json.dumps(result, indent=2))
except requests.exceptions.HTTPError as e:
    print(json.dumps({"error": f"HTTP {e.response.status_code}", "url": url}))
    sys.exit(1)
except Exception as e:
    print(json.dumps({"error": str(e), "type": type(e).__name__}))
    sys.exit(1)
```

## Token Savings Example

| Scenario                 | Without Script | With Script |
| ------------------------ | -------------- | ----------- |
| LinkedIn profile page    | ~45,000 tokens | ~150 tokens |
| Twitter feed (20 tweets) | ~30,000 tokens | ~800 tokens |
| API response (100 items) | ~20,000 tokens | ~500 tokens |

**10-100x token reduction** = faster, cheaper, better context for reasoning.

## Quick Reference

```markdown
## Scraping Checklist

- [ ] Define exactly what fields are needed
- [ ] Write uv script with inline dependencies
- [ ] Extract ONLY needed fields
- [ ] Output structured JSON
- [ ] Run script, read JSON output (not raw HTML)
- [ ] Handle errors gracefully
```
