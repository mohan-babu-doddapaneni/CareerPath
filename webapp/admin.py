from django.contrib import admin
from .models import Users, WorkExperience, Resumes, Resume_skills, Resume_education, Resume_experience, SkillsDataset, performance, dataset

# Register your models here.
admin.site.register(Users)
admin.site.register(WorkExperience)
admin.site.register(Resumes)
admin.site.register(Resume_skills)
admin.site.register(Resume_education)
admin.site.register(Resume_experience)
admin.site.register(SkillsDataset)
admin.site.register(performance)
admin.site.register(dataset)
