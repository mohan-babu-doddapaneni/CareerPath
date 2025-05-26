from django.test import TestCase, Client
from django.urls import reverse
from .models import Users, ResumeEducation, WorkExperience, ResumeSkill # Consolidated model imports
from .forms import EducationForm, WorkExperienceForm, SkillForm # New form imports
from django.contrib.auth.hashers import check_password, make_password

class UserModelTests(TestCase):
    def test_user_creation(self):
        """Test that a Users object can be created and password is hashed."""
        raw_password = "testpassword123"
        hashed_password = make_password(raw_password) # Use the same hashing as in views
        user = Users.objects.create(
            username="testuser@example.com",
            name="Test User",
            contact="1234567890",
            email="testuser@example.com",
            password=hashed_password  # Store the pre-hashed password
        )
        retrieved_user = Users.objects.get(username="testuser@example.com")
        self.assertEqual(retrieved_user.name, "Test User")
        self.assertTrue(check_password(raw_password, retrieved_user.password))

class UserRegistrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')

    def test_registration_page_loads(self):
        """Test that the registration page loads correctly."""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')

    def test_user_registration_success(self):
        """Test successful user registration."""
        user_data = {
            'name': 'New User',
            'contact': '0987654321',
            'email': 'newuser@example.com',
            'password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }
        response = self.client.post(self.register_url, user_data)
        
        # Expect a redirect to login page upon successful registration
        self.assertRedirects(response, reverse('login')) 
        self.assertTrue(Users.objects.filter(username='newuser@example.com').exists())
        user = Users.objects.get(username='newuser@example.com')
        self.assertTrue(check_password('newpassword123', user.password))

    def test_user_registration_password_mismatch(self):
        """Test registration failure when passwords do not match."""
        user_data = {
            'name': 'Mismatch User',
            'contact': '1122334455',
            'email': 'mismatch@example.com',
            'password': 'password1',
            'confirm_password': 'password2'
        }
        response = self.client.post(self.register_url, user_data)
        self.assertEqual(response.status_code, 200) # Should re-render the form
        self.assertFalse(Users.objects.filter(username='mismatch@example.com').exists())
        # Check for error message if possible (might require template parsing or specific context variable)
        # For now, checking no user created is the primary test

class UserLoginTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        self.raw_password = 'testpassword123'
        # Use make_password from Django's auth system as used in the view
        self.hashed_password = make_password(self.raw_password)
        self.user = Users.objects.create(
            username='testlogin@example.com',
            name='Login Test User',
            email='testlogin@example.com',
            password=self.hashed_password
        )

    def test_login_page_loads(self):
        """Test that the login page loads correctly."""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_user_login_success(self):
        """Test successful user login and session creation."""
        login_data = {
            'email': 'testlogin@example.com',
            'password': self.raw_password 
        }
        response = self.client.post(self.login_url, login_data)
        self.assertRedirects(response, reverse('dashboard')) # Check for redirect to dashboard
        self.assertEqual(self.client.session.get('email'), 'testlogin@example.com')

    def test_user_login_failure_wrong_password(self):
        """Test login failure with an incorrect password."""
        login_data = {
            'email': 'testlogin@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, 200) # Should re-render form
        self.assertIsNone(self.client.session.get('email'))

    def test_user_login_failure_nonexistent_user(self):
        """Test login failure for a user that does not exist."""
        login_data = {
            'email': 'nouser@example.com',
            'password': 'anypassword'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, 200) # Should re-render form
        self.assertIsNone(self.client.session.get('email'))

# Appended CRUD Test Code Starts Here

class BaseUserLoggedInTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        self.raw_password = 'testpassword123'
        self.user_email = 'testcruduser@example.com'
        self.hashed_password = make_password(self.raw_password)
        self.user = Users.objects.create(
            username=self.user_email,
            name='CRUD Test User',
            email=self.user_email,
            password=self.hashed_password
        )
        
        # Log the user in
        login_data = {'email': self.user_email, 'password': self.raw_password}
        self.client.post(self.login_url, login_data)
        # Verify session
        self.assertEqual(self.client.session.get('email'), self.user_email)

class EducationCRUDTests(BaseUserLoggedInTestCase):
    def test_add_education_page_loads(self):
        """Test that the add education page loads for a logged-in user."""
        response = self.client.get(reverse('add_education'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'addeducation.html')
        self.assertIsInstance(response.context['form'], EducationForm)

    def test_add_education_success(self):
        """Test successful addition of education data."""
        education_data = {'degree': 'B.Sc. Computer Science'}
        response = self.client.post(reverse('add_education'), education_data)
        
        # Expect redirect to the same page or a success page (current view renders same template)
        self.assertEqual(response.status_code, 200) # View renders same template with a message
        self.assertTrue(ResumeEducation.objects.filter(username=self.user_email, degree='B.Sc. Computer Science').exists())
        # Check for success message in context if possible, or in response content
        self.assertContains(response, "Education data added successfully!") # Updated message from views


    def test_view_education_loads(self):
        """Test that the view education page (profile with education) loads."""
        # Add some education data first
        ResumeEducation.objects.create(username=self.user_email, degree="M.Sc. Data Science")
        
        response = self.client.get(reverse('view_education'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        self.assertTrue(response.context.get('st1')) # Checks if the education section flag is true
        self.assertQuerysetEqual(
            response.context['educations'],
            ResumeEducation.objects.filter(username=self.user_email),
            transform=lambda x: x,
            ordered=False # Add ordered=False if order is not guaranteed/important
        )

class WorkExperienceCRUDTests(BaseUserLoggedInTestCase):
    def test_add_work_experience_page_loads(self):
        response = self.client.get(reverse('add_work_experience'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'addworkexperience.html')
        self.assertIsInstance(response.context['form'], WorkExperienceForm)

    def test_add_work_experience_success(self):
        experience_data = {
            'job_title': 'Software Engineer',
            'company': 'Tech Solutions Inc.',
            'start_date': '2020-01-15',
            'end_date': '2022-12-31',
            'experience': 'Developed web applications.'
        }
        response = self.client.post(reverse('add_work_experience'), experience_data)
        self.assertEqual(response.status_code, 200) # View renders same template
        self.assertTrue(WorkExperience.objects.filter(
            username=self.user_email, 
            job_title='Software Engineer'
        ).exists())
        self.assertContains(response, "Work experience data added successfully!") # Updated message

    def test_view_work_experience_loads(self):
        WorkExperience.objects.create(
            username=self.user_email, 
            job_title='Developer', 
            company='MyCo', 
            start_date='2019-01-01', 
            experience='Stuff'
        )
        response = self.client.get(reverse('view_work_experience'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        self.assertTrue(response.context.get('st2'))
        # Comparing querysets for WorkExperience can be complex if Resume_experience is also involved
        # For now, check if the 'experiences' key is in context and has items
        self.assertTrue('experiences' in response.context)
        self.assertTrue(len(response.context['experiences']) > 0)


class SkillsCRUDTests(BaseUserLoggedInTestCase):
    def test_add_skills_page_loads(self):
        response = self.client.get(reverse('add_skills'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'addskills.html')
        self.assertIsInstance(response.context['form'], SkillForm)

    def test_add_skills_success(self):
        skills_data = {'skills': 'Python, Django, JavaScript'}
        response = self.client.post(reverse('add_skills'), skills_data)
        self.assertEqual(response.status_code, 200) # View renders same template
        self.assertTrue(ResumeSkill.objects.filter(
            username=self.user_email, 
            skills='Python, Django, JavaScript'
        ).exists())
        self.assertContains(response, "Skills data added successfully!") # Updated message

    def test_view_skills_loads(self):
        ResumeSkill.objects.create(username=self.user_email, skills="Java, Spring")
        response = self.client.get(reverse('view_skills'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        self.assertTrue(response.context.get('st3'))
        self.assertQuerysetEqual(
            response.context['skills'],
            ResumeSkill.objects.filter(username=self.user_email),
            transform=lambda x: x,
            ordered=False # Add ordered=False if order is not guaranteed/important
        )
