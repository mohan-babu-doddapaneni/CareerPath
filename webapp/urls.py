from django.urls import path
from .views import *

urlpatterns = [
    path("", home, name="home"),
    path("register/", register, name="register"),
    path("login/", login_user, name="login"),
    path("dashboard/", dashboard, name="dashboard"),
    path('userhome/', userhomedef, name="userhomedef"),
    path('userlogout/', userlogoutdef, name="userlogoutdef"),
    path('addeducation/', addeducation, name="addeducation"),
    path('addworkexperience/', addworkexperience, name="addworkexperience"),
    path('addskills/', addskills, name="addskills"),

    path('profile/', profile, name="profile"),
    
    path('vieweducation/', vieweducation, name="vieweducation"),
    path('viewworkexperience/', viewworkexperience, name="viewworkexperience"),
    path('viewskills/', viewskills, name="viewskills"),
]
