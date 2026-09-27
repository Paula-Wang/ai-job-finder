CAREER_TRACKS = {
    "systems": [
        "systems administrator",
        "system administrator",
        "sysadmin",
        "microsoft 365",
        "m365",
        "cloud support",
        "technical support",
        "it support",
        "it administrator",
    ],

    "software": [
        "software engineer",
        "software developer",
        "backend developer",
        "java developer",
        "spring boot",
        "flutter developer",
        "junior developer",
        "graduate developer",
    ],

    "cybersecurity": [
        "cybersecurity",
        "security analyst",
        "soc analyst",
        "security engineer",
        "information security",
        "iam analyst",
        "identity access management",
    ],

    "iot_embedded": [
        "iot",
        "internet of things",
        "embedded systems",
        "embedded engineer",
        "embedded software",
    ],
}


SEARCH_TERMS = [
    term
    for terms in CAREER_TRACKS.values()
    for term in terms
]