from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User # Not directly used for custom Users model, but good for reference
from django.contrib.auth import authenticate, login # Authenticate and login are not used with custom user model directly here
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from .models import Users, WorkExperience, Resumes, ResumeSkill, ResumeEducation, ResumeExperience, SkillsDataset, Performance, JobDataset # Updated model names
from .forms import UserRegistrationForm, EducationForm, WorkExperienceForm, SkillForm, ResumeUploadForm # Import new forms
import csv
import os 
from django.conf import settings 
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist 

# Machine Learning specific imports
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
#from sklearn.linear_model import LogisticRegression # Example of an unused import
from sklearn.naive_bayes import BernoulliNB
from sklearn.svm import LinearSVC


def home(request):
    """Renders the home page."""
    return render(request, "index.html")


# Helper Functions for CRUD operations

def _ensure_user_session(request):
    """
    Ensures that a user session (identified by 'email' in session data) exists.
    
    Args:
        request: The HttpRequest object.
        
    Returns:
        The user's email from the session.
        
    Raises:
        Http404: If 'email' is not found in the session.
    """
    if "email" not in request.session:
        raise Http404("User session not found. Please login.") 
    return request.session["email"]

def _handle_add_operation(request, model_class, form_class, template_name, success_msg_text):
    """
    Handles the creation of a new model instance using a Django ModelForm.
    Assumes the model_class has a 'username' field to be populated by the user's email.
    
    Args:
        request: The HttpRequest object.
        model_class: The Django model class (used for context, form handles model).
        form_class: The Django ModelForm class for creating the instance.
        template_name: The name of the template to render.
        success_msg_text: The success message to display.
        
    Returns:
        HttpResponse: Renders the specified template with the form.
    """
    user_email = _ensure_user_session(request)
    
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            if hasattr(instance, 'username'): # Set username if model has it
                instance.username = user_email
            instance.save()
            messages.success(request, success_msg_text)
            # After successful POST, redirect or show success message with a new form
            # For simplicity and consistency with previous behavior, re-render with new form and message.
            # Consider redirecting to a list view or the item's detail view (Post/Redirect/Get pattern).
            return render(request, template_name, {'form': form_class(), 'msg': success_msg_text})
        else:
            # Form is invalid, re-render with errors
            return render(request, template_name, {'form': form, 'msg_error': 'Please correct the errors below.'})
    else: # GET request
        form = form_class()
        return render(request, template_name, {'form': form})

def _handle_edit_operation(request, model_class, form_class, template_name, success_msg_text, redirect_view_name):
    """
    Handles editing an existing model instance using a Django ModelForm.
    
    Args:
        request: The HttpRequest object.
        model_class: The Django model class (used for fetching instance).
        form_class: The Django ModelForm class for editing.
        template_name: The template for the edit form.
        success_msg_text: Success message after update.
        redirect_view_name: The name of the view to redirect to after update.
        
    Returns:
        HttpResponse: Renders template or redirects.
    """
    user_email = _ensure_user_session(request)
    item_id = request.GET.get('id') if request.method == 'GET' else request.POST.get('id')

    if not item_id:
        raise Http404(f"{model_class.__name__} ID not provided.")

    # Fetch the instance, ensuring user ownership if applicable
    instance_kwargs = {'id': item_id}
    if hasattr(model_class, 'username'):
        instance_kwargs['username'] = user_email
    
    try:
        model_instance = get_object_or_404(model_class, **instance_kwargs)
    except Http404:
        messages.error(request, f"{model_class.__name__} not found or you do not have permission to access this item.")
        return redirect(redirect_view_name) # Or a more generic error page/dashboard

    if request.method == 'POST':
        form = form_class(request.POST, instance=model_instance)
        if form.is_valid():
            form.save()
            messages.success(request, success_msg_text)
            return redirect(redirect_view_name)
        else:
            # Form is invalid, re-render with errors
             return render(request, template_name, {'form': form, 'data': model_instance, 'msg_error': 'Please correct the errors below.'})
    else: # GET request
        form = form_class(instance=model_instance)
        return render(request, template_name, {'form': form, 'data': model_instance}) # 'data' might be used by some templates for hidden ID field

