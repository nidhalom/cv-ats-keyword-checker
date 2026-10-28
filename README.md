# cv-ats-keyword-checker

A command line tool that compares a CV (`.txt`, `.md`, `.docx` or `.pdf`) with a job description. It reports which
technical skills and keywords from the job appear in the CV, which are missing, and a coverage score.
Synonyms are understood, so "Golang" counts as "Go" and "Postgres" counts as "PostgreSQL".

## Features

- Reads CVs and job descriptions from TXT, Markdown, DOCX (paragraphs and tables) and PDF (via `pypdf`).
- Built-in dictionary of about 60 technical skills with synonyms (for example `k8s` to Kubernetes,
  `nodejs` to Node.js, `ci/cd` to CI/CD). Longer phrases win over shorter ones, so "Docker Compose" is not also
  counted as a separate "Docker" match. A CV listing "Docker Compose" also counts as "Docker".
- Generic keyword extraction: unigrams and bigrams from the job description, with French and English stopwords
  and common job-ad filler words removed. Bigrams need at least two occurrences.
- Coverage score: skills weigh 2 points, generic keywords weigh 1 point.
- Plain text report or JSON output, and an optional `--min-score` threshold that sets the exit status.
- Works offline. No API keys, no network calls.

## Quick start

Requires Python 3.12.

```bash
git clone https://github.com/nidhalom/cv-ats-keyword-checker.git
cd cv-ats-keyword-checker
python -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest -q
cv-ats check --cv examples/cv_sample.txt --jd examples/job_description.txt
```

Use your own files:

```bash
cv-ats check --cv path/to/cv.pdf --jd path/to/job.docx --top 20
cv-ats check --cv cv.docx --jd job.txt --json > report.json
cv-ats check --cv cv.docx --jd job.txt --min-score 70   # exit status 1 if below 70
```

## Example output

Real output from the sample files in `examples/` (`cv_sample.txt` against `job_description.txt`):

```
CV:              examples/cv_sample.txt
Job description: examples/job_description.txt
Coverage score:  54.1%

Skills required by the job: 13
  matched: Agile, Docker, GitHub Actions, Go, PostgreSQL, REST API, SQL, Unit Testing
  missing: CI/CD, Kubernetes, Next.js, Redis, TypeScript

Generic keywords checked: 11
  matched: backend, services, automated, data
  missing: caching, communication, compiled, containerised, coverage, dashboards, deploy
```

The sample CV says "Golang", "Postgres" and "Docker Compose", and all three are matched to their canonical skills.
The CI line in the CV reads "CI pipelines", not "CI/CD", so CI/CD is reported as missing. That is correct for this text.

## Project structure

```
src/cv_ats/
  extract.py   reads txt, md, docx and pdf into plain text
  text.py      normalisation (accents, case), tokenising, stopwords (FR and EN), term counts
  skills.py    skill dictionary with synonyms and the matcher
  analyze.py   compares CV and job, builds the report and the score
  cli.py       `cv-ats check` command
tests/         unit tests and CLI tests (37 tests, offline, a few seconds)
examples/      sample CV and job description
```

## How it works

1. The text is extracted from each file and normalised: accents are removed, text is lowercased, and curly apostrophes
   become straight ones.
2. Skills are found with regular expressions built from the dictionary aliases. Boundary checks stop "go" matching
   inside "algorithm". Some skills are matched case-sensitively, so "Go" the language does not match "go to market".
   When matches overlap, the longest one wins.
3. Generic keywords come from the job text: runs of content words (no stopwords, no fillers, at least 3 letters) give
   unigrams and bigrams. The most frequent ones are kept.
4. A keyword counts as covered if the CV contains it as a skill or as a term.

## Limitations

- The skill dictionary is small and English-centric. Add entries to `SKILLS` in `src/cv_ats/skills.py` for other
  technologies.
- Matching is lexical. The tool does not understand that "built APIs in Go" implies "REST" or that two phrases mean the
  same thing.
- Generic keywords on short job descriptions are noisy. Words like "communication" are kept on purpose.
- Scanned PDFs (images without a text layer) produce no text. The tool reports this as an error.
- The score is a rough guide for tailoring a CV, not a replica of any specific applicant tracking system.

## License

MIT. See [LICENSE](LICENSE).
