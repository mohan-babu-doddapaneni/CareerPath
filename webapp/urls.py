from django.urls import path
from .views import *

urlpatterns = [
    path("", home, name="home"),
    path("register/", register, name="register"),
    path("login/", login_user, name="login"),
    path("dashboard/", dashboard, name="dashboard"),
    path('userhome/', userhomedef, name="userhomedef"),
    path('userlogout/', userlogoutdef, name="userlogoutdef"),
]
