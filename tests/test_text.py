from cv_ats.text import content_phrases, content_terms, normalize, term_frequencies, tokenize


def test_normalize_strips_accents_and_casefolds():
    assert normalize("Développeur Équipe") == "developpeur equipe"


def test_normalize_unifies_curly_apostrophes():
    assert normalize("l’équipe") == "l'equipe"


def test_tokenize_keeps_hyphenated_and_apostrophe_words():
    assert tokenize("Full-stack, l'API REST") == ["full-stack", "l'api", "rest"]


def test_content_phrases_break_on_stopwords_and_short_tokens():
    # "build" is a filler word and "go" is shorter than min_len=3, so both end runs.
    phrases = list(content_phrases("Build a REST API with Go and PostgreSQL"))
    assert phrases == [["rest", "api"], ["postgresql"]]


def test_french_stopwords_are_removed():
    phrases = list(content_phrases("Nous recherchons un développeur backend pour notre équipe"))
    flat = [word for run in phrases for word in run]
    assert "nous" not in flat
    assert "un" not in flat
    assert "backend" in flat
    assert "developpeur" in flat


def test_content_terms_contains_unigrams_and_bigrams():
    terms = content_terms("Senior python developer, python developer")
    assert {"senior", "python", "developer", "python developer"} <= terms


def test_term_frequencies_counts_bigrams_only_within_runs():
    counts = term_frequencies("docker kubernetes and docker kubernetes")
    assert counts["docker"] == 2
    assert counts["docker kubernetes"] == 2
    # "and" is a stopword, so no bigram crosses it
    assert "kubernetes docker" not in counts
