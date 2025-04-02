from django.db import models

# Create your models here.

class Users(models.Model):
	username=models.CharField(max_length=100)
	name=models.CharField(max_length=100)
	contact=models.CharField(max_length=100)
	email=models.CharField(max_length=100)
	password=models.CharField(max_length=100)

class Education(models.Model):
    username = models.CharField(max_length=255)
    degree = models.CharField(max_length=255)
    institution = models.CharField(max_length=255)
    start_year = models.DateField()
    end_year = models.DateField(null=True, blank=True)
    score = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.degree} at {self.institution}"

class WorkExperience(models.Model):
    username = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    experience = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.job_title} at {self.company}"

class Skills(models.Model):
    username = models.CharField(max_length=255)
    skills = models.CharField(max_length=100)

    def __str__(self):
        return self.skill_name
