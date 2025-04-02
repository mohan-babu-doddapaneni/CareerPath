import re
import docx

def extract_text_from_docx(docx_path):
    """Extract text from a .docx file"""
    doc = docx.Document(docx_path)
    return "\n".join([para.text.strip() for para in doc.paragraphs if para.text.strip()])

def extract_total_experience(text):
    """Extract total years of experience (e.g., '6 years')"""
    match = re.search(r"(\d+)\s+years?", text, re.IGNORECASE)
    return match.group(0) if match else "Experience Not Found"

def extract_experience(text):
    """Extract work experience details based on pattern matching"""
    
    experience_sections = []
    
    # Define job title keywords (add more if needed)
    job_titles = [
        "Software Engineer", "Senior Software Engineer", "Technology Analyst",
        "Developer", "Software Developer", "Data Engineer", "System Analyst", "Developer", "Tester"
    ]

    # Regex pattern to capture job experience (Job Title, Duration)
    duration_pattern = r"\(([\w\s-]+ to [\w\s-]+)\)"

    lines = text.split("\n")
    company = None
    job_title = None
    duration = None
    
    for i, line in enumerate(lines):
        # Check if the line contains a job title
        for title in job_titles:
            if title.lower() in line.lower():
                job_title = title
                company = lines[i - 1] if i > 0 else "Unknown"
                
                # Extract duration using regex
                match = re.search(duration_pattern, line)
                if match:
                    duration = match.group(1)
                else:
                    duration = "Unknown Duration"
                
                experience_sections.append({
                    "Company": company.strip(),
                    "Job Title": job_title.strip(),
                    "Duration": duration.strip()
                })
                break  # Stop checking job titles after finding a match
    
    return experience_sections

def parse_resume(docx_path):
    text = extract_text_from_docx(docx_path)
    return {
        "Total Experience": extract_total_experience(text),
        "Experience": extract_experience(text),
    }


if __name__ == '__main__':
        
    resume_path = "CV.docx"  
    resume_data = parse_resume(resume_path)


    print(f"Total Experience: {resume_data['Total Experience']}\n")
    print("Work Experience:")
    for exp in resume_data["Experience"]:
        print(f"Company: {exp['Company']}")
        print(f"Job Title: {exp['Job Title']}")
        print(f"Duration: {exp['Duration']}")
        print("-" * 40)
