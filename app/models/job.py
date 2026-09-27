from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Job:
    source_id: str
    source: str
    title: str
    company: str
    location: str
    description: str
    tags: list[str]
    url: str
    posted_at: datetime

    salary_min: int | None = None
    salary_max: int | None = None

    employment_type: str | None = None
    seniority: list[str] = field(default_factory=list)
    location_restrictions: list[str] = field(default_factory=list)
    timezone_restrictions: list[float] = field(default_factory=list)