from difflib import SequenceMatcher

from app.profile import CAREER_TRACKS


SENIORITY_PENALTIES = {
    "senior": -10,
    "staff": -12,
    "principal": -15,
    "manager": -10,
    "director": -15,
    "vp": -20,
    "vice president": -20,
    "head of": -15,
}


EARLY_CAREER_BONUSES = {
    "junior": 8,
    "graduate": 10,
    "entry level": 10,
    "entry-level": 10,
    "associate": 4,
}


CAREER_STAGE_PENALTIES = {
    "intern": -15,
    "internship": -15,
    "attachment": -20,
    "industrial attachment": -20,
    "student": -20,
}


def fuzzy_title_match(
    term,
    title,
    threshold=0.88,
):
    """
    Check whether a career term approximately matches
    part of a job title.

    Intended to catch small spelling differences such as:
    'IT Support Specialist'
    'IT Suport Specialist'
    """
    term_words = term.lower().split()
    title_words = title.lower().split()

    if len(term_words) > len(title_words):
        return False

    window_size = len(term_words)

    for index in range(
        len(title_words) - window_size + 1
    ):
        candidate = " ".join(
            title_words[
                index:index + window_size
            ]
        )

        similarity = SequenceMatcher(
            None,
            term.lower(),
            candidate,
        ).ratio()

        if similarity >= threshold:
            return True

    return False


def calculate_relevance(job):
    title = job.title.lower()
    description = job.description.lower()

    tags = [
        tag.lower()
        for tag in job.tags
    ]

    track_scores = {}

    for track, terms in CAREER_TRACKS.items():
        score = 0
        matched_terms = []

        exact_title_matches = []
        fuzzy_title_matches = []
        description_matches = []

        for term in terms:
            term = term.lower()

            if term in title:
                exact_title_matches.append(
                    term
                )

            elif fuzzy_title_match(
                term,
                title,
            ):
                fuzzy_title_matches.append(
                    term
                )

            if term in tags:
                score += 3

            if term in description:
                description_matches.append(
                    term
                )

        # Prefer one exact title match.
        # If there is no exact match, allow one
        # fuzzy title match instead.
        if exact_title_matches:
            best_exact = max(
                exact_title_matches,
                key=len,
            )

            score += 10

            matched_terms.append(
                best_exact
            )

        elif fuzzy_title_matches:
            best_fuzzy = max(
                fuzzy_title_matches,
                key=len,
            )

            score += 8

            matched_terms.append(
                f"{best_fuzzy} (fuzzy)"
            )

        # Description matches provide supporting
        # evidence but should not dominate scoring.
        if description_matches:
            score += min(
                len(description_matches),
                2,
            )

        # A track only qualifies if the job title
        # matched exactly or fuzzily.
        if matched_terms:
            track_scores[track] = {
                "score": score,
                "matched_terms": matched_terms,
            }

    if not track_scores:
        return 0, [], None

    best_track = max(
        track_scores,
        key=lambda track: (
            track_scores[track]["score"]
        ),
    )

    score = track_scores[
        best_track
    ]["score"]

    reasons = [
        f"Career track: {best_track}"
    ]

    for term in track_scores[
        best_track
    ]["matched_terms"]:
        reasons.append(
            f"Matched '{term}'"
        )

    seniority = [
        level.lower()
        for level in job.seniority
    ]

    # Penalize jobs that are clearly senior.
    for word, penalty in (
        SENIORITY_PENALTIES.items()
    ):
        if (
            word in title
            or any(
                word in level
                for level in seniority
            )
        ):
            score += penalty

            reasons.append(
                f"Seniority penalty: '{word}'"
            )

    # Give a bonus to suitable early-career
    # titles such as Junior or Graduate.
    for word, bonus in (
        EARLY_CAREER_BONUSES.items()
    ):
        if word in title:
            score += bonus

            reasons.append(
                f"Early-career bonus: '{word}'"
            )

    # Penalize internships and similar roles
    # because we are looking for a next career
    # move rather than restarting at internship.
    for word, penalty in (
        CAREER_STAGE_PENALTIES.items()
    ):
        if word in title:
            score += penalty

            reasons.append(
                f"Career-stage penalty: '{word}'"
            )

    return (
        max(score, 0),
        reasons,
        best_track,
    )