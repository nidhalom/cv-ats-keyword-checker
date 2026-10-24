"""Compare a CV with a job description: matched and missing skills and keywords, and a score.

Scoring: every skill from the job description counts 2 points, every generic keyword counts 1 point.
Score = 100 * (points found in the CV) / (total points). Skills get more weight because a recruiter's
keyword filter is usually built from the named technologies first.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

from .skills import find_skills
from .text import content_terms, term_frequencies

SKILL_WEIGHT = 2
TERM_WEIGHT = 1
MIN_BIGRAM_COUNT = 2


@dataclass
class Report:
    skills_required: list[str] = field(default_factory=list)
    skills_matched: list[str] = field(default_factory=list)
    skills_missing: list[str] = field(default_factory=list)
    terms_required: list[str] = field(default_factory=list)
    terms_matched: list[str] = field(default_factory=list)
    terms_missing: list[str] = field(default_factory=list)
    score: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)


def top_job_terms(job_text: str, limit: int) -> list[str]:
    """Most frequent generic keywords in the job text. Bigrams need at least two occurrences."""
    counts = term_frequencies(job_text)
    eligible = [
        (term, count)
        for term, count in counts.items()
        if " " not in term or count >= MIN_BIGRAM_COUNT
    ]
    # Higher count first, then longer phrases, then alphabetical for a stable order.
    eligible.sort(key=lambda item: (-item[1], -item[0].count(" "), item[0]))
    return [term for term, _ in eligible[:limit]]


def analyze(cv_text: str, job_text: str, top_terms: int = 15) -> Report:
    skills_required = sorted(find_skills(job_text))
    skills_in_cv = find_skills(cv_text)

    terms_required = top_job_terms(job_text, top_terms)
    terms_in_cv = content_terms(cv_text)

    # A skill that is also a generic term (for example "docker") should count once, as a skill.
    skill_words = {word for skill in skills_required for word in skill.lower().split()}
    terms_required = [t for t in terms_required if t not in skill_words]

    skills_matched = [s for s in skills_required if s in skills_in_cv]
    terms_matched = [t for t in terms_required if t in terms_in_cv]

    total = SKILL_WEIGHT * len(skills_required) + TERM_WEIGHT * len(terms_required)
    found = SKILL_WEIGHT * len(skills_matched) + TERM_WEIGHT * len(terms_matched)
    score = round(100 * found / total, 1) if total else 0.0

    return Report(
        skills_required=skills_required,
        skills_matched=skills_matched,
        skills_missing=[s for s in skills_required if s not in skills_in_cv],
        terms_required=terms_required,
        terms_matched=terms_matched,
        terms_missing=[t for t in terms_required if t not in terms_in_cv],
        score=score,
    )