def _handle_delete_operation(request, model_class, success_msg_text, redirect_view_name): 
    # This helper seems fine as is, forms are not typically used for simple deletes.
    # Ownership check could be enhanced here as noted in its docstring.
    """
    Handles deletion of a model instance via POST request.
    Ownership check is rudimentary (checks if model has 'username' and if it matches session email
    if an instance is fetched with username, but current implementation fetches by id only before delete).
    
    Args:
        request: The HttpRequest object.
        model_class: The Django model class.
        success_msg_text: Success message after deletion.
        redirect_view_name: The name of the view to redirect to after deletion.
        
    Returns:
        HttpResponse: Redirects to specified view.
    """
    user_email = _ensure_user_session(request) # Ensures user is logged in
    
    if request.method == 'POST':
        item_id = request.POST.get('id')
        if not item_id:
            raise Http404(f"{model_class.__name__} ID not provided for deletion.")

        try:
            # Original views deleted by 'id' only.
            # For stronger security, especially for user-owned data, an ownership check is vital.
            # instance = get_object_or_404(model_class, id=item_id, username=user_email) # If model has username
            instance = get_object_or_404(model_class, id=item_id) 
            
            # Example of an explicit ownership check if instance was fetched by ID only:
            # if hasattr(instance, 'username') and instance.username != user_email:
            #     messages.error(request, "You do not have permission to delete this item.")
            #     return redirect(redirect_view_name) # Or some other appropriate response
            
            instance.delete()
            messages.success(request, success_msg_text)
        except Http404:
            messages.error(request, f"{model_class.__name__} not found.")
        return redirect(redirect_view_name)
    else:
        # HTTP GET method is not appropriate for delete operations.
        messages.warning(request, "Delete operation should be performed via POST.")
        return redirect(redirect_view_name)


def register(request):
    """Handles new user registration."""
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            name = cleaned_data['name']
            contact = cleaned_data['contact']
            email_address = cleaned_data['email']
            password = cleaned_data['password']
            
            hashed_password = make_password(password)

            # TODO: Check if user with this email (username) already exists before creating
            # This check should ideally be in the form's clean_email or clean method.
            if Users.objects.filter(username=email_address).exists():
                messages.error(request, "This email address is already registered.")
                return render(request, "register.html", {'form': form})

            Users.objects.create(
                name=name, 
                contact=contact, 
                username=email_address, 
                email=email_address, 
                password=hashed_password
            )
            messages.success(request, "Account created successfully! Please login.")
            return redirect("login")
        else:
            # Form is invalid, re-render with form containing errors
            return render(request, "register.html", {'form': form})
    else: # GET request
        form = UserRegistrationForm()
    return render(request, "register.html", {'form': form})


def login_user(request):
    """Handles user login."""
    if request.method == "POST":
        email_address = request.POST["email"] # Variable renamed
        password = request.POST["password"]

        # Retrieve the user by username (which stores the email)
        user = Users.objects.filter(username=email_address).first()
        
        # Verify user existence and password
        if user and check_password(password, user.password):
            # Store email in session to indicate logged-in state
            request.session['email'] = email_address 
            messages.success(request, "Logged in successfully!")
            return redirect("dashboard") # Redirect to the user dashboard
        else:
            messages.error(request, "Invalid email or password!")
            # Re-render login page with error
            return render(request, "login.html") 

    return render(request, "login.html") # Render login page for GET requests


def dashboard(request):
    """
    Renders the user's dashboard page.
    Requires 'email' in session.
    """
    user_email = _ensure_user_session(request) # Ensures user is logged in
    user = Users.objects.filter(username=user_email).first()
    if not user:
        # This case should ideally not happen if session email guarantees a user.
        # It might indicate data inconsistency or an issue with user deletion logic.
        messages.error(request, "User not found.")
        return redirect('user_logout') # Log out if user associated with session email is gone
    return render(request, "user_home.html", {'user': user})


def profile(request):
    """Renders the user's profile page, which serves as a container for profile sections."""
    _ensure_user_session(request) # Ensures user is logged in
    # The profile page itself doesn't load data; specific view_... functions do.
    return render(request, "profile.html")


def user_logout(request):
    """Logs the user out by clearing the session."""
    try:
        # Remove 'email' from session to log the user out
        del request.session['email']
        messages.success(request, "You have been logged out.")
    except KeyError:
        # Session 'email' key might already be missing if user was not logged in
        messages.info(request, "You were not logged in.")
    return redirect('login') # Redirect to login page


def user_home(request):
    """
    Renders the user's personalized home/dashboard page after login.
    Displays user's basic information.
    """
    user_email = _ensure_user_session(request) # Ensures user is logged in
    # Fetch the user object. Using get() is better if exactly one object is expected.
    # Using filter().first() is safer if there's any doubt.
    user_data = Users.objects.filter(username=user_email).first()
    if not user_data:
        # Handle case where user might have been deleted after session started
        messages.error(request, "User data not found. Please log in again.")
        return redirect('user_logout')
       
    return render(request, 'user_home.html', {'data': user_data}) # 'data' is used in template


