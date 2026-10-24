"""A small dictionary of technical skills with synonyms, and a matcher that finds them in text.

Aliases are matched on normalised text (lowercase, no accents). Entries in ``strict`` are matched
case-sensitively on the raw text, for words that are also common English (for example "Go").
When two matches overlap, the longer one wins, so "docker compose" is not also reported as "Docker".
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .text import normalize


@dataclass(frozen=True)
class Skill:
    name: str
    aliases: tuple[str, ...] = ()
    strict: tuple[str, ...] = field(default=())
    # Skills that are implied when this one is found, e.g. "Docker Compose" implies "Docker".
    implies: tuple[str, ...] = field(default=())


SKILLS: tuple[Skill, ...] = (
    # Languages
    Skill("Python", ("python", "python3")),
    Skill("Go", ("golang", "go lang"), strict=("Go",)),
    Skill("Java", ("java",)),
    Skill("JavaScript", ("javascript", "ecmascript")),
    Skill("TypeScript", ("typescript",)),
    Skill("C++", ("c++",)),
    Skill("C#", ("c#", "csharp")),
    Skill("Rust", ("rust",)),
    Skill("SQL", ("sql", "pl/sql")),
    Skill("Bash", ("bash", "shell scripting")),
    # Databases
    Skill("PostgreSQL", ("postgresql", "postgres")),
    Skill("Oracle Database", ("oracle database", "oracle db", "oracle")),
    Skill("MySQL", ("mysql", "mariadb")),
    Skill("MongoDB", ("mongodb", "mongo db")),
    Skill("Redis", ("redis",)),
    Skill("SQLite", ("sqlite",)),
    # Frameworks and libraries
    Skill("Next.js", ("next.js", "nextjs")),
    Skill("React", ("react", "reactjs", "react.js")),
    Skill("Node.js", ("node.js", "nodejs")),
    Skill("FastAPI", ("fastapi",)),
    Skill("Django", ("django",)),
    Skill("Flask", ("flask",)),
    Skill("Spring", ("spring boot", "spring framework")),
    Skill("Liferay", ("liferay",)),
    Skill("pandas", ("pandas",)),
    Skill("NumPy", ("numpy",)),
    Skill("scikit-learn", ("scikit-learn", "sklearn")),
    Skill("PyTorch", ("pytorch",)),
    # Delivery and infrastructure
    Skill("Docker", ("docker",)),
    Skill("Docker Compose", ("docker compose", "docker-compose"), implies=("Docker",)),
    Skill("Kubernetes", ("kubernetes", "k8s")),
    Skill("Git", ("git",)),
    Skill("GitHub Actions", ("github actions",)),
    Skill("CI/CD", ("ci/cd", "cicd", "continuous integration", "continuous delivery")),
    Skill("Linux", ("linux", "ubuntu", "debian")),
    Skill("Proxmox", ("proxmox ve", "proxmox")),
    Skill("Nginx", ("nginx",)),
    Skill("Terraform", ("terraform",)),
    Skill("Ansible", ("ansible",)),
    # Architecture and practice
    Skill("REST API", ("rest api", "restful", "rest")),
    Skill("Microservices", ("microservices", "microservice")),
    Skill("Machine Learning", ("machine learning", "ml")),
    Skill("Deep Learning", ("deep learning",)),
    Skill("Unit Testing", ("unit testing", "unit tests", "pytest", "jest")),
    Skill("Agile", ("agile", "scrum")),
    # Marketing and analytics (for the media-buying background)
    Skill("Google Analytics", ("google analytics", "ga4")),
    Skill("Meta Ads", ("meta ads", "facebook ads")),
    Skill("Google Ads", ("google ads",)),
    Skill("Performance Marketing", ("performance marketing", "media buying")),
)


@dataclass(frozen=True)
class _Pattern:
    regex: re.Pattern[str]
    canonical: str
    length: int


def _compile_patterns(skills: tuple[Skill, ...]) -> tuple[list[_Pattern], list[_Pattern]]:
    loose: list[_Pattern] = []
    strict: list[_Pattern] = []
    for skill in skills:
        for alias in skill.aliases:
            # Lookarounds stop "go" matching inside "algorithm" or "c++" matching "c++11".
            pattern = re.compile(rf"(?<![a-z0-9+#.]){re.escape(normalize(alias))}(?![a-z0-9+#])")
            loose.append(_Pattern(pattern, skill.name, len(alias)))
        for alias in skill.strict:
            pattern = re.compile(rf"(?<![A-Za-z0-9+#.]){re.escape(alias)}(?![A-Za-z0-9+#\-])")
            strict.append(_Pattern(pattern, skill.name, len(alias)))
    return loose, strict


_LOOSE, _STRICT = _compile_patterns(SKILLS)
_IMPLIES = {skill.name: skill.implies for skill in SKILLS if skill.implies}


def find_skills(text: str) -> set[str]:
    """Return the canonical names of every skill mentioned in ``text``."""
    found: set[str] = set()
    normalised = normalize(text)

    # Longest alias first, so the most specific phrase claims its characters.
    candidates = []
    for pattern in _LOOSE:
        for match in pattern.regex.finditer(normalised):
            candidates.append((-(match.end() - match.start()), match.start(), match.end(), pattern.canonical))
    candidates.sort()

    taken: list[tuple[int, int]] = []
    for _, start, end, canonical in candidates:
        if any(start < t_end and end > t_start for t_start, t_end in taken):
            continue
        taken.append((start, end))
        found.add(canonical)

    for pattern in _STRICT:
        if pattern.regex.search(text):
            found.add(pattern.canonical)

    for name in list(found):
        found.update(_IMPLIES.get(name, ()))
    return found
