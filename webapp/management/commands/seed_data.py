"""Populate the database from the bundled CSV datasets.

Safe to run repeatedly (e.g. on every deploy): it refreshes the skills
reference table and upserts the career/job rows by their unique Job_ID.

Usage:
    python manage.py seed_data
"""
import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from webapp.models import SkillsDataset, dataset


class Command(BaseCommand):
    help = "Load SkillsDataset.csv and career_path_dataset.csv into the database."

    def handle(self, *args, **options):
        self._seed_skills()
        self._seed_careers()
        self.stdout.write(self.style.SUCCESS("Seeding complete."))

    def _seed_skills(self):
        path = os.path.join(settings.BASE_DIR, "SkillsDataset.csv")
        if not os.path.exists(path):
            self.stdout.write(self.style.WARNING(f"Skipping skills: {path} not found"))
            return

        # Reference data with no natural key: replace wholesale.
        SkillsDataset.objects.all().delete()
        created = 0
        with open(path, encoding="utf-8-sig") as csvfile:
            for row in csv.DictReader(csvfile):
                SkillsDataset.objects.create(
                    Role=row["Role"],
                    Skills=row["Skills"],
                    SoftSkills=row["Soft Skills"],
                    AdvancedConcepts=row["Advanced Concepts"],
                    Certifications=row["Suggested Certifications & Courses"],
                )
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Skills roles loaded: {created}"))

    def _seed_careers(self):
        path = os.path.join(settings.BASE_DIR, "career_path_dataset.csv")
        if not os.path.exists(path):
            self.stdout.write(self.style.WARNING(f"Skipping careers: {path} not found"))
            return

        count = 0
        with open(path, encoding="utf-8-sig") as csvfile:
            for row in csv.DictReader(csvfile):
                dataset.objects.update_or_create(
                    job_id=row["Job_ID"],
                    defaults={
                        "skills": row["Skills"],
                        "years_of_experience": int(row["Years_of_Experience"]),
                        "predicted_job_title": row["Predicted_Job_Title"],
                        "company_name": row["Company_Name"],
                        "company_location": row["Company_Location"],
                        "industry": row["Industry"],
                        "salary_usd": int(row["Salary (USD)"]),
                        "education_level": row["Education_Level"],
                    },
                )
                count += 1
        self.stdout.write(self.style.SUCCESS(f"Career/job rows loaded: {count}"))
