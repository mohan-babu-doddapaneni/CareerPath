# Generated by Django 4.2.20 on 2025-03-25 19:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0002_resume_education_resume_experience_resume_skills'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Education',
        ),
        migrations.DeleteModel(
            name='Skills',
        ),
    ]
