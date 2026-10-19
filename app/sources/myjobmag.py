import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from urllib.parse import urljoin

from app.models.job import Job


BASE_URL = "https://www.myjobmag.co.ke"

MYJOBMAG_URL = (
    "https://www.myjobmag.co.ke/jobs-by-field/information-technology"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Safari/537.36"
    )
}


def fetch_job_details(url):
    """
    Fetch the actual job description from an individual
    MyJobMag job page.
    """
    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=30,
        )

        response.raise_for_status()

    except requests.RequestException as error:
        print(f"    Could not fetch details: {error}")
        return ""

    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    job_description = soup.select_one(
        "li.job-description"
    )

    if not job_description:
        print("    Could not find job description.")
        return ""

    # Remove Method of Application and anything after it
    # from the description container.
    method_heading = job_description.find(
        "h2",
        string=lambda text: (
            text
            and "Method of Application" in text
        ),
    )

    if method_heading:
        for element in list(
            method_heading.find_all_next()
        ):
            if (
                element is job_description
                or job_description not in element.parents
            ):
                break

            element.decompose()

        method_heading.decompose()

    description = job_description.get_text(
        " ",
        strip=True,
    )

    return description


def fetch_myjobmag_jobs():
    """
    Fetch ICT jobs from the MyJobMag Kenya ICT category
    and enrich each result using its individual job page.
    """
    try:
        response = requests.get(
            MYJOBMAG_URL,
            headers=HEADERS,
            timeout=30,
        )

        response.raise_for_status()

    except requests.RequestException as error:
        print(f"  MyJobMag unavailable: {error}")
        return []

    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    jobs = []
    seen_urls = set()

    job_cards = soup.select(
        "li.job-list-li"
    )

    for card in job_cards:
        job_info = card.select_one(
            "li.job-info"
        )

        if not job_info:
            continue

        title_link = job_info.select_one(
            'a[href^="/job/"]'
        )

        if not title_link:
            continue

        href = title_link.get(
            "href",
            "",
        )

        full_title = title_link.get_text(
            " ",
            strip=True,
        )

        if not href or not full_title:
            continue

        url = urljoin(
            BASE_URL,
            href,
        )

        if url in seen_urls:
            continue

        seen_urls.add(url)

        if " at " in full_title:
            job_title, company = full_title.rsplit(
                " at ",
                1,
            )
        else:
            job_title = full_title
            company = ""

        print(
            f"    Reading: "
            f"{job_title.strip()} "
            f"at {company.strip()}"
        )

        description = fetch_job_details(
            url
        )

        job = Job(
            source_id=href,
            source="MyJobMag Kenya",
            title=job_title.strip(),
            company=company.strip(),
            location="Kenya",
            description=description,
            tags=[],
            url=url,

            # Temporary until we parse MyJobMag's
            # actual posting date.
            posted_at=datetime.now(
                timezone.utc
            ),
        )

        jobs.append(job)

    print(
        f"  Found {len(jobs)} Kenya ICT jobs."
    )

    return jobs