def add_education(request):
    """Handles adding education details for the logged-in user."""
    """Handles adding education details for the logged-in user."""
    return _handle_add_operation(request, ResumeEducation, EducationForm,
                                 'addeducation.html', 'Education data added successfully!')

def add_work_experience(request):
    """Handles adding work experience for the logged-in user."""
    return _handle_add_operation(request, WorkExperience, WorkExperienceForm,
                                 'addworkexperience.html', 'Work experience data added successfully!')

def add_skills(request):
    """Handles adding skills for the logged-in user."""
    return _handle_add_operation(request, ResumeSkill, SkillForm,
                                 'addskills.html', 'Skills data added successfully!')

def view_education(request):
    """Displays education details for the logged-in user on their profile page."""
    user_email = _ensure_user_session(request)
    education_details = ResumeEducation.objects.filter(username=user_email)
    return render(request, 'profile.html', {'educations': education_details, 'st1': True}) # st1 indicates education section

def view_work_experience(request):
    """Displays work experience for the logged-in user on their profile page."""
    user_email = _ensure_user_session(request)
    work_experiences = WorkExperience.objects.filter(username=user_email)
    # ResumeExperience model stores an overall summary, not individual experiences.
    resume_experience_summary = ResumeExperience.objects.filter(username=user_email).first() 
    
    return render(request, 'profile.html', {
        'experiences': work_experiences, # List of detailed WorkExperience objects
        'data': resume_experience_summary, # Single ResumeExperience object (overall summary)
        'st2': True # st2 indicates work experience section
    })

def view_skills(request):
    """Displays skills for the logged-in user on their profile page."""
    user_email = _ensure_user_session(request)
    skills_list = ResumeSkill.objects.filter(username=user_email)
    return render(request, 'profile.html', {'skills': skills_list, 'st3': True}) # st3 indicates skills section



# from .forms import ResumeUploadForm # Already imported at the top

def upload_resume(request):
    """Handles resume uploads, parsing, and saving extracted data, using ResumeUploadForm."""
    user_email = _ensure_user_session(request)
    
    if request.method == "POST":
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # File type validation is now handled in ResumeUploadForm.clean_file()
            uploaded_file = form.cleaned_data['file'] # Use cleaned_data
            
            # Ensure username from form (if still present) matches session user_email
            # The 'username' field in ResumeUploadForm is populated with user_email in GET.
            # If form.cleaned_data['username'] is not user_email, there's a discrepancy.
            if form.cleaned_data.get('username') != user_email:
                 messages.error(request, "User identity mismatch. Please try again.")
                 return redirect("upload_resume")

            # Delete existing resume and related data if replacing
            if Resumes.objects.filter(pk=user_email).exists():
                 Resumes.objects.filter(pk=user_email).delete()
                 ResumeSkill.objects.filter(username=user_email).delete()
                 ResumeEducation.objects.filter(username=user_email).delete()
                 ResumeExperience.objects.filter(username=user_email).delete()

            try:
                # Resume parsing logic
                from .resume_parser import parse_resume as parse_resume_data
                basic_data = parse_resume_data(uploaded_file) # Use the file from cleaned_data
                
                
                parsed_skills_list = basic_data.get('Skills', [])
                skills_text = ", ".join(parsed_skills_list)
                ResumeSkill.objects.update_or_create(username=user_email, defaults={'skills': skills_text})

                parsed_education_list = basic_data.get('Education', [])
                ResumeEducation.objects.filter(username=user_email).delete()
                for edu_entry_text in parsed_education_list:
                    ResumeEducation.objects.create(username=user_email, degree=edu_entry_text)
                
                from .parse_exp import parse_resume as parse_experience_data
                resume_experience_info = parse_experience_data(uploaded_file)
                total_experience_text = resume_experience_info.get('Total Experience', '')
                ResumeExperience.objects.update_or_create(username=user_email, defaults={'experience': total_experience_text})

            except ImportError:
                messages.error(request, "Resume parsing modules are not available.")
                return redirect("upload_resume")
            except Exception as e: # Catch specific parsing errors if possible
                messages.error(request, f"Error parsing resume: {e}")
                return redirect("upload_resume")

            # Save the Resumes model instance (file record)
            # The form's 'username' is already cleaned_data['username'] which should be user_email
            # If 'username' is PK on Resumes, form.save() will create it.
            # Ensure the form instance has the correct PK before saving.
            resume_instance = form.save(commit=False)
            resume_instance.username = user_email # Explicitly set PK
            resume_instance.save() # This saves the Resumes model instance
            
            education_for_edit_page = ResumeEducation.objects.filter(username=user_email)
            
            return render(request, "upload_resume_edit.html", {
                "exp": total_experience_text, 
                'skills_txt': skills_text, 
                'education': education_for_edit_page
            })
        else:
            # Form is invalid, re-render with form containing errors
            # messages.error(request, "Form is not valid. Please correct the errors.") # This is generic
            # The form itself will contain specific field errors.
            pass # Fall through to render the form again.
            
    else: # GET request
        # Initialize form with username (email) for the Resumes model's PK.
        form = ResumeUploadForm(initial={'username': user_email})

    user_resumes = Resumes.objects.filter(username=user_email)
    return render(request, "upload_resume.html", {"form": form, "resumes": user_resumes})

