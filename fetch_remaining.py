"""Retry fetching job details for ones that got 429'd."""

import asyncio
import json
import re
import sys

sys.path.insert(0, "src")

import httpx
from bs4 import BeautifulSoup

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


async def fetch_one(client, job, idx):
    url = job["listing_url"]
    try:
        resp = await client.get(url, headers=HEADERS)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        desc_el = soup.select_one("div.show-more-less-html__markup")
        if desc_el:
            job["description"] = _clean(desc_el.get_text(separator="\n"))

        # Apply link from ld+json
        for script in soup.select('script[type="application/ld+json"]'):
            try:
                data = json.loads(script.string or "")
                if isinstance(data, dict) and data.get("url"):
                    job["apply_url"] = data["url"]
            except (json.JSONDecodeError, TypeError):
                pass

        print(f"  OK [{idx+1:2d}] {job['title']} @ {job['company']}")
    except Exception as e:
        print(f"  FAIL [{idx+1:2d}] {job['title']} — {e}")
    return job


async def main():
    with open("jobs_scraped.json") as f:
        jobs = json.load(f)

    failed = [(i, j) for i, j in enumerate(jobs) if j["description"].startswith("[Error")]
    print(f"Retrying {len(failed)} failed jobs with 3s delays...\n")

    async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
        for idx, (i, job) in enumerate(failed):
            if idx > 0:
                await asyncio.sleep(3)
            jobs[i] = await fetch_one(client, job, i)

    with open("jobs_scraped.json", "w") as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)

    # Print all results
    print(f"\n{'='*80}")
    print(f"  FULL RESULTS ({len(jobs)} jobs)")
    print(f"{'='*80}\n")
    for i, r in enumerate(jobs, 1):
        status = "X" if r["description"].startswith("[Error") else "OK"
        print(f"[{i:2d}] [{status:>4s}] {r['title']}")
        print(f"      Company:  {r['company']} | {r['location']}")
        print(f"      Posted:   {r['posted']}")
        print(f"      Apply:    {r['apply_url']}")
        desc = r["description"]
        if not desc.startswith("[Error"):
            if len(desc) > 800:
                desc = desc[:800] + "..."
            print(f"      JD: {desc}")
        print()

    ok = sum(1 for j in jobs if not j["description"].startswith("[Error"))
    print(f"Successfully fetched: {ok}/{len(jobs)}")


if __name__ == "__main__":
    asyncio.run(main())
