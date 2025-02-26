from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from . models import *

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