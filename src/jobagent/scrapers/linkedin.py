"""LinkedIn public job search scraper."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from urllib.parse import quote_plus

import httpx
from bs4 import BeautifulSoup


@dataclass
class JobListing:
    title: str
    company: str
    location: str
    url: str
    posted: str = ""
    description_snippet: str = ""


def build_search_url(
    keywords: str,
    location: str = "Singapore",
    start: int = 0,
) -> str:
    """Build a LinkedIn public job search URL."""
    base = "https://www.linkedin.com/jobs/search"
    params = (
        f"?keywords={quote_plus(keywords)}"
        f"&location={quote_plus(location)}"
        f"&start={start}"
        f"&position=1&pageNum=0"
    )
    return base + params


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def parse_job_cards(html: str) -> list[JobListing]:
    """Parse job cards from LinkedIn public search HTML."""
    soup = BeautifulSoup(html, "lxml")
    jobs: list[JobListing] = []

    cards = soup.select("div.base-card")
    for card in cards:
        title_el = card.select_one("h3.base-search-card__title")
        company_el = card.select_one("h4.base-search-card__subtitle a")
        location_el = card.select_one("span.job-search-card__location")
        link_el = card.select_one("a.base-card__full-link")
        time_el = card.select_one("time")

        if not title_el or not link_el:
            continue

        jobs.append(
            JobListing(
                title=_clean(title_el.get_text()),
                company=_clean(company_el.get_text()) if company_el else "Unknown",
                location=_clean(location_el.get_text()) if location_el else "",
                url=link_el.get("href", "").split("?")[0],
                posted=_clean(time_el.get_text()) if time_el else "",
            )
        )

    return jobs


async def search_jobs(
    keywords: str,
    location: str = "Singapore",
    max_results: int = 25,
) -> list[JobListing]:
    """Search LinkedIn public job listings."""
    url = build_search_url(keywords, location)
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }
    async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
        resp = await client.get(url, headers=headers)
        resp.raise_for_status()

    jobs = parse_job_cards(resp.text)
    return jobs[:max_results]
