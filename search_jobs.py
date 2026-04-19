"""Quick CLI to search LinkedIn jobs and display results."""

import asyncio
import sys

sys.path.insert(0, "src")

from jobagent.scrapers.linkedin import search_jobs


async def main():
    queries = [
        ("Software Engineer", "Singapore"),
        ("DevOps Engineer", "Singapore"),
    ]

    for keywords, location in queries:
        print(f"\n{'='*80}")
        print(f"  🔍  {keywords} — {location}")
        print(f"{'='*80}\n")

        try:
            jobs = await search_jobs(keywords, location, max_results=15)
        except Exception as e:
            print(f"  Error fetching jobs: {e}")
            continue

        if not jobs:
            print("  No jobs found.")
            continue

        for i, job in enumerate(jobs, 1):
            print(f"  [{i:2d}] {job.title}")
            print(f"       {job.company} | {job.location}")
            if job.posted:
                print(f"       Posted: {job.posted}")
            print(f"       {job.url}")
            print()


if __name__ == "__main__":
    asyncio.run(main())