def delete_resume(request):
    """Deletes a user's resume and all associated parsed data."""
    user_email = _ensure_user_session(request)
    
    # Cascading delete is not set up in models, so manual deletion of related data is needed.
    Resumes.objects.filter(username=user_email).delete()
    ResumeEducation.objects.filter(username=user_email).delete()
    ResumeExperience.objects.filter(username=user_email).delete()
    ResumeSkill.objects.filter(username=user_email).delete()
    
    messages.success(request, "Resume and associated data deleted successfully!")
    return redirect("upload_resume")


def update_resume_data(request):
    """Updates resume-derived data (skills, experience, education) after manual editing by user."""
    user_email = _ensure_user_session(request)
    
    if request.method == "POST":
        skills_text = request.POST.get('skills')
        experience_summary = request.POST.get('exp')

        # Update skills
        ResumeSkill.objects.update_or_create(username=user_email, defaults={'skills': skills_text})
        
        # Update overall experience summary
        ResumeExperience.objects.update_or_create(username=user_email, defaults={'experience': experience_summary})

        # Update individual education records
        education_record_ids = request.POST.getlist('record_id')  
        education_contents = request.POST.getlist('content')

        for record_id, content in zip(education_record_ids, education_contents):
            try:
                education_record = ResumeEducation.objects.get(id=record_id, username=user_email)
                education_record.degree = content
                education_record.save()
            except ResumeEducation.DoesNotExist:
                messages.error(request, f"Education record with ID {record_id} not found or access denied.")
            except Exception as e:
                messages.error(request, f"An error occurred while updating education record ID {record_id}: {e}")
        
        # Update ResumeSkill and ResumeExperience using try-except for .get()
        try:
            skill_instance = ResumeSkill.objects.get(username=user_email)
            skill_instance.skills = skills_text
            skill_instance.save()
        except ResumeSkill.DoesNotExist:
             # if it's acceptable for a user to not have skills record yet, create one
            ResumeSkill.objects.create(username=user_email, skills=skills_text)
        except Exception as e:
            messages.error(request, f"An error occurred while updating skills: {e}")

        try:
            experience_instance = ResumeExperience.objects.get(username=user_email)
            experience_instance.experience = experience_summary
            experience_instance.save()
        except ResumeExperience.DoesNotExist:
            # if it's acceptable for a user to not have experience record yet, create one
            ResumeExperience.objects.create(username=user_email, experience=experience_summary)
        except Exception as e:
            messages.error(request, f"An error occurred while updating experience: {e}")

        messages.success(request, "Resume data updated successfully!")
        return redirect("upload_resume")
        
    return redirect('/')    


