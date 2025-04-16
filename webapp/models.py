from django.db import models
# Create your models here.

class Users(models.Model):
	username=models.CharField(max_length=100)
	name=models.CharField(max_length=100)
	contact=models.CharField(max_length=100)
	email=models.CharField(max_length=100)
	password=models.CharField(max_length=100)

class WorkExperience(models.Model):
    username = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    experience = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.job_title} at {self.company}"



from django.db import models

class Resumes(models.Model):
    username = models.CharField(max_length=255, primary_key=True)  # Set as primary key
    file = models.FileField(upload_to='resumes/')  # Saves files in 'media/resumes/'

    def __str__(self):
        return self.username + " - " + self.file.name

class Resume_skills(models.Model):
    username = models.CharField(max_length=255 )
    skills = models.TextField()  

class Resume_education(models.Model):
    username = models.CharField(max_length=255 )
    degree = models.TextField()  

class Resume_experience(models.Model):
    username = models.CharField(max_length=255 )
    experience = models.CharField(max_length=255)  

class SkillsDataset(models.Model):
    Role = models.CharField(max_length=255 )
    Skills = models.CharField(max_length=255 )
    SoftSkills = models.CharField(max_length=255 )
    AdvancedConcepts = models.CharField(max_length=255 )
    Certifications = models.CharField(max_length=255 )

class performance(models.Model):
    alg_name = models.CharField(max_length=100)
    sc1 = models.FloatField()
    sc2 = models.FloatField()
    sc3 = models.FloatField()
    sc4 = models.FloatField()



class dataset(models.Model):
    job_id = models.CharField(max_length=20, unique=True)
    skills = models.TextField()
    years_of_experience = models.PositiveIntegerField()
    predicted_job_title = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100)
    company_location = models.CharField(max_length=100)
    industry = models.CharField(max_length=100)
    salary_usd = models.PositiveIntegerField()
    education_level = models.CharField(max_length=100)

