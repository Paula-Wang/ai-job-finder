import json

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from urllib.parse import urljoin

from app.models.job import Job

BASE_URL = "https://www.fuzu.com"

FUZU_BASE_URLS = [
    ("https://www.fuzu.com/kenya/job/" "computers-software-development"),
    ("https://www.fuzu.com/kenya/job/" "computers-software-development/basic"),
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Safari/537.36"
    )
}


def fetch_page(url):
    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=30,
        )

        response.raise_for_status()

        return response.text

    except requests.RequestException as error:
        print(f"  Fuzu unavailable: {error}")

        return ""


def fetch_job_links(max_pages=3):
    """
    Collect individual Fuzu vacancy URLs from
    multiple pages of the general and basic-level
    IT job listings.
    """
    links = set()

    for base_url in FUZU_BASE_URLS:
        for page in range(1, max_pages + 1):
            if page == 1:
                page_url = base_url
            else:
                page_url = f"{base_url}?page={page}"

            print(f"  Scanning Fuzu page " f"{page}: {page_url}")

            html = fetch_page(page_url)

            if not html:
                continue

            soup = BeautifulSoup(
                html,
                "html.parser",
            )

            page_links = set()

            for link in soup.find_all(
                "a",
                href=True,
            ):
                href = link.get(
                    "href",
                    "",
                )

                if not href.startswith("/kenya/jobs/"):
                    continue

                page_links.add(
                    urljoin(
                        BASE_URL,
                        href,
                    )
                )

            print(f"    Found " f"{len(page_links)} " f"job links.")

            links.update(page_links)

    return links


def extract_job_posting(html):
    """
    Extract Fuzu's structured JobPosting JSON-LD.
    """
    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    scripts = soup.find_all(
        "script",
        type="application/ld+json",
    )

    for script in scripts:
        if not script.string:
            continue

        try:
            data = json.loads(script.string)
        except json.JSONDecodeError:
            continue

        if isinstance(data, dict) and data.get("@type") == "JobPosting":
            return data

    return None


def clean_description(description):
    """
    Convert the HTML description from JSON-LD
    into plain text.
    """
    if not description:
        return ""

    soup = BeautifulSoup(
        description,
        "html.parser",
    )

    return soup.get_text(
        " ",
        strip=True,
    )


def extract_location(data):
    location = data.get("jobLocation")

    if not location:
        return "Kenya"

    if isinstance(location, list):
        location = location[0]

    if not isinstance(location, dict):
        return "Kenya"

    address = location.get("address", {})

    if not isinstance(address, dict):
        return "Kenya"

    city = address.get("addressLocality")

    country = address.get("addressCountry")

    parts = [part for part in [city, country] if part]

    return ", ".join(parts) or "Kenya"


def fetch_fuzu_jobs():
    print("  Finding Fuzu jobs...")

    links = fetch_job_links()

    print(f"  Found {len(links)} " f"unique Fuzu job links.")

    jobs = []

    for url in links:
        html = fetch_page(url)

        if not html:
            continue

        data = extract_job_posting(html)

        if not data:
            print(f"    No JobPosting data: {url}")
            continue

        title = data.get(
            "title",
            "",
        ).strip()

        organization = data.get(
            "hiringOrganization",
            {},
        )

        if isinstance(
            organization,
            dict,
        ):
            company = organization.get(
                "name",
                "",
            ).strip()
        else:
            company = ""

        print(f"    Reading: " f"{title} at {company}")

        description = clean_description(
            data.get(
                "description",
                "",
            )
        )

        date_posted = data.get("datePosted")

        try:
            posted_at = datetime.fromisoformat(date_posted).replace(tzinfo=timezone.utc)
        except (
            TypeError,
            ValueError,
        ):
            posted_at = datetime.now(timezone.utc)

        identifier = data.get(
            "identifier",
            {},
        )

        if isinstance(
            identifier,
            dict,
        ):
            source_id = str(
                identifier.get(
                    "value",
                    url,
                )
            )
        else:
            source_id = url

        job = Job(
            source_id=source_id,
            source="Fuzu Kenya",
            title=title,
            company=company,
            location=extract_location(data),
            description=description,
            tags=[],
            url=url,
            posted_at=posted_at,
        )

        jobs.append(job)

    print(f"  Collected {len(jobs)} " f"Fuzu jobs.")

    return jobs

def inspect_fallback_page(url):
    html = fetch_page(url)

    if not html:
        return

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    print("\n" + "=" * 60)
    print("FUZU FALLBACK PAGE")
    print("=" * 60)

    if soup.title:
        print("\nPAGE TITLE:")
        print(
            soup.title.get_text(
                " ",
                strip=True,
            )
        )

    print("\nHEADINGS:")

    for heading in soup.find_all(
        ["h1", "h2", "h3"]
    ):
        text = heading.get_text(
            " ",
            strip=True,
        )

        if text:
            print(
                heading.name,
                repr(text),
            )

    print("\nPARAGRAPHS:")

    paragraphs = []

    for paragraph in soup.find_all("p"):
        text = paragraph.get_text(
            " ",
            strip=True,
        )

        if text:
            paragraphs.append(text)

    for text in paragraphs[:40]:
        print(repr(text))


if __name__ == "__main__":
    jobs = fetch_fuzu_jobs()

    print()

    for job in jobs:
        print("=" * 60)
        print(f"Title:    {job.title}")
        print(f"Company:  {job.company}")
        print(f"Location: {job.location}")
        print(f"Posted:   {job.posted_at.date()}")
        print(f"URL:      {job.url}")