import requests

from datetime import datetime, timezone

from app.models.job import Job

from app.profile import HIMALAYAS_SEARCH_QUERIES

HIMALAYAS_URL = "https://himalayas.app/jobs/api/search"


def fetch_himalayas_jobs(max_pages=2):
    jobs = []
    seen_ids = set()

    for query in HIMALAYAS_SEARCH_QUERIES:
        print(f"  Searching: {query}")

        for page in range(1, max_pages + 1):
            params = {
                "q": query,
                "worldwide": "true",
                "sort": "relevant",
                "page": page,
            }

            response = requests.get(
                HIMALAYAS_URL,
                params=params,
                headers={"User-Agent": "AI Job Finder"},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            page_jobs = data["jobs"]

            if not page_jobs:
                break

            for item in page_jobs:
                source_id = item["guid"]

                if source_id in seen_ids:
                    continue

                seen_ids.add(source_id)

                job = Job(
                    source_id=source_id,
                    source="Himalayas",
                    title=item["title"].strip(),
                    company=item["companyName"].strip(),
                    location="Worldwide Remote",
                    description=item.get("description", ""),
                    tags=item.get("categories", []),
                    url=item["applicationLink"],
                    posted_at=datetime.fromtimestamp(
                        item["pubDate"],
                        tz=timezone.utc,
                    ),
                    salary_min=item.get("minSalary"),
                    salary_max=item.get("maxSalary"),
                    employment_type=item.get("employmentType"),
                    seniority=item.get("seniority", []),
                    location_restrictions=item.get(
                        "locationRestrictions", []
                    ),
                    timezone_restrictions=item.get(
                        "timezoneRestrictions", []
                    ),
                )

                jobs.append(job)

    return jobs
