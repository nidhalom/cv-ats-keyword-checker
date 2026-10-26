from cv_ats.analyze import analyze, top_job_terms

JOB = "Backend engineer. Build REST API services in Go. Own the PostgreSQL schema."
CV = "Backend developer. I wrote Golang services and a Postgres schema for a REST API."


def test_skills_are_matched_through_synonyms():
    report = analyze(CV, JOB)
    assert report.skills_required == ["Go", "PostgreSQL", "REST API"]
    assert report.skills_matched == ["Go", "PostgreSQL", "REST API"]
    assert report.skills_missing == []


def test_missing_skill_is_reported():
    report = analyze("Python developer with SQL", "We need Kubernetes and Python experience.")
    assert report.skills_missing == ["Kubernetes"]
    assert report.skills_matched == ["Python"]


def test_score_is_weighted_skills_over_terms():
    # Skills: Go, PostgreSQL (2 points each). Terms are the generic words left in the job text.
    report = analyze("Go and PostgreSQL", "Go and PostgreSQL")
    assert report.score == 100.0

    report = analyze("Go", "Go and PostgreSQL")
    # 2 points for Go out of (2 + 2) skill points, no generic terms left
    assert report.score == 50.0


def test_score_is_zero_when_job_has_no_keywords():
    report = analyze("Python developer", "The and of to a")
    assert report.score == 0.0
    assert report.skills_required == []
    assert report.terms_required == []


def test_score_stays_in_range():
    report = analyze("", JOB)
    assert 0.0 <= report.score <= 100.0
    assert report.score == 0.0


def test_top_job_terms_drops_single_bigram_occurrences():
    terms = top_job_terms("data pipeline data pipeline. stream processing once", limit=10)
    assert "data pipeline" in terms
    assert "stream processing" not in terms
    assert "stream" in terms


def test_top_job_terms_respects_limit():
    assert len(top_job_terms("alpha beta gamma delta epsilon", limit=3)) == 3


def test_report_to_dict_has_all_fields():
    data = analyze(CV, JOB).to_dict()
    assert set(data) == {
        "skills_required",
        "skills_matched",
        "skills_missing",
        "terms_required",
        "terms_matched",
        "terms_missing",
        "score",
    }
