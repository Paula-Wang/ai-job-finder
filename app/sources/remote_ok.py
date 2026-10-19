import requests

from datetime import datetime

from app.models.job import Job


REMOTE_OK_URL = "https://remoteok.com/api"


def fetch_jobs():
    try:
        response = requests.get(
            REMOTE_OK_URL,
            headers={"User-Agent": "AI Job Finder"},
            timeout=30,
        )
        response.raise_for_status()

    except requests.RequestException as error:
        print(f"  Remote OK unavailable: {error}")
        return []

    data = response.json()

    jobs = []

    for item in data[1:]:
        job = Job(
            source_id=item["id"],
            source="Remote OK",
            title=item["position"].strip(),
            company=item["company"].strip(),
            location=item.get("location", "").strip(),
            description=item.get("description", ""),
            tags=item.get("tags", []),
            url=item["apply_url"],
            posted_at=datetime.fromisoformat(item["date"]),
            salary_min=item.get("salary_min"),
            salary_max=item.get("salary_max"),
        )

        jobs.append(job)

    return jobs
    response = requests.get(
        REMOTE_OK_URL,
        headers={
            "User-Agent": "AI Job Finder"
        },
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    jobs = []

    # The first record contains Remote OK API metadata,
    # so actual job records begin at index 1.
    for item in data[1:]:
        job = Job(
            source_id=item["id"],
            source="Remote OK",
            title=item["position"].strip(),
            company=item["company"].strip(),
            location=item.get("location", "").strip(),
            description=item.get("description", ""),
            tags=item.get("tags", []),
            url=item["apply_url"],
            posted_at=datetime.fromisoformat(item["date"]),
            salary_min=item.get("salary_min"),
            salary_max=item.get("salary_max"),
        )

        jobs.append(job)

    return jobs