import re
import docx
import spacy

nlp = spacy.load("en_core_web_sm")

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
    print(text)
    skills_list = ['Trello', 'PostgreSQL', 'Git', 'TypeScript', 'Asana', 'PyTorch', 'Blender', 'Pandas', 'C#', 'Flutter', 'Python', 'Jupyter', 'Unity', 'TailwindCSS', 'Truffle', 'Tableau', 'R', 'JavaScript', 'Android Studio', 'Prometheus', 'Jenkins', 'HTML', 'MERN/MEAN Stack', 'Scikit-Learn', 'GitHub', 'Nagios', 'Power BI', 'Azure DevOps', 'SASS', 'Agile', 'Software Development', 'AWS Sagemaker', 'AWS Redshift', 'JUnit', 'Jira', 'Nginx', 'Bash', 'Hyperledger', 'TestNG', 'SQL', 'Selenium', 'React Native', 'GitLab CI/CD', 'Ruby on Rails', 'Unreal Engine', 'TensorFlow', 'Matplotlib', 'Firebase', 'Autodesk Maya', 'Node.js', 'Wireshark', 'Kubernetes', 'Docker', 'Scrum', 'Kali Linux', 'Figma', 'MongoDB', 'GitHub Actions', 'Keras', 'Django + React', 'Cypress', 'LAMP Stack', 'Redis', 'OpenCV', 'Swift', 'ASP.NET', 'Project Management', 'Assembly', 'Terraform', 'Ansible', 'Spring Boot', 'Kotlin', 'CI/CD Tools', 'Plastic SCM', 'Express.js', 'Adobe XD', 'C', 'CSS', 'Angular', 'Appium', 'Ethereum', 'MetaMask', 'Azure', 'AWS', 'Smart Contracts', 'Ganache', 'MVC', 'Solidity', 'Google Colab', 'Spring Boot + Angular', 'Vue', 'React', 'Java', 'Google Cloud', 'Xcode', 'Metasploit', 'MySQL', 'MS Project', 'Flask', 'Webpack', 'Machine Learning', 'Burp Suite', 'Nessus', 'Lua', 'Postman', 'Remix IDE', 'Vite', 'Django', 'C++']
    found_skills = [skill for skill in skills_list if skill.lower() in text.lower()]
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
