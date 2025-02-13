# Career Path Recommendation System

## Introduction
The **Career Path Recommendation System** is an AI-driven web application designed to assist users in evaluating their career suitability, identifying skill gaps, and recommending relevant online courses and certifications.

## Features
- **User Authentication** (Email/Password)
- **Resume Analysis** (Extract skills, match career paths)
- **AI-Powered Recommendations** (Skill gaps, improvement suggestions)
- **Job Portal Integration** (Real-time job updates)
- **Interactive Dashboards** (Career insights, progress tracking)
- **Secure Data Handling** (Privacy compliance)

## Tech Stack
| Category      | Technology |
|--------------|------------|
| **Frontend** | Angular.js, Bootstrap, CSS |
| **Backend**  | Python, Flask |
| **ML/NLP**   | Scikit-learn, NLTK, Pandas |
| **Database** | MySQL |
| **Hosting**  | AWS |
| **Version Control** | GitHub |
| **Project Management** | Trello/Jira |

## Installation

### Prerequisites
- Node.js
- Python 3
- MySQL Database
- Git

### Steps to Run the Project
1. **Clone the Repository**
   ```sh
   git clone https://github.com/your-repo-url.git
   cd career-path-recommendation
   ```

2. **Backend Setup**
   ```sh
   cd backend
   python -m venv env
   source env/bin/activate  # On Windows use `env\Scripts\activate`
   pip install -r requirements.txt
   python app.py
   ```

3. **Frontend Setup**
   ```sh
   cd frontend
   npm install
   ng serve --open
   ```

## Usage
1. **Sign Up/Login**
2. **Upload Resume** (Supports .pdf, .docx formats)
3. **View Career Recommendations**
4. **Follow Skill Improvement Suggestions**
5. **Apply for Jobs via Integrated Portals**

## Folder Structure
```
career-path-recommendation/
│── backend/
│   ├── app.py
│   ├── models/
│   ├── routes/
│   ├── static/
│   ├── templates/
│── frontend/
│   ├── src/
│   ├── angular.json
│── README.md
│── requirements.txt
│── package.json
│── .gitignore
```

## Contributors
- **Poornachandra Reddy Ramireddy**
- **Mohan Babu Doddapaneni**
- **Shivaprasad Yelijala**

## License
This project is licensed under the MIT License - see the LICENSE file for details.
