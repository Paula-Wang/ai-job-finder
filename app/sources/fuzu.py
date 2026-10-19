import json
import re

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from urllib.parse import urljoin

from app.models.job import Job


BASE_URL = "https://www.fuzu.com"

FUZU_BASE_URLS = [
    (
        "https://www.fuzu.com/kenya/job/"
        "computers-software-development"
    ),
    (
        "https://www.fuzu.com/kenya/job/"
        "computers-software-development/basic"
    ),
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
        print(
            f"  Fuzu unavailable: {error}"
        )

        return ""


def fetch_job_links(max_pages=3):
    """
    Collect individual Fuzu vacancy URLs from
    multiple pages of the general and basic-level
    IT job listings.
    """
    links = set()

    for base_url in FUZU_BASE_URLS:
        for page in range(
            1,
            max_pages + 1,
        ):
            if page == 1:
                page_url = base_url
            else:
                page_url = (
                    f"{base_url}?page={page}"
                )

            print(
                f"  Scanning Fuzu page "
                f"{page}: {page_url}"
            )

            html = fetch_page(
                page_url
            )

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

                if not href.startswith(
                    "/kenya/jobs/"
                ):
                    continue

                page_links.add(
                    urljoin(
                        BASE_URL,
                        href,
                    )
                )

            print(
                f"    Found "
                f"{len(page_links)} "
                f"job links."
            )

            links.update(
                page_links
            )

    return links


def extract_job_posting(html):
    """
    Extract Fuzu's structured JobPosting
    JSON-LD data.
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
            data = json.loads(
                script.string
            )
        except json.JSONDecodeError:
            continue

        if (
            isinstance(data, dict)
            and data.get("@type")
            == "JobPosting"
        ):
            return data

    return None


def clean_description(description):
    """
    Convert an HTML job description
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
    """
    Extract location from JSON-LD
    JobPosting data.
    """
    location = data.get(
        "jobLocation"
    )

    if not location:
        return "Kenya"

    if isinstance(
        location,
        list,
    ):
        location = location[0]

    if not isinstance(
        location,
        dict,
    ):
        return "Kenya"

    address = location.get(
        "address",
        {},
    )

    if not isinstance(
        address,
        dict,
    ):
        return "Kenya"

    city = address.get(
        "addressLocality"
    )

    country = address.get(
        "addressCountry"
    )

    parts = [
        part
        for part in [
            city,
            country,
        ]
        if part
    ]

    return (
        ", ".join(parts)
        or "Kenya"
    )


def extract_fallback_job(
    html,
    url,
):
    """
    Extract job information from visible
    Fuzu HTML when JobPosting JSON-LD
    is unavailable.
    """
    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    # -------------------------
    # Title
    # -------------------------
    heading = soup.find("h1")

    if not heading:
        return None

    title = heading.get_text(
        " ",
        strip=True,
    )

    # -------------------------
    # Company
    # -------------------------
    company = ""

    if soup.title:
        page_title = (
            soup.title.get_text(
                " ",
                strip=True,
            )
        )

        match = re.match(
            (
                r"^.+?\s+at\s+"
                r"(.+?)\s+\|\s+Fuzu$"
            ),
            page_title,
        )

        if match:
            company = (
                match.group(1)
                .strip()
            )

    # -------------------------
    # Visible paragraph text
    # -------------------------
    paragraphs = [
        paragraph.get_text(
            " ",
            strip=True,
        )
        for paragraph
        in soup.find_all("p")
        if paragraph.get_text(
            " ",
            strip=True,
        )
    ]

    # -------------------------
    # Posted date
    # -------------------------
    posted_at = None

    for text in paragraphs:
        if text.startswith(
            "Posted:"
        ):
            date_text = (
                text.replace(
                    "Posted:",
                    "",
                    1,
                )
                .strip()
            )

            try:
                posted_at = (
                    datetime.strptime(
                        date_text,
                        "%d %b %Y",
                    )
                    .replace(
                        tzinfo=timezone.utc
                    )
                )
            except ValueError:
                pass

            break

    # -------------------------
    # Location
    # -------------------------
    location = "Kenya"

    for index, text in enumerate(
        paragraphs
    ):
        if (
            text == "Location"
            and index + 1
            < len(paragraphs)
        ):
            location = (
                paragraphs[
                    index + 1
                ]
                .replace(
                    "•",
                    ",",
                )
            )

            location = re.sub(
                r"\s*,\s*",
                ", ",
                location,
            )

            break

    # -------------------------
    # Description
    # -------------------------
    description = ""

    skip_prefixes = (
        "More than ",
        "Posted:",
        "Apply by:",
        "Recruit better ",
        "Selected articles ",
        "Don’t miss your chance",
        "Fuzu helps you ",
        "© ",
    )

    skip_exact = {
        "Expired",
        "Location",
        "Contract Type",
        "Home",
        "Jobs",
        "Articles",
        "Learn",
    }

    for text in paragraphs:
        if text in skip_exact:
            continue

        if text.startswith(
            skip_prefixes
        ):
            continue

        if len(text) >= 100:
            description = text
            break

    return {
        "title": title,
        "company": company,
        "location": location,
        "description": description,
        "posted_at": posted_at,
        "url": url,
    }


def fetch_fuzu_jobs():
    """
    Fetch Fuzu jobs using JSON-LD when
    available and visible HTML as a fallback.
    """
    print(
        "  Finding Fuzu jobs..."
    )

    links = fetch_job_links()

    print(
        f"  Found {len(links)} "
        f"unique Fuzu job links."
    )

    jobs = []

    for url in links:
        html = fetch_page(
            url
        )

        if not html:
            continue

        data = extract_job_posting(
            html
        )

        # =========================
        # JSON-LD extraction
        # =========================
        if data:
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
                company = (
                    organization.get(
                        "name",
                        "",
                    )
                    .strip()
                )
            else:
                company = ""

            description = (
                clean_description(
                    data.get(
                        "description",
                        "",
                    )
                )
            )

            location = (
                extract_location(
                    data
                )
            )

            date_posted = data.get(
                "datePosted"
            )

            try:
                posted_at = (
                    datetime.fromisoformat(
                        date_posted
                    )
                    .replace(
                        tzinfo=timezone.utc
                    )
                )
            except (
                TypeError,
                ValueError,
            ):
                posted_at = None

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

            extraction_method = (
                "JSON-LD"
            )

        # =========================
        # HTML fallback
        # =========================
        else:
            fallback = (
                extract_fallback_job(
                    html,
                    url,
                )
            )

            if not fallback:
                print(
                    f"    Could not "
                    f"parse: {url}"
                )
                continue

            title = fallback[
                "title"
            ]

            company = fallback[
                "company"
            ]

            location = fallback[
                "location"
            ]

            description = fallback[
                "description"
            ]

            posted_at = fallback[
                "posted_at"
            ]

            source_id = url

            extraction_method = (
                "HTML fallback"
            )

        # =========================
        # Validation
        # =========================
        if not title:
            print(
                f"    Missing title: "
                f"{url}"
            )
            continue

        if not posted_at:
            print(
                f"    Missing posted "
                f"date: {title}"
            )

            # Temporary fallback because
            # Job currently requires a
            # datetime value.
            posted_at = datetime.now(
                timezone.utc
            )

        print(
            f"    Reading: "
            f"{title} at "
            f"{company} "
            f"[{extraction_method}]"
        )

        job = Job(
            source_id=source_id,
            source="Fuzu Kenya",
            title=title,
            company=company,
            location=location,
            description=description,
            tags=[],
            url=url,
            posted_at=posted_at,
        )

        jobs.append(
            job
        )

    print(
        f"  Collected "
        f"{len(jobs)} "
        f"Fuzu jobs."
    )

    return jobs


if __name__ == "__main__":
    jobs = fetch_fuzu_jobs()

    print()

    for job in jobs:
        print(
            "=" * 60
        )

        print(
            f"Title:    "
            f"{job.title}"
        )

        print(
            f"Company:  "
            f"{job.company}"
        )

        print(
            f"Location: "
            f"{job.location}"
        )

        print(
            f"Posted:   "
            f"{job.posted_at.date()}"
        )

        print(
            f"URL:      "
            f"{job.url}"
        )