def upload_skills_dataset(request):
    """
    Loads skills data from a predefined CSV file into the SkillsDataset model.
    The CSV filename is configured in settings.py (SKILLS_DATASET_FILENAME).
    The file is expected to be in the BASE_DIR of the project.
    """
    # This view is assumed to be for admin/staff use; session check might be needed if not.
    if request.method == 'POST': # Typically, a load operation might not need POST, but keeping as is.
        file_path = os.path.join(settings.BASE_DIR, settings.SKILLS_DATASET_FILENAME)
        
        try:
            SkillsDataset.objects.all().delete() # Clear existing dataset
            with open(file_path, mode='r', encoding="utf-8-sig") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    try:
                        SkillsDataset.objects.create(
                            role=row.get('Role', '').strip(),
                            skills=row.get('Skills', '').strip(),
                            soft_skills=row.get('Soft Skills', '').strip(),
                            advanced_concepts=row.get('Advanced Concepts', '').strip(),
                            certifications=row.get('Suggested Certifications & Courses', '').strip()
                        )
                    except Exception as e:
                        # Log this error properly in a real application
                        print(f"Error saving row {row}: {e}") # Keep print for now
                        messages.warning(request, f"Skipping row due to error: {row.get('Role', 'Unknown Role')}. Error: {e}")
            messages.success(request, "Skills dataset loaded successfully!")
        except FileNotFoundError:
            messages.error(request, f"Skills dataset file not found at the configured path: {settings.SKILLS_DATASET_FILENAME}. Please ensure it's in the project's root directory.")
        except Exception as e:
            messages.error(request, f"An error occurred during skills dataset processing: {e}")
    
    # Always render the page, showing current data and any messages
    all_skills_data = SkillsDataset.objects.all()
    # Pass messages to context if not using Django's default message rendering in template for 'msg'
    # For 'msg': messages.get_messages(request) is not standard, usually messages are iterated in template.
    # If 'msg' context var is specifically used:
    # current_messages = list(messages.get_messages(request)) # Consume messages
    # msg_texts = [str(m) for m in current_messages]
    return render(request, 'skillsdataset.html', {'data': all_skills_data}) # Removed {'msg':...} assuming template handles Django messages


def edit_degree(request):
    """Handles editing of a specific education degree entry."""
    """Handles editing of a specific education degree entry."""
    return _handle_edit_operation(request, ResumeEducation, EducationForm,
                                'editdegree.html', 'Education data updated successfully!', 'view_education')

def delete_degree(request):
    """Handles deletion of a specific education degree entry."""
    return _handle_delete_operation(request, ResumeEducation, 
                                  'Education data deleted successfully!', 'view_education')

def edit_experience(request):
    """Handles editing of a specific work experience entry."""
    return _handle_edit_operation(request, WorkExperience, WorkExperienceForm,
                                'editexp.html', 'Experience data updated successfully!', 'view_work_experience')

def delete_experience(request):
    """Handles deletion of a specific work experience entry."""
    return _handle_delete_operation(request, WorkExperience, 
                                  'Experience data deleted successfully!', 'view_work_experience')

def edit_skill(request):
    """Handles editing of a user's skills entry."""
    return _handle_edit_operation(request, ResumeSkill, SkillForm,
                                'editskill.html', 'Skill data updated successfully!', 'view_skills')

def delete_skill(request):
    """Handles deletion of a user's skills entry."""
    return _handle_delete_operation(request, ResumeSkill, 
                                  'Skill data deleted successfully!', 'view_skills')


def analyseskillset(request): # Original name, consider analyze_skill_set
    """Displays an interface for users to select a career and see a skills analysis."""
    # This view likely prepares data for the analysis form.
    # It should probably ensure user is logged in if skills are user-specific.
    # _ensure_user_session(request) # Uncomment if user context is needed for initial data
    all_skills_data = SkillsDataset.objects.all() # Fetches all roles for dropdown
    return render(request, 'analyseskill.html', {'data': all_skills_data})

def analyse_skillset(request): # Original name
    """
    Performs and displays a skill gap analysis for the user against a selected career.
    """
    user_email = _ensure_user_session(request)
    selected_career_role = request.GET.get('career') # Get selected career from query params

    if not selected_career_role:
        messages.error(request, "Please select a career role to analyze.")
        return redirect('analyseskillset') # Redirect back to selection page

    # Get required skills for the selected career
    career_skill_data = SkillsDataset.objects.filter(role=selected_career_role).first() # role field
    if not career_skill_data:
        messages.error(request, f"No data found for career: {selected_career_role}")
        return redirect('analyseskillset')
        
    required_skills_list = [skill.strip().lower() for skill in career_skill_data.skills.split(',') if skill.strip()] # skills field

    # Get user's skills
    user_skills_instance = ResumeSkill.objects.filter(username=user_email).first() # Use ResumeSkill
    current_user_skills_list = []
    if user_skills_instance and user_skills_instance.skills:
        current_user_skills_list = [skill.strip().lower() for skill in user_skills_instance.skills.split(',') if skill.strip()]
    
    # Calculate matched and missing skills
    # Using sets for efficient comparison
    required_skills_set = set(required_skills_list)
    current_user_skills_set = set(current_user_skills_list)
    
    matched_skills_set = current_user_skills_set.intersection(required_skills_set)
    missing_skills_set = required_skills_set - current_user_skills_set
    
    match_percentage = 0
    if required_skills_list: # Avoid division by zero
        match_percentage = (len(matched_skills_set) / len(required_skills_list)) * 100
    
    skill_mismatch_percentage = 100 - match_percentage
    
    # Data for rendering the skill analysis page
    all_career_roles_for_dropdown = SkillsDataset.objects.all() # For the dropdown in the template
    
    context = {
        'green_status': match_percentage, # Percentage of skills matched
        'red_status': skill_mismatch_percentage, # Percentage of skills mismatched/missing
        'data': all_career_roles_for_dropdown, # For repopulating dropdown
        'stz': True, # Flag to indicate analysis results are available
        'req_skills': ", ".join(required_skills_list), # Comma-separated string of required skills
        'user_skills': ", ".join(current_user_skills_list), # Comma-separated string of user's skills
        'unique_skills': ", ".join(missing_skills_set), # Comma-separated string of skills to learn
        'tot_data': career_skill_data # The specific SkillsDataset entry for the chosen role
    }
    return render(request, 'analyseskill.html', context)


