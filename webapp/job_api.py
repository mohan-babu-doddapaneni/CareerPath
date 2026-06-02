"""Live job-listing search with graceful provider fallback.

Resolution order (first one that returns results wins):
  1. Adzuna  - real roles + location + salary, when ADZUNA_APP_ID / ADZUNA_APP_KEY
               are configured (free tier: https://developer.adzuna.com/).
  2. Remotive - keyless remote-jobs API; works with no signup.
  3. Local   - the bundled `dataset` table, so the page never breaks (e.g. when
               the host has no outbound network).

Every provider returns a list of normalized dicts:
    {title, company, location, salary, url, description, source}
"""
import os
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

TIMEOUT = 8  # seconds


def _adzuna(role, location, limit):
    app_id = os.environ.get("ADZUNA_APP_ID")
    app_key = os.environ.get("ADZUNA_APP_KEY")
    if not (app_id and app_key):
        return None  # not configured -> let caller fall through

    country = os.environ.get("ADZUNA_COUNTRY", "gb").lower()
    url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"
    params = {
        "app_id": app_id,
        "app_key": app_key,
        "what": role or "",
        "results_per_page": limit,
        "content-type": "application/json",
    }
    if location:
        params["where"] = location

    resp = requests.get(url, params=params, timeout=TIMEOUT)
    resp.raise_for_status()
    results = resp.json().get("results", [])

    jobs = []
    for r in results[:limit]:
        salary_min = r.get("salary_min")
        salary_max = r.get("salary_max")
        if salary_min and salary_max:
            salary = f"{int(salary_min):,} - {int(salary_max):,}"
        elif salary_min:
            salary = f"{int(salary_min):,}+"
        else:
            salary = "Not disclosed"
        jobs.append({
            "title": r.get("title", "").strip(),
            "company": (r.get("company") or {}).get("display_name", "Unknown"),
            "location": (r.get("location") or {}).get("display_name", "N/A"),
            "salary": salary,
            "url": r.get("redirect_url", ""),
            "description": (r.get("description") or "")[:300],
            "source": "Adzuna",
        })
    return jobs


def _remotive(role, location, limit):
    params = {"limit": limit}
    if role:
        params["search"] = role
    resp = requests.get("https://remotive.com/api/remote-jobs", params=params, timeout=TIMEOUT)
    resp.raise_for_status()
    results = resp.json().get("jobs", [])

    jobs = []
    for r in results[:limit]:
        jobs.append({
            "title": r.get("title", "").strip(),
            "company": r.get("company_name", "Unknown"),
            "location": r.get("candidate_required_location") or "Remote",
            "salary": r.get("salary") or "Not disclosed",
            "url": r.get("url", ""),
            "description": (r.get("description") or "")[:300],
            "source": "Remotive",
        })
    return jobs


def _local(role, location, limit):
    """Offline fallback using the seeded career dataset."""
    from .models import dataset

    qs = dataset.objects.all()
    if role:
        qs = qs.filter(predicted_job_title__icontains=role)
    if location:
        qs = qs.filter(company_location__icontains=location)

    jobs = []
    for r in qs[:limit]:
        jobs.append({
            "title": r.predicted_job_title,
            "company": r.company_name,
            "location": r.company_location,
            "salary": f"{r.salary_usd:,} USD",
            "url": "",
            "description": f"Skills: {r.skills} | Experience: {r.years_of_experience} yrs | {r.industry}",
            "source": "Sample dataset",
        })
    return jobs


def search_jobs(role, location="", limit=10):
    """Return (jobs, source_label). Tries live providers, then falls back."""
    for provider in (_adzuna, _remotive):
        try:
            jobs = provider(role, location, limit)
            if jobs:
                return jobs, jobs[0]["source"]
        except Exception as exc:  # network/parse errors -> try the next provider
            logger.warning("Job provider %s failed: %s", provider.__name__, exc)

    jobs = _local(role, location, limit)
    label = "Sample dataset (live sources unavailable)" if jobs else "No results"
    return jobs, label
