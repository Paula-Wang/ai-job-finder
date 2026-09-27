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


def calculate_relevance(job):
    title = job.title.lower()
    description = job.description.lower()
    tags = [tag.lower() for tag in job.tags]

    track_scores = {}

    for track, terms in CAREER_TRACKS.items():
        score = 0
        matched_terms = []

        for term in terms:
            term = term.lower()

            if term in title:
                score += 10
                matched_terms.append(term)

            if term in tags:
                score += 3
                matched_terms.append(term)

            if term in description:
                score += 1

        if score > 0:
            track_scores[track] = {
                "score": score,
                "matched_terms": list(set(matched_terms)),
            }

    if not track_scores:
        return 0, [], None

    # Pick whichever career track matched best
    best_track = max(
        track_scores,
        key=lambda track: track_scores[track]["score"]
    )

    score = track_scores[best_track]["score"]
    reasons = [
        f"Career track: {best_track}"
    ]

    for term in track_scores[best_track]["matched_terms"]:
        reasons.append(f"Matched '{term}'")

    # Only apply seniority after establishing career relevance
    for word, penalty in SENIORITY_PENALTIES.items():
        if word in title:
            score += penalty
            reasons.append(
                f"Seniority penalty: '{word}'"
            )

    for word, bonus in EARLY_CAREER_BONUSES.items():
        if word in title:
            score += bonus
            reasons.append(
                f"Early-career bonus: '{word}'"
            )

    return max(score, 0), reasons, best_track