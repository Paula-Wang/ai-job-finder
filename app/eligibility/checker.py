from app.utils.text import clean_text

ELIGIBLE_TERMS = {
    "kenya",
    "africa",
    "worldwide",
    "anywhere in the world",
    "globally",
    "global remote",
}

RESTRICTED_PHRASES = {
    "within germany": "Role is restricted to Germany",
    "germany only": "Role is restricted to Germany",
    "us only": "Role is restricted to the US",
    "u.s. only": "Role is restricted to the US",
    "united states only": "Role is restricted to the US",
    "canada only": "Role is restricted to Canada",
    "uk only": "Role is restricted to the UK",
}


def check_eligibility(job):
    if job.source in {
        "MyJobMag Kenya",
        "Fuzu Kenya",
    }:
        return (
            "ELIGIBLE",
            [f"Listed on {job.source}"],
        )
    description = clean_text(job.description).lower()

    restrictions = [restriction.lower() for restriction in job.location_restrictions]

    # First use structured location data when available.
    if restrictions:
        for restriction in restrictions:
            if any(term in restriction for term in ELIGIBLE_TERMS):
                return "LIKELY_ELIGIBLE", [f"Location allows: {restriction}"]

        return "LIKELY_RESTRICTED", [
            "Structured location restrictions do not appear to include Kenya"
        ]

    # If structured data is unavailable, inspect explicit
    # restriction language in the job description.
    for phrase, reason in RESTRICTED_PHRASES.items():
        if phrase in description:
            return "LIKELY_RESTRICTED", [reason]

    for term in ELIGIBLE_TERMS:
        if term in description:
            return "LIKELY_ELIGIBLE", [f"Job description mentions: {term}"]

    return "CHECK_MANUALLY", ["No clear eligibility or location restriction found"]
