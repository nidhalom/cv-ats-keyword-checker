import pytest

from cv_ats.skills import find_skills


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Experience with Golang microservices", {"Go", "Microservices"}),
        ("We use Postgres and Redis", {"PostgreSQL", "Redis"}),
        ("Deploy on k8s with Docker", {"Kubernetes", "Docker"}),
        ("Node.js and nodejs services", {"Node.js"}),
        ("Comfortable with C++ and C# code", {"C++", "C#"}),
        ("CI/CD with GitHub Actions", {"CI/CD", "GitHub Actions"}),
    ],
)
def test_synonyms_resolve_to_canonical_names(text, expected):
    assert expected <= find_skills(text)


def test_longest_match_claims_the_span_once():
    # "docker compose" is matched as one phrase; the plain "docker" alias must not match inside it.
    skills = find_skills("docker compose up -d")
    assert skills == {"Docker Compose", "Docker"}  # Docker comes from the implies rule, not a second match


def test_docker_compose_implies_docker():
    assert "Docker" in find_skills("Packaged services with Docker Compose")


def test_strict_go_does_not_match_the_verb():
    assert "Go" not in find_skills("We go to market next quarter")
    assert "Go" not in find_skills("Our algorithm is fast")


def test_strict_go_matches_capitalised_language_name():
    assert "Go" in find_skills("Backend services written in Go.")


def test_word_boundaries_block_partial_matches():
    assert find_skills("Rustic furniture and javascripting") == set()


def test_french_text_is_matched_too():
    assert {"PostgreSQL", "Docker"} <= find_skills("Maîtrise de PostgreSQL et Docker")


def test_empty_text_has_no_skills():
    assert find_skills("") == set()
