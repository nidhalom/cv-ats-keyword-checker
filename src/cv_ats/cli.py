"""Command line interface: ``cv-ats check --cv CV --jd JOB [--json] [--min-score N]``."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence

from .analyze import analyze
from .extract import UnsupportedFormatError, extract_text


def _format_report(report, cv_name: str, jd_name: str) -> str:
    lines = [
        f"CV:              {cv_name}",
        f"Job description: {jd_name}",
        f"Coverage score:  {report.score:.1f}%",
        "",
        f"Skills required by the job: {len(report.skills_required)}",
        f"  matched: {', '.join(report.skills_matched) or '-'}",
        f"  missing: {', '.join(report.skills_missing) or '-'}",
        "",
        f"Generic keywords checked: {len(report.terms_required)}",
        f"  matched: {', '.join(report.terms_matched) or '-'}",
        f"  missing: {', '.join(report.terms_missing) or '-'}",
    ]
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cv-ats", description="Compare a CV with a job description.")
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check", help="Print matched and missing keywords for one CV and one job.")
    check.add_argument("--cv", required=True, help="CV file (.txt, .md, .docx or .pdf)")
    check.add_argument("--jd", required=True, help="Job description file (.txt, .md, .docx or .pdf)")
    check.add_argument("--top", type=int, default=15, help="How many generic keywords to check (default 15)")
    check.add_argument("--json", action="store_true", help="Print the report as JSON")
    check.add_argument(
        "--min-score",
        type=float,
        default=None,
        help="Exit with status 1 when the coverage score is below this value",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        cv_text = extract_text(args.cv)
        jd_text = extract_text(args.jd)
    except (FileNotFoundError, UnsupportedFormatError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if not cv_text.strip() or not jd_text.strip():
        print("error: the CV or the job description has no extractable text", file=sys.stderr)
        return 2

    report = analyze(cv_text, jd_text, top_terms=args.top)
    if args.json:
        print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
    else:
        print(_format_report(report, args.cv, args.jd))

    if args.min_score is not None and report.score < args.min_score:
        return 1
    return 0
