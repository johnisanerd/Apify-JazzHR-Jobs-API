"""JazzHR Jobs API: example client.

Searches live job postings across every company hiring on JazzHR
(applytojob.com). You do not need to know a company URL first: leave the
search open and it covers the whole platform.

Get a free Apify API token: https://apify.com?fpr=9n7kx3
Actor: https://apify.com/johnvc/jazzhr-jobs-api?fpr=9n7kx3

Run it:
    uv sync
    cp .env.example .env      # then paste your token into .env
    uv run python jazzhr-jobs-api-example.py

Pick one example:
    uv run python jazzhr-jobs-api-example.py --example jobs
    uv run python jazzhr-jobs-api-example.py --example companies
    uv run python jazzhr-jobs-api-example.py --example urls
    uv run python jazzhr-jobs-api-example.py --example new-jobs
    uv run python jazzhr-jobs-api-example.py --example all
"""

import argparse
import os
import sys

from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()

ACTOR_ID = "johnvc/jazzhr-jobs-api"

# Every run below asks for a small number of rows on purpose. You pay per row
# returned, so keep the first run cheap, confirm the shape of the data, then
# raise maxItems once you know it is what you want.
SMALL = 10


def client() -> ApifyClient:
    token = os.getenv("APIFY_TOKEN")
    if not token or token == "your_apify_api_token_here":
        sys.exit(
            "Set APIFY_TOKEN first. Copy .env.example to .env and paste your token.\n"
            "Get one free: https://apify.com?fpr=9n7kx3"
        )
    return ApifyClient(token)


def rows(api: ApifyClient, run_input: dict, limit: int = 5) -> list[dict]:
    """Run the Actor and return the first rows of its dataset.

    apify-client 3.x returns a typed Run object here, not a dict, so the
    dataset id is an attribute. On 2.x this was run["defaultDatasetId"].
    """
    run = api.actor(ACTOR_ID).call(run_input=run_input)
    return list(api.dataset(run.default_dataset_id).iterate_items(limit=limit))


def run_jobs(api: ApifyClient) -> None:
    """Full job records, filtered the way a real search would be.

    Keywords are matched against the job URL before the posting is opened, so
    filtering here also makes the run cheaper.
    """
    print("\n=== Full job records ===")
    results = rows(api, {
        "keywords": ["nurse", "registered nurse"],
        "location": "TX",
        "employmentType": "FULL_TIME",
        "postedAfter": "2026-01-01",
        "descriptionFormat": "markdown",
        "maxItems": SMALL,
    })
    for job in results:
        location = job.get("locationText") or "location not stated"
        remote = " [remote]" if job.get("isRemote") else ""
        print(f"\n{job.get('title')}{remote}")
        print(f"  {job.get('companyName')} | {location}")
        print(f"  posted {job.get('datePosted')} | expires {job.get('validThrough')}")
        print(f"  apply: {job.get('applyUrl')}")
        description = job.get("descriptionMarkdown") or ""
        if description:
            print(f"  {description[:140].strip()}...")


def run_companies(api: ApifyClient) -> None:
    """Every employer hiring on JazzHR, with a live count of open roles.

    This mode never opens a job page, so it is the cheap way to see who is
    hiring before deciding which boards are worth pulling in full.
    """
    print("\n=== Companies hiring on JazzHR ===")
    results = rows(api, {"outputMode": "companiesOnly", "maxItems": SMALL}, limit=SMALL)
    for company in results:
        titles = ", ".join(company.get("sampleJobTitles") or []) or "no sample titles"
        print(f"{company.get('companySlug'):<28} {company.get('jobCount'):>4} open  {titles[:60]}")


def run_urls(api: ApifyClient) -> None:
    """The job index without descriptions.

    The whole platform index costs only a handful of upstream requests, so this
    is the cheapest way to survey what is out there and pick targets.
    """
    print("\n=== Job index (no descriptions) ===")
    results = rows(api, {"outputMode": "urlsOnly", "maxItems": 25}, limit=SMALL)
    for row in results:
        print(f"{row.get('companySlug'):<24} {row.get('titleFromSlug')}")


def run_new_jobs(api: ApifyClient) -> None:
    """Only postings not seen in an earlier run.

    The Actor remembers job IDs between runs in a named store. Put this on a
    schedule and each run returns just what appeared since the last one. The
    very first run seeds the store, so it returns nothing by design.
    """
    print("\n=== New postings only (delta mode) ===")
    results = rows(api, {
        "newJobsOnly": True,
        "firstRunBehavior": "seedOnly",
        "keywords": ["welder"],
        "deltaStoreName": "jazzhr-example-seen",
        "maxItems": SMALL,
    }, limit=SMALL)
    if not results:
        print("Nothing returned: the first delta run records what exists today.")
        print("Run it again later and only genuinely new postings come back.")
    for job in results:
        print(f"{job.get('title')} at {job.get('companyName')}")


EXAMPLES = {
    "jobs": run_jobs,
    "companies": run_companies,
    "urls": run_urls,
    "new-jobs": run_new_jobs,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="JazzHR Jobs API examples")
    parser.add_argument("--example", choices=[*EXAMPLES, "all"], default="jobs",
                        help="Which example to run (default: jobs)")
    args = parser.parse_args()

    api = client()
    chosen = list(EXAMPLES) if args.example == "all" else [args.example]
    for name in chosen:
        EXAMPLES[name](api)


if __name__ == "__main__":
    main()
