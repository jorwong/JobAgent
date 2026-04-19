"""Fetch full job descriptions and apply links for all scraped jobs."""

import asyncio
import json
import re
import sys

sys.path.insert(0, "src")

import httpx
from bs4 import BeautifulSoup
from jobagent.scrapers.linkedin import search_jobs, JobListing

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


async def fetch_job_detail(client: httpx.AsyncClient, job: JobListing) -> dict:
    """Fetch a single job page and extract description + apply link."""
    result = {
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "posted": job.posted,
        "listing_url": job.url,
        "apply_url": "",
        "description": "",
    }
    try:
        resp = await client.get(job.url, headers=HEADERS)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        # Job description
        desc_el = soup.select_one("div.show-more-less-html__markup")
        if desc_el:
            result["description"] = _clean(desc_el.get_text(separator="\n"))

        # Apply link — LinkedIn sometimes has an external apply button
        apply_btn = soup.select_one("a.apply-button") or soup.select_one(
            'a[data-tracking-control-name="public_jobs_apply-link-offsite_sign-up-modal"]'
        )
        if apply_btn and apply_btn.get("href"):
            result["apply_url"] = apply_btn["href"].split("?")[0]

        # Fallback: look for applyUrl in embedded JSON
        if not result["apply_url"]:
            for script in soup.select('script[type="application/ld+json"]'):
                try:
                    data = json.loads(script.string or "")
                    if isinstance(data, dict):
                        apply = data.get("directApply")
                        url = data.get("url", "")
                        if url:
                            result["apply_url"] = url
                except (json.JSONDecodeError, TypeError):
                    pass

        # Another fallback: any offsite apply link
        if not result["apply_url"]:
            offsite = soup.select_one('a[href*="applyUrl"]') or soup.find(
                "a", string=re.compile(r"apply", re.I)
            )
            if offsite and offsite.get("href"):
                href = offsite["href"]
                if "linkedin.com" not in href:
                    result["apply_url"] = href

        if not result["apply_url"]:
            result["apply_url"] = job.url  # fallback to listing page

    except Exception as e:
        result["description"] = f"[Error fetching: {e}]"
        result["apply_url"] = job.url

    return result


async def main():
    queries = [
        ("Software Engineer", "Singapore"),
        ("DevOps Engineer", "Singapore"),
    ]

    all_jobs: list[JobListing] = []
    for keywords, location in queries:
        try:
            jobs = await search_jobs(keywords, location, max_results=15)
            all_jobs.extend(jobs)
        except Exception as e:
            print(f"Error searching '{keywords}': {e}")

    print(f"\nFetching details for {len(all_jobs)} jobs...\n")

    sem = asyncio.Semaphore(5)  # rate limit

    async def fetch_with_sem(client, job):
        async with sem:
            await asyncio.sleep(0.5)  # be polite
            return await fetch_job_detail(client, job)

    async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
        tasks = [fetch_with_sem(client, job) for job in all_jobs]
        results = await asyncio.gather(*tasks)

    for i, r in enumerate(results, 1):
        print(f"{'='*80}")
        print(f"[{i:2d}] {r['title']}")
        print(f"     Company:  {r['company']}")
        print(f"     Location: {r['location']}")
        print(f"     Posted:   {r['posted']}")
        print(f"     Apply:    {r['apply_url']}")
        print(f"{'─'*80}")
        desc = r["description"]
        if len(desc) > 1500:
            desc = desc[:1500] + "..."
        print(f"     {desc}")
        print()

    # Save full results to JSON for later use
    with open("jobs_scraped.json", "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nSaved full details to jobs_scraped.json ({len(results)} jobs)")


if __name__ == "__main__":
    asyncio.run(main())
