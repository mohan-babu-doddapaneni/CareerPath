# Career Path Recommendation System

## Introduction
The **Career Path Recommendation System** is an AI-driven web application that helps
users evaluate their career suitability, identify skill gaps against target roles, and
get a recommended job title based on their resume and skills.

## Features
- **User Authentication** (email/password, passwords stored as salted PBKDF2 hashes)
- **Resume Analysis** (uploads a `.docx` or `.pdf`, extracts skills, education and experience)
- **Skill-Gap Analysis** (compares your skills against a target role's required skills)
- **AI Role Prediction** (Random Forest model predicts a suitable job title)
- **Live Job Search** (real listings by role/location via Adzuna or keyless Remotive, with a local fallback)
- **Model Comparison Dashboard** (Random Forest, Naive Bayes, SVM, Neural Network metrics)
- **Admin Dashboard** (manage the skills and career datasets)

## Tech Stack
| Category   | Technology |
|------------|------------|
| **Frontend** | HTML, Bootstrap, jQuery |
| **Backend**  | Django 5.2 |
| **ML / NLP** | scikit-learn, spaCy, pandas, matplotlib |
| **Static**   | WhiteNoise |
| **Database** | PostgreSQL in production (via `DATABASE_URL`); SQLite locally |
| **Server**   | gunicorn |
| **Hosting**  | Render (see below) |

## Running Locally

```bash
# 1. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# 3. Apply migrations (uses a local SQLite DB by default — no setup needed)
python manage.py migrate

# 4. Run the development server
python manage.py runserver
```

Then open http://127.0.0.1:8000/. The admin section is at `/adminlogin/`
(default credentials: `admin` / `admin`).

## Running Tests

```bash
python manage.py test webapp
```

The suite covers resume parsing (skill matching, email/phone/experience),
the live-job-search provider fallback, the ML classifier, authentication
(including legacy-hash upgrade), the data seeder, and the key views.

### Configuration (environment variables)
| Variable | Purpose | Default |
|----------|---------|---------|
| `DJANGO_SECRET_KEY` | Django secret key | insecure dev key |
| `DJANGO_DEBUG` | Debug mode | `True` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated allowed hosts | `*,.vercel.app,.onrender.com` |
| `DATABASE_URL` | Database connection string | local SQLite file |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` | Admin panel login | `admin` / `admin` |
| `ADZUNA_APP_ID` / `ADZUNA_APP_KEY` | Enable real role+location job search (free key at developer.adzuna.com) | unset (uses keyless Remotive, then local fallback) |
| `ADZUNA_COUNTRY` | Adzuna country code | `gb` |

## Deploying a Live Site (Render)

This project ships with a `render.yaml` blueprint and a `build.sh` script.

1. Push this repository to GitHub.
2. Go to https://dashboard.render.com → **New + → Blueprint** and select this repo.
3. Render reads `render.yaml`, provisions a free PostgreSQL database, sets
   `DATABASE_URL`/`DJANGO_SECRET_KEY` automatically, runs `build.sh`
   (install deps + spaCy model + `collectstatic` + `migrate`), and starts the
   app with `gunicorn CareerPath.wsgi:application`.
4. The live URL will be `https://<service-name>.onrender.com`.

> **Note:** Vercel is **not** suitable for this app — scikit-learn + spaCy far
> exceed its serverless function size limit. A container host such as Render,
> Railway, or Fly.io is required.

## Notes on the ML Model

The role classifier is trained on `career_path_dataset.csv`. Cross-validated
accuracy is modest (~25–30% across 9 job titles) because the relationship
between the listed skills and the job title in this sample dataset is weak. The
honest metrics are intentional (the model is evaluated on a held-out split, not
the training data). Accuracy will improve mainly with a richer, better-labelled
dataset rather than a different algorithm.
