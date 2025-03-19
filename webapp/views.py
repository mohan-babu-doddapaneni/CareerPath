from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from .models import *
from .GetHash import get_hash

def home(request):
    return render(request, "index.html")

def register(request):
    if request.method == "POST":
        name = request.POST["name"]
        contact = request.POST["contact"]
        email = request.POST["email"]
        password = request.POST["password"]
        hashed_password = get_hash(password)  # Hash the password

        user = Users.objects.create(name=name, contact=contact, username=email, email=email, password=hashed_password)
        
        messages.success(request, "Account created successfully!")
        
        return redirect("login")

    return render(request, "register.html")


def login_user(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        print(make_password(password))

        user = Users.objects.filter(username=email).filter(password=get_hash(password)).first()  # Get user by email
        if user:  # Check hashed password

            request.session['email']=email
            
            messages.success(request, "Logged in successfully!")
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid email or password!")

    return render(request, "login.html")
    
def dashboard(request):
    return render(request, "user_home.html")

def profile(request):
    if "email" in request.session:
        return render(request, "profile.html")
    else:
        return redirect('userlogoutdef')
    
def userlogoutdef(request):
    try:
        del request.session['email']
    except:
        pass
    return render(request, 'login.html')

def userhomedef(request):
    if "email" in request.session:
        email=request.session["email"]
        d=Users.objects.filter(username__exact=email)
        return render(request, 'user_home.html',{'data': d[0]})
    else:
        return redirect('userlogoutdef')

def addeducation(request):
    if request.method=='POST':
        email=request.session["email"]
        degree=request.POST['degree']
        institution=request.POST['institution']
        start_year=request.POST['start_year']
        end_year=request.POST['end_year']
        score=request.POST['score']
        d=Education(username=email, degree=degree, institution=institution, start_year=start_year, end_year=end_year, score=score)
        d.save()
        return render(request, 'addeducation.html',{'msg': 'Education data added !!'})
    else:
        return render(request, 'addeducation.html'  )


def addworkexperience(request):
    if request.method=='POST':
        email=request.session["email"]
        company=request.POST['company']
        job_title=request.POST['job_title']
        experience=request.POST['experience']
        start_date=request.POST['start_date']
        end_date=request.POST['end_date']
        d=WorkExperience(username=email, job_title=job_title, company=company, start_date=start_date, end_date=end_date, experience=experience)
        d.save()
        return render(request, 'addworkexperience.html',{'msg': 'Work experience data added !!'})
    else:
        return render(request, 'addworkexperience.html'  )


def addskills(request):
    if request.method=='POST':
        email=request.session["email"]
        skills=request.POST['skills']
        d=Skills(username=email, skills=skills)
        d.save()
        return render(request, 'addskills.html',{'msg': 'Skills data added !!'})
    else:
        return render(request, 'addskills.html'  )

def vieweducation(request):
    if "email" in request.session:
        email=request.session["email"]
        d=Education.objects.filter(username__exact=email)
        return render(request, 'profile.html',{'educations': d, 'st1':True})
    else:
        return redirect('userlogoutdef')

def viewworkexperience(request):
    if "email" in request.session:
        email=request.session["email"]
        d=WorkExperience.objects.filter(username__exact=email)
        return render(request, 'profile.html',{'experiences': d, 'st2':True})
    else:
        return redirect('userlogoutdef')

def viewskills(request):
    if "email" in request.session:
        email=request.session["email"]
        d=Skills.objects.filter(username__exact=email)
        return render(request, 'profile.html',{'skills': d, 'st3':True})
    else:
        return redirect('userlogoutdef')
