# from app.sources.remote_ok import fetch_jobs
# from app.sources.himalayas import fetch_himalayas_jobs

from app.matching.filter import calculate_relevance
from app.eligibility.checker import check_eligibility
from app.sources.myjobmag import fetch_myjobmag_jobs
from app.matching.experience import classify_experience
from app.sources.fuzu import fetch_fuzu_jobs


def main():
    print("AI Job Finder\n")

    print("Fetching MyJobMag Kenya...")
    myjobmag_jobs = fetch_myjobmag_jobs()

    print("\nFetching Fuzu Kenya...")
    fuzu_jobs = fetch_fuzu_jobs()

    jobs = myjobmag_jobs + fuzu_jobs

    print(f"\nTotal collected: {len(jobs)} jobs.\n")

    ranked_jobs = []

    for job in jobs:
        score, reasons, track = calculate_relevance(job)

        if score >= 5:
            ranked_jobs.append(
                (job, score, reasons, track)
            )

    ranked_jobs.sort(
        key=lambda item: item[1],
        reverse=True,
    )

    print(
        f"Found {len(ranked_jobs)} "
        f"potentially relevant jobs.\n"
    )

    for job, score, reasons, track in ranked_jobs:
        eligibility, eligibility_reasons = (
            check_eligibility(job)
        )

        experience_fit, experience_evidence = (
            classify_experience(job)
        )

        print("=" * 60)
        print(f"Score:       {score}")
        print(f"Title:       {job.title}")
        print(f"Company:     {job.company}")
        print(f"Source:      {job.source}")
        print(f"Track:       {track}")
        print(f"Location:    {job.location}")
        print(f"Eligibility: {eligibility}")
        print(f"Experience:  {experience_fit}")

        if experience_evidence:
            print(
                f"Requirement: "
                f"{experience_evidence}"
            )

        print(f"Posted:      {job.posted_at.date()}")

        if reasons:
            print("Why:")

            for reason in reasons:
                print(f"  - {reason}")

        print("Eligibility reason:")

        for reason in eligibility_reasons:
            print(f"  - {reason}")

        print(f"URL:         {job.url}")
        print()


if __name__ == "__main__":
    main()