import os
import csv
import re
import functools

import docx
import spacy

nlp = spacy.load("en_core_web_sm")

# Fallback vocabulary, used only if the dataset CSVs can't be read.
_FALLBACK_SKILLS = ['Trello', 'PostgreSQL', 'Git', 'TypeScript', 'Asana', 'PyTorch', 'Blender', 'Pandas', 'C#', 'Flutter', 'Python', 'Jupyter', 'Unity', 'TailwindCSS', 'Truffle', 'Tableau', 'R', 'JavaScript', 'Android Studio', 'Prometheus', 'Jenkins', 'HTML', 'Scikit-Learn', 'GitHub', 'Nagios', 'Power BI', 'Azure DevOps', 'SASS', 'Agile', 'AWS Sagemaker', 'JUnit', 'Jira', 'Nginx', 'Bash', 'SQL', 'Selenium', 'React Native', 'Ruby on Rails', 'TensorFlow', 'Matplotlib', 'Firebase', 'Node.js', 'Kubernetes', 'Docker', 'Scrum', 'Figma', 'MongoDB', 'Keras', 'Redis', 'OpenCV', 'Swift', 'ASP.NET', 'Terraform', 'Ansible', 'Spring Boot', 'Kotlin', 'Express.js', 'C', 'CSS', 'Angular', 'Azure', 'AWS', 'Solidity', 'Vue', 'React', 'Java', 'Google Cloud', 'MySQL', 'Flask', 'Webpack', 'Machine Learning', 'Lua', 'Postman', 'Vite', 'Django', 'C++']


@functools.lru_cache(maxsize=1)
def load_skill_vocabulary():
    """Build the skill vocabulary from the bundled datasets (deduplicated),
    instead of a hard-coded list, so it stays in sync with the data."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Deduplicate case-insensitively (the datasets mix "JavaScript"/"Javascript"),
    # keeping the first casing seen as canonical.
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

def extract_text_from_docx(docx_path):
    
    doc = docx.Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_email(text):
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return match.group() if match else None

def extract_phone_number(text):
    match = re.search(r"\+?\d[\d\s\-\(\)]{8,}\d", text)
    return match.group() if match else None


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
    found_education = [keyword for keyword in education_keywords if keyword.lower() in text.lower()]
    return found_education



def parse_resume(docx_path):
    text = extract_text_from_docx(docx_path)
    return {
        "Email": extract_email(text),
        "Phone": extract_phone_number(text),
        "Skills": extract_skills(text),
        "Education": extract_education(text),
    }

if __name__ == '__main__':
    resume_data = parse_resume("CV.docx")
    print(resume_data)
