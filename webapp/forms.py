from django import forms
from .models import Resumes

class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = Resumes
        fields = ['username', 'file']
