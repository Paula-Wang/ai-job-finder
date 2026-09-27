from app.sources.remote_ok import fetch_jobs
from app.sources.himalayas import fetch_himalayas_jobs
from app.matching.filter import calculate_relevance


def main():
    print("AI Job Finder\n")

    print("Fetching Remote OK...")
    remote_ok_jobs = fetch_jobs()

    print(f"  Found {len(remote_ok_jobs)} jobs.")

    print("Fetching Himalayas...")
    himalayas_jobs = fetch_himalayas_jobs()

    print(f"  Found {len(himalayas_jobs)} worldwide jobs.")

    jobs = remote_ok_jobs + himalayas_jobs

    print(f"\nTotal collected: {len(jobs)} jobs.\n")

    ranked_jobs = []

    for job in jobs:
        score, reasons, track = calculate_relevance(job)

        if score > 0:
            ranked_jobs.append(
    (job, score, reasons, track)
)

    ranked_jobs.sort(
        key=lambda item: item[1],
        reverse=True
    )

    print(
        f"Found {len(ranked_jobs)} "
        f"potentially relevant jobs.\n"
    )

    for job, score, reasons, track in ranked_jobs[:20]:
        print("=" * 60)
        print(f"Score:     {score}")
        print(f"Title:     {job.title}")
        print(f"Company:   {job.company}")
        print(f"Source:    {job.source}")
        print(f"Track:     {track}")
        print(f"Location:  {job.location}")

        if job.seniority:
            print(
                f"Seniority: {', '.join(job.seniority)}"
            )

        print(f"Posted:    {job.posted_at.date()}")

        if reasons:
            print("Why:")

            for reason in reasons:
                print(f"  - {reason}")

        print(f"URL:       {job.url}")
        print()


if __name__ == "__main__":
    main()