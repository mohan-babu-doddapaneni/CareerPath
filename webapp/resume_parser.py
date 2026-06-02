"""Resume parsing: text extraction (.docx and .pdf), plus skill, education,
contact and experience extraction.

This is the single source of truth for resume parsing; ``parse_exp`` delegates
here so the docx/pdf handling isn't duplicated.
"""
import os
import csv
import re
import functools
import logging

import docx

logger = logging.getLogger(__name__)

# Fallback vocabulary, used only if the dataset CSVs can't be read.
_FALLBACK_SKILLS = ['Trello', 'PostgreSQL', 'Git', 'TypeScript', 'Asana', 'PyTorch', 'Blender', 'Pandas', 'C#', 'Flutter', 'Python', 'Jupyter', 'Unity', 'TailwindCSS', 'Truffle', 'Tableau', 'R', 'JavaScript', 'Android Studio', 'Prometheus', 'Jenkins', 'HTML', 'Scikit-Learn', 'GitHub', 'Nagios', 'Power BI', 'Azure DevOps', 'SASS', 'Agile', 'AWS Sagemaker', 'JUnit', 'Jira', 'Nginx', 'Bash', 'SQL', 'Selenium', 'React Native', 'Ruby on Rails', 'TensorFlow', 'Matplotlib', 'Firebase', 'Node.js', 'Kubernetes', 'Docker', 'Scrum', 'Figma', 'MongoDB', 'Keras', 'Redis', 'OpenCV', 'Swift', 'ASP.NET', 'Terraform', 'Ansible', 'Spring Boot', 'Kotlin', 'Express.js', 'C', 'CSS', 'Angular', 'Azure', 'AWS', 'Solidity', 'Vue', 'React', 'Java', 'Google Cloud', 'MySQL', 'Flask', 'Webpack', 'Machine Learning', 'Lua', 'Postman', 'Vite', 'Django', 'C++']

SUPPORTED_EXTENSIONS = ('.docx', '.pdf')


def _filename(source):
    """Best-effort filename for a path string or an uploaded file object."""
    name = getattr(source, 'name', source)
    return name if isinstance(name, str) else ''


def extract_text(source):
    """Extract plain text from a .docx or .pdf file (path or file-like)."""
    name = _filename(source).lower()

    # Reset file-like objects so repeated reads work.
    if hasattr(source, 'seek'):
        try:
            source.seek(0)
        except Exception:
            pass

    if name.endswith('.pdf'):
        from pypdf import PdfReader
        reader = PdfReader(source)
        return "\n".join((page.extract_text() or "") for page in reader.pages)

    # Default to .docx
    document = docx.Document(source)
    return "\n".join(para.text for para in document.paragraphs)


# Backwards-compatible alias.
def extract_text_from_docx(source):
    return extract_text(source)


def extract_email(text):
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return match.group() if match else None


def extract_phone_number(text):
    match = re.search(r"\+?\d[\d\s\-\(\)]{8,}\d", text)
    return match.group() if match else None


@functools.lru_cache(maxsize=1)
def load_skill_vocabulary():
    """Build the skill vocabulary from the bundled datasets (deduplicated
    case-insensitively), instead of a hard-coded list, so it stays in sync
    with the data. Falls back to a built-in list if the CSVs are missing."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Keep the first casing seen as canonical (datasets mix JavaScript/Javascript).
    skills = {}
    for filename, column in (("SkillsDataset.csv", "Skills"),
                             ("career_path_dataset.csv", "Skills")):
        path = os.path.join(base_dir, filename)
        try:
            with open(path, encoding="utf-8-sig") as csvfile:
                for row in csv.DictReader(csvfile):
                    for token in (row.get(column) or "").split(","):
                        token = token.strip()
                        if token:
                            skills.setdefault(token.lower(), token)
        except FileNotFoundError:
            continue
    return sorted(skills.values()) if skills else _FALLBACK_SKILLS


def extract_skills(text):
    skills_list = load_skill_vocabulary()
    # Match whole tokens only so single-letter skills like "R"/"C" don't match
    # every word, and "Java" doesn't match inside "JavaScript". The boundaries
    # treat +, # and . as part of a skill token (e.g. C++, C#, Node.js).
    lowered = text.lower()
    found_skills = []
    for skill in skills_list:
        pattern = r'(?<![\w+#.])' + re.escape(skill.lower()) + r'(?![\w+#])'
        if re.search(pattern, lowered):
            found_skills.append(skill)
    return found_skills


def extract_education(text):
    education_keywords = ["Bachelor", "Masters", "PhD", "BSc", "MSc", "B.Tech", "M.Tech"]
    return [kw for kw in education_keywords if kw.lower() in text.lower()]


def extract_total_experience(text):
    """Extract total years of experience (e.g. '6 years')."""
    match = re.search(r"(\d+)\s+years?", text, re.IGNORECASE)
    return match.group(0) if match else "Experience Not Found"


def extract_experience(text):
    """Extract work-experience entries (Company, Job Title, Duration)."""
    job_titles = [
        "Senior Software Engineer", "Software Engineer", "Technology Analyst",
        "Software Developer", "Data Engineer", "System Analyst", "Developer", "Tester",
    ]
    duration_pattern = r"\(([\w\s-]+ to [\w\s-]+)\)"

    sections = []
    lines = text.split("\n")
    for i, line in enumerate(lines):
        for title in job_titles:
            if title.lower() in line.lower():
                match = re.search(duration_pattern, line)
                sections.append({
                    "Company": (lines[i - 1] if i > 0 else "Unknown").strip(),
                    "Job Title": title.strip(),
                    "Duration": (match.group(1) if match else "Unknown Duration").strip(),
                })
                break
    return sections


def parse_resume(source):
    """Parse a resume file and return all extracted fields in one pass."""
    text = extract_text(source)
    return {
        "Email": extract_email(text),
        "Phone": extract_phone_number(text),
        "Skills": extract_skills(text),
        "Education": extract_education(text),
        "Total Experience": extract_total_experience(text),
        "Experience": extract_experience(text),
    }


if __name__ == '__main__':
    print(parse_resume("CV.docx"))
