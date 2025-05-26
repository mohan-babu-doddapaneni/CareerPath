from django.db import models
# Create your models here.

class Users(models.Model):
    """Represents a user of the application."""
    # username field is used to store the user's email address, which is their unique identifier for login.
    username = models.CharField(max_length=100) 
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=100) # Stores user's contact information, typically a phone number.
    email = models.CharField(max_length=100) # Stores user's email, often redundant if username stores email.
    password = models.CharField(max_length=128) # Stores the hashed password.

class WorkExperience(models.Model):
    """Represents a single work experience entry for a user."""
    # TODO: Consider changing 'username' to a ForeignKey to the Users model for better relational integrity.
    username = models.CharField(max_length=255) 
    job_title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True) # Can be null if it's the current job.
    experience = models.TextField(blank=True, null=True) # Detailed description of the work experience.

    def __str__(self):
        return f"{self.job_title} at {self.company}"

# Note: The import 'from django.db import models' is typically only needed once at the top of the file.
# Removing redundant import if it was here.

class Resumes(models.Model):
    """Represents an uploaded resume file linked to a user."""
    # TODO: 'username' as CharField primary_key is problematic for relational integrity.
    # This should ideally be a OneToOneField or ForeignKey to the Users model.
    # Example: user = models.OneToOneField(Users, on_delete=models.CASCADE, primary_key=True)
    # This change would require significant refactoring (migrations, data handling in views).
    username = models.CharField(max_length=255, primary_key=True)
    file = models.FileField(upload_to='resumes/')  # Saves files in 'media/resumes/'

    def __str__(self):
        return f"Resume for {self.username} - {self.file.name}"

class ResumeSkill(models.Model):
    """Represents skills extracted or manually added from a user's resume."""
    # TODO: Consider changing 'username' to a ForeignKey to the Users model.
    username = models.CharField(max_length=255)
    skills = models.TextField() # Comma-separated skills or a JSON field could be used.

    def __str__(self):
        return f"Skills for {self.username}: {self.skills[:50]}..."

class ResumeEducation(models.Model):
    """Represents education details from a user's resume."""
    # TODO: Consider changing 'username' to a ForeignKey to the Users model.
    # TODO: Consider adding fields like institution, start_year, end_year, score if they were intended.
    username = models.CharField(max_length=255)
    degree = models.TextField()

    def __str__(self):
        return f"Education for {self.username}: {self.degree}"

class ResumeExperience(models.Model):
    """Represents overall experience summary from a user's resume (e.g., total years)."""
    # TODO: Consider changing 'username' to a ForeignKey to the Users model.
    username = models.CharField(max_length=255)
    experience = models.CharField(max_length=255) # e.g., "5 years", "10+ years"

    def __str__(self):
        return f"Experience summary for {self.username}: {self.experience}"

class SkillsDataset(models.Model):
    """Represents a dataset of skills typically required for various job roles."""
    role = models.CharField(max_length=255) # Name of the job role.
    skills = models.CharField(max_length=255) # Technical skills, often comma-separated.
    soft_skills = models.CharField(max_length=255) # Soft skills, often comma-separated.
    advanced_concepts = models.CharField(max_length=255) # Advanced concepts or specializations.
    certifications = models.CharField(max_length=255) # Suggested or required certifications.

    def __str__(self):
        return f"Skills for role: {self.role}"

class Performance(models.Model):
    """Stores performance metrics for different machine learning algorithms."""
    alg_name = models.CharField(max_length=100) # Name of the algorithm.
    # sc1, sc2, sc3, sc4 are likely performance scores like accuracy, precision, recall, F1-score.
    # TODO: Rename sc1-sc4 to more descriptive names if their specific meaning is confirmed (e.g., accuracy, precision).
    sc1 = models.FloatField() # e.g., Accuracy
    sc2 = models.FloatField() # e.g., Precision
    sc3 = models.FloatField() # e.g., Recall
    sc4 = models.FloatField() # e.g., F1-score

    def __str__(self):
        return f"Performance metrics for {self.alg_name}"

class JobDataset(models.Model):
    """Represents a dataset of job postings or job-related data."""
    job_id = models.CharField(max_length=20, unique=True) # Unique identifier for the job.
    skills = models.TextField() # Skills required for the job.
    years_of_experience = models.PositiveIntegerField()
    predicted_job_title = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100)
    company_location = models.CharField(max_length=100)
    industry = models.CharField(max_length=100)
    salary_usd = models.PositiveIntegerField()
    education_level = models.CharField(max_length=100)

