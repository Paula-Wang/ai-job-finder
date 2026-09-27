import requests

from datetime import datetime, timezone

from app.models.job import Job


HIMALAYAS_URL = "https://himalayas.app/jobs/api/search"


def fetch_himalayas_jobs(max_pages=5):
    jobs = []
    cursor = None

    for page in range(max_pages):
        params = {
            "worldwide": "true",
            "sort": "recent",
        }

        if cursor:
            params["cursor"] = cursor

        response = requests.get(
            HIMALAYAS_URL,
            params=params,
            headers={
                "User-Agent": "AI Job Finder"
            },
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        for item in data["jobs"]:
            job = Job(
                source_id=item["guid"],
                source="Himalayas",
                title=item["title"].strip(),
                company=item["companyName"].strip(),
                location="Worldwide Remote",
                description=item.get("description", ""),
                tags=item.get("categories", []),
                url=item["applicationLink"],
                posted_at=datetime.fromtimestamp(
                    item["pubDate"],
                    tz=timezone.utc
                ),
                salary_min=item.get("minSalary"),
                salary_max=item.get("maxSalary"),
                employment_type=item.get(
                    "employmentType"
                ),
                seniority=item.get(
                    "seniority", []
                ),
                location_restrictions=item.get(
                    "locationRestrictions", []
                ),
                timezone_restrictions=item.get(
                    "timezoneRestrictions", []
                ),
            )

            jobs.append(job)

        cursor = data.get("nextCursor")

        if not cursor:
            break

    return jobs