def prediction_job(request): # Original name, consider predict_job_roles
    """Suggests best job roles for the user based on their skills match percentage."""
    user_email = _ensure_user_session(request)
    from collections import defaultdict # Moved import to top of function for clarity
    
    user_skills_instance = ResumeSkill.objects.filter(username=user_email).first() # Use ResumeSkill
    current_user_skills_list = []
    if user_skills_instance and user_skills_instance.skills:
        current_user_skills_list = [skill.strip().lower() for skill in user_skills_instance.skills.split(',') if skill.strip()]

    role_match_scores = defaultdict(float)
    all_job_roles_dataset = SkillsDataset.objects.all()

    for role_data_entry in all_job_roles_dataset:
        required_skills_for_role = [skill.strip().lower() for skill in role_data_entry.skills.split(',') if skill.strip()]
        
        if not required_skills_for_role:
            continue # Skip roles with no defined skills

        matched_count = sum(1 for skill in current_user_skills_list if skill in required_skills_for_role)
        match_percentage = round((matched_count / len(required_skills_for_role)) * 100, 2)
        role_match_scores[role_data_entry.role] = match_percentage # role field
    
    # Find the best matching role
    best_role_id = max(role_match_scores, key=role_match_scores.get) if role_match_scores else "N/A"
    
    # Sort scores for display
    sorted_role_scores = dict(sorted(role_match_scores.items(), key=lambda item: item[1], reverse=True))
    
    context = {
        'best': best_role_id,
        'scores': sorted_role_scores
    }
    return render(request, 'prediction_job.html', context)


def analyse_skillset2(request): # Original name, consider analyze_skill_set_detailed or similar
    """
    Performs and displays a skill gap analysis, similar to `analyse_skillset`.
    This seems like a duplicate or variant; its distinct purpose isn't clear from name/content alone.
    Assuming it's another display variant for skill analysis.
    """
    user_email = _ensure_user_session(request)
    selected_career_role = request.GET.get('career')

    if not selected_career_role:
        messages.error(request, "Please select a career role.")
        # The redirect target should be where career selection happens, e.g., 'prediction_job' or 'analyseskillset'
        return redirect('prediction_job') # Or 'analyseskillset'

    career_skill_data = SkillsDataset.objects.filter(role=selected_career_role).first() # role field
    if not career_skill_data:
        messages.error(request, f"No data found for career: {selected_career_role}")
        return redirect('prediction_job')

    required_skills_list = [skill.strip().lower() for skill in career_skill_data.skills.split(',') if skill.strip()] # skills field

    user_skills_instance = ResumeSkill.objects.filter(username=user_email).first() # Use ResumeSkill
    current_user_skills_list = []
    if user_skills_instance and user_skills_instance.skills:
        current_user_skills_list = [skill.strip().lower() for skill in user_skills_instance.skills.split(',') if skill.strip()]

    required_skills_set = set(required_skills_list)
    current_user_skills_set = set(current_user_skills_list)
    
    matched_skills_set = current_user_skills_set.intersection(required_skills_set)
    missing_skills_set = required_skills_set - current_user_skills_set
    
    match_percentage = 0
    if required_skills_list:
        match_percentage = (len(matched_skills_set) / len(required_skills_list)) * 100
    
    skill_mismatch_percentage = 100 - match_percentage
    
    all_career_roles_for_dropdown = SkillsDataset.objects.all()
    
    context = {
        'green_status': match_percentage,
        'red_status': skill_mismatch_percentage,
        'data': all_career_roles_for_dropdown, # For a potential dropdown in the template
        'stz': True, # Flag for template rendering
        'req_skills': ", ".join(required_skills_list),
        'user_skills': ", ".join(current_user_skills_list),
        'tot_data': career_skill_data, # The specific SkillsDataset object
        'unique_skills': ", ".join(missing_skills_set) # Skills to learn
    }
    return render(request, 'analyseskill2.html', context)


def classification(request):
    """Renders the classification algorithm training page (likely for admin/testing)."""
    # This view seems to be a gateway to trigger different ML model trainings.
    # No specific data loading, just renders a template with options.
    return render(request, 'classification.html')

def _train_and_save_performance(algorithm_instance, algorithm_name_str):
    """Helper function to train a model and save its performance."""
    from .Classification import Classification # Local import to avoid circular dependency if Classification uses models
    
    model_trainer = Classification(algorithm_instance)
    scores = model_trainer.train() # train() should return a list/tuple of scores [sc1, sc2, sc3, sc4]
    
    # Delete old performance data for this algorithm
    Performance.objects.filter(alg_name=algorithm_name_str).delete() # Use Performance model
    
    # Create new performance record
    Performance.objects.create( # Use Performance model
        alg_name=algorithm_name_str, 
        sc1=scores[0], 
        sc2=scores[1], 
        sc3=scores[2], 
        sc4=scores[3]
    )
    return f"{algorithm_name_str} classification completed and performance saved."

def train_naive_bayes(request):
    """Trains the Naive Bayes classifier and records its performance."""
    message_to_render = _train_and_save_performance(BernoulliNB(), 'Naive Bayes')
    return render(request, 'classification.html', {'msg': message_to_render})

def train_random_forest(request):
    """Trains the Random Forest classifier and records its performance."""
    message_to_render = _train_and_save_performance(RandomForestClassifier(), 'Random Forest')
    return render(request, 'classification.html', {'msg': message_to_render})

def train_svm(request):
    """Trains the SVM classifier and records its performance."""
    message_to_render = _train_and_save_performance(LinearSVC(), 'SVM')
    return render(request, 'classification.html', {'msg': message_to_render})

def train_neural_network(request):
    """Trains the Neural Network (MLP) classifier and records its performance."""
    message_to_render = _train_and_save_performance(MLPClassifier(), 'Neural Networks')
    return render(request, 'classification.html', {'msg': message_to_render})
    

def view_results(request):
    """Displays performance results and graphs for trained ML models."""
    from .Graphs import viewg # Local import for utility function
    
    performance_data = Performance.objects.all() # Use Performance model
    
    # Data for graphs
    accuracy_values = {p.alg_name: p.sc1 for p in performance_data}
    precision_values = {p.alg_name: p.sc2 for p in performance_data}
    recall_values = {p.alg_name: p.sc3 for p in performance_data}
    f1_score_values = {p.alg_name: p.sc4 for p in performance_data}
    
    # Attempt to generate graphs. Errors are caught silently (pass).
    try: viewg(accuracy_values, 'accuracy.png', 'Accuracy')
    except Exception as e: print(f"Error generating accuracy graph: {e}") 
    try: viewg(precision_values, 'precision.png', 'Precision')
    except Exception as e: print(f"Error generating precision graph: {e}")
    try: viewg(recall_values, 'recall.png', 'Recall')
    except Exception as e: print(f"Error generating recall graph: {e}")
    try: viewg(f1_score_values, 'f1.png', 'F1 Score')
    except Exception as e: print(f"Error generating F1 score graph: {e}")

    return render(request, 'viewacc.html', {'data': performance_data})


def upload_job_dataset(request):
    """
    Loads job data from a predefined CSV file into the JobDataset model.
    The CSV filename is configured in settings.py (JOB_DATASET_FILENAME).
    The file is expected to be in the BASE_DIR of the project.
    This view no longer accepts a file path via POST.
    """
    # Assumed admin/staff view.
    if request.method == 'POST': # A POST request could trigger the load operation.
        file_path = os.path.join(settings.BASE_DIR, settings.JOB_DATASET_FILENAME)
        
        try:
            # Consider if clearing the dataset is always desired on each "upload".
            # JobDataset.objects.all().delete() # Optional: clear existing dataset.
            
            with open(file_path, mode='r', encoding="utf-8-sig") as csvfile:
                reader = csv.DictReader(csvfile)
                for row_data in reader:
                    try:
                        JobDataset.objects.update_or_create(
                            job_id=row_data.get("Job_ID", "").strip(), # Use .get() for safety
                            defaults={
                                "skills": row_data.get("Skills", "").strip(),
                                "years_of_experience": int(row_data.get("Years_of_Experience", 0)),
                                "predicted_job_title": row_data.get("Predicted_Job_Title", "").strip(),
                                "company_name": row_data.get("Company_Name", "").strip(),
                                "company_location": row_data.get("Company_Location", "").strip(),
                                "industry": row_data.get("Industry", "").strip(),
                                "salary_usd": int(row_data.get("Salary (USD)", 0)),
                                "education_level": row_data.get("Education_Level", "").strip(),
                            }
                        )
                    except ValueError as ve: # Catch errors converting to int
                        messages.warning(request, f"Skipping row for Job ID {row_data.get('Job_ID', 'Unknown')} due to data conversion error: {ve}")
                    except Exception as e:
                        messages.warning(request, f"Skipping row for Job ID {row_data.get('Job_ID', 'Unknown')} due to error: {e}")
            messages.success(request, "Job dataset loaded successfully.")
        except FileNotFoundError:
            messages.error(request, f"Job dataset file not found at the configured path: {settings.JOB_DATASET_FILENAME}. Please ensure it's in the project's root directory.")
        except Exception as e:
            messages.error(request, f"An error occurred during job dataset processing: {e}")
        
    # Always render the page, showing current data and any messages
    all_job_data = JobDataset.objects.all()
    return render(request, 'dataset.html', {'data': all_job_data}) # Removed {'msg':...}
    

def prediction(request): # Original name, consider predict_job_for_user
    """Predicts suitable jobs for a user based on their profile (education, skills, experience)."""
    user_email = _ensure_user_session(request) # Usually needed if prediction is personalized
    
    if request.method == 'POST':
        # Get user inputs from form
        experience_input = request.POST['exp']
        education_input = request.POST['edu']
        skills_input = request.POST['skills']
        
        from .Classification import Classification # Local import
        
        try:
            # Initialize the classifier (RandomForestClassifier is used here)
            # The model should be pre-trained ideally, not trained on each request.
            # TODO: Load a pre-trained model instead of training here.
            classification_model = Classification(RandomForestClassifier())
            classification_model.train() # This is likely time-consuming and inefficient here.
            
            predicted_job_id = classification_model.predict(skills_input, experience_input, education_input)
            
            # Fetch job details for the predicted job ID
            predicted_jobs = JobDataset.objects.filter(job_id=predicted_job_id) # Use JobDataset model

            # Fetch relevant/similar jobs (e.g., same title)
            relevant_jobs = []
            if predicted_jobs.exists():
                first_predicted_job = predicted_jobs.first()
                relevant_jobs = JobDataset.objects.filter(predicted_job_title=first_predicted_job.predicted_job_title).exclude(job_id=first_predicted_job.job_id)[:9] # Use JobDataset
            else:
                messages.info(request, "No specific job found for the prediction, but showing similar ones if available.")

            context = {'data': predicted_jobs, 'relevant': relevant_jobs}
            return render(request, 'predictionres.html', context)
            
        except Exception as e:
            # Log the exception e
            print(f"Error during prediction: {e}")
            messages.error(request, "An error occurred during job prediction. Details might be mismatched or the prediction model is unavailable.")
            return render(request, 'user_home.html', {'message': messages.get_messages(request)}) # Re-render user_home with error

    else: # GET request: Populate form with user's current data
        # education_str, skills_str, experience_str = '', '', '' # Renamed for clarity
        
        # Fetch user's education details
        education_records = ResumeEducation.objects.filter(username=user_email) # Use ResumeEducation
        education_degrees_list = [record.degree.replace('.', '') for record in education_records]
        education_str = ', '.join(education_degrees_list)

        # Fetch user's skills
        skills_instance = ResumeSkill.objects.filter(username=user_email).first() # Use ResumeSkill
        skills_str = skills_instance.skills if skills_instance else ''

        # Fetch user's experience summary (this might need parsing to get years)
        # The original code extracts digits, which might not be robust.
        experience_instance = ResumeExperience.objects.filter(username=user_email).first() # Use ResumeExperience
        experience_str = ''
        if experience_instance and experience_instance.experience:
            # Simple digit extraction; consider more robust parsing for "X years"
            experience_str = ''.join(char for char in experience_instance.experience if char.isdigit())

        context = {
            'skills': skills_str, 
            "education": education_str, 
            "experience": experience_str
        }
        return render(request, 'prediction.html', context)    
    

