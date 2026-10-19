import re

from app.utils.text import clean_text


ENTRY_LEVEL_TERMS = [
    "entry-level",
    "entry level",
    "graduate role",
    "graduate position",
    "fresh graduate",
]


def extract_experience(job):
    """
    Extract the minimum and maximum years of experience
    mentioned in a job description.

    Returns:
        (min_years, max_years, evidence)
    """
    text = clean_text(
        job.description
    ).lower()

    # Example:
    # "3-5 years"
    # "3 - 5 years"
    # "3 to 5 years"
    range_pattern = re.compile(
        r"\b(\d{1,2})\s*"
        r"(?:-|–|—|to)\s*"
        r"(\d{1,2})\s+"
        r"years?\b"
    )

    match = range_pattern.search(text)

    if match:
        minimum = int(
            match.group(1)
        )

        maximum = int(
            match.group(2)
        )

        return (
            minimum,
            maximum,
            match.group(0),
        )

    # Example:
    # "minimum 5 years"
    # "at least 3 years"
    minimum_pattern = re.compile(
        r"\b(?:minimum(?: of)?|at least)"
        r"\s+(\d{1,2})\s+years?\b"
    )

    match = minimum_pattern.search(text)

    if match:
        years = int(
            match.group(1)
        )

        return (
            years,
            None,
            match.group(0),
        )

    # Example:
    # "5 years of experience"
    # "5 years experience"
    years_pattern = re.compile(
        r"\b(\d{1,2})\+?\s+years?"
        r"(?:\s+of)?\s+experience\b"
    )

    match = years_pattern.search(text)

    if match:
        years = int(
            match.group(1)
        )

        return (
            years,
            None,
            match.group(0),
        )

    # Some jobs do not state a number but explicitly
    # identify themselves as entry-level.
    for term in ENTRY_LEVEL_TERMS:
        if term in text:
            return (
                0,
                2,
                term,
            )

    return (
        None,
        None,
        None,
    )


def classify_experience(job):
    minimum, maximum, evidence = (
        extract_experience(job)
    )

    if minimum is None:
        return (
            "UNKNOWN",
            evidence,
        )

    if maximum is not None:
     if maximum <= 2:
        return (
            "GOOD_FIT",
            evidence,
        )

    if minimum <= 2 and maximum <= 3:
        return (
            "STRETCH",
            evidence,
        )

    if minimum <= 2:
     return (
        "GOOD_FIT",
        evidence,
    )

    if minimum == 3:
     return (
        "STRETCH",
        evidence,
    )

    if minimum <= 5:
        return (
            "UNLIKELY",
            evidence,
        )

    return (
        "TOO_SENIOR",
        evidence,
    )