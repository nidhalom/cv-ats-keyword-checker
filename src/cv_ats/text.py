"""Text normalisation, tokenisation and stopword filtering (English and French)."""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterator

# Stopwords are stored without accents because normalize() strips accents.
STOPWORDS_EN = frozenset(
    """
    a about above after again against all also am an and any are as at be because been
    before being below between both but by can could did do does doing down during each
    few for from further had has have having he her here hers herself him himself his how
    i if in into is it its itself just me more most my myself no nor not now of off on
    once only or other our ours out over own same she should so some such than that the
    their theirs them themselves then there these they this those through to too under
    until up us very was we were what when where which while who whom why will with would
    you your yours yourself
    """.split()
)

STOPWORDS_FR = frozenset(
    """
    le la les un une des du de d l au aux et ou ni mais donc or car que qui quoi dont ou
    est sont etre avoir ai as ont il elle ils elles on nous vous je tu se ce cet cette ces
    mon ma mes ton ta tes son sa ses notre nos votre vos leur leurs en dans par pour sur
    sans avec entre vers chez comme plus moins tres aussi tout tous toute toutes pas ne
    y fait faire sous selon lors afin etc ete ou
    """.split()
)

# Filler words that show up in almost every job ad. They carry no signal for matching.
FILLER_WORDS = frozenset(
    """
    able across work works working team teams role roles experience years year good strong
    using use used new etc join looking need needs must will ability including include
    plus within based help make way get take well also know knowledge skills skill
    another clear build engineer own maintain ship design
    travail expérience ans équipe poste profil missions entreprise candidat rejoindre
    """.split()
)

STOPWORDS = STOPWORDS_EN | STOPWORDS_FR | FILLER_WORDS

_TOKEN_RE = re.compile(r"[a-z][a-z0-9]*(?:['\-][a-z0-9]+)*")


def normalize(text: str) -> str:
    """Lowercase, strip accents and unify apostrophes so that CV and job text compare fairly."""
    decomposed = unicodedata.normalize("NFKD", text)
    without_marks = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return without_marks.casefold().replace("’", "'")


def tokenize(text: str) -> list[str]:
    """Return every word-like token in normalised form, stopwords included."""
    return _TOKEN_RE.findall(normalize(text))


def content_phrases(text: str, min_len: int = 3) -> Iterator[list[str]]:
    """Yield runs of consecutive content tokens. A stopword or a short token ends a run."""
    run: list[str] = []
    for token in tokenize(text):
        if len(token) < min_len or token in STOPWORDS:
            if run:
                yield run
            run = []
        else:
            run.append(token)
    if run:
        yield run


def content_terms(text: str) -> set[str]:
    """Unigrams and bigrams made of content tokens, used to test whether a CV covers a term."""
    terms: set[str] = set()
    for run in content_phrases(text):
        terms.update(run)
        terms.update(f"{a} {b}" for a, b in zip(run, run[1:]))
    return terms


def term_frequencies(text: str) -> dict[str, int]:
    """Count unigrams and bigrams of content tokens. Bigrams are counted only inside a run."""
    counts: dict[str, int] = {}
    for run in content_phrases(text):
        for word in run:
            counts[word] = counts.get(word, 0) + 1
        for a, b in zip(run, run[1:]):
            phrase = f"{a} {b}"
            counts[phrase] = counts.get(phrase, 0) + 1
    return counts
