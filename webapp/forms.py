from django import forms
from django.core.exceptions import ValidationError
from .models import Resumes, ResumeEducation, WorkExperience, ResumeSkill

class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = Resumes
        fields = ['username', 'file'] # Keeping 'username' as per instructions for now

    def clean_file(self):
        uploaded_file = self.cleaned_data.get('file')
        if uploaded_file:
            if not uploaded_file.name.endswith(".docx"):
                raise ValidationError("Only .docx files are allowed.")
        # It's also good practice to check file size, content type more robustly if needed,
        # but for this task, extension check matches the existing view logic.
        return uploaded_file

class UserRegistrationForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    contact = forms.CharField(max_length=100, required=False) # Assuming contact is optional
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean_email(self):
        # Assuming your custom Users model is imported if you need to check uniqueness here
        # from .models import Users 
        # email = self.cleaned_data.get('email')
        # if Users.objects.filter(username=email).exists(): # Or filter(email=email) depending on model
        #     raise ValidationError("This email address is already registered.")
        # For now, this check is primarily handled in the view or by model's unique=True constraint if username is email.
        # This form doesn't directly link to Users model, so direct check here is less straightforward
        # without access to request or User model details.
        # The view logic will handle user existence checks.
        return self.cleaned_data.get('email')

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        
        return cleaned_data

class EducationForm(forms.ModelForm):
    class Meta:
        model = ResumeEducation
        fields = ['degree']
        # 'username' will be set in the view from the session

class WorkExperienceForm(forms.ModelForm):
    class Meta:
        model = WorkExperience
        fields = ['job_title', 'company', 'start_date', 'end_date', 'experience']
        # 'username' will be set in the view from the session
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'experience': forms.Textarea(attrs={'rows': 4}),
        }

class SkillForm(forms.ModelForm):
    class Meta:
        model = ResumeSkill
        fields = ['skills']
        # 'username' will be set in the view from the session
        widgets = {
            'skills': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter skills, comma-separated'}),
        }
