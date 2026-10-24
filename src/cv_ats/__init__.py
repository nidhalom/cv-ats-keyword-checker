"""Compare a CV with a job description: keyword extraction, synonyms and coverage score."""

from .analyze import Report, analyze
from .extract import extract_text
from .skills import find_skills

__all__ = ["Report", "analyze", "extract_text", "find_skills"]
__version__ = "0.1.0"
