"""Backwards-compatible shim.

Experience parsing now lives in ``resume_parser`` (which also handles .pdf and
.docx). This module re-exports those helpers so existing imports keep working.
"""
from .resume_parser import (
    extract_text,
    extract_total_experience,
    extract_experience,
)


def parse_resume(source):
    text = extract_text(source)
    return {
        "Total Experience": extract_total_experience(text),
        "Experience": extract_experience(text),
    }


if __name__ == '__main__':
    data = parse_resume("CV.docx")
    print(f"Total Experience: {data['Total Experience']}\n")
    print("Work Experience:")
    for exp in data["Experience"]:
        print(f"Company: {exp['Company']}")
        print(f"Job Title: {exp['Job Title']}")
        print(f"Duration: {exp['Duration']}")
        print("-" * 40)
