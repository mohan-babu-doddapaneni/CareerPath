


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
    path('upload_resume/', upload_resume, name='upload_resume'),
    path('deleteresume/', deleteresume, name='deleteresume'),
    path('update_resume_data/', update_resume_data, name="update_resume_data"),
    
    path('adminlogout/', adminlogout, name="userlogoutdef"),
    path('adminlogin/', adminlogin, name="adminlogin"),
    path('adminloginaction/', adminloginaction, name="adminloginaction"),
    path('admindashboard/', admindashboard, name="admindashboard"),
    path('skillsdataset/', skillsdataset, name="skillsdataset"),
    path('editdegree/', editdegree, name="editdegree"),
    path('deletedegree/', deletedegree, name="deletedegree"),
    
    
    path('editexp/', editexp, name="editexp"),
    path('deleteexp/', deleteexp, name="deleteexp"),
    
    path('editdegree/', editdegree, name="editdegree"),
    path('deletedegree/', deletedegree, name="deletedegree"),
    
    
    path('editskill/', editskill, name="editskill"),
    path('deleteskill/', deleteskill, name="deleteskill"),
    
    
    
    
    path('analyseskillset/', analyseskillset, name="analyseskillset"),
    path('analyse_skillset/', analyse_skillset, name='analyse_skillset'),
    path('prediction_job/', prediction_job, name='prediction_job'),
    path('analyse_skillset2/', analyse_skillset2, name='analyse_skillset2'),


    path('classification/', classification, name="classification"),
    path('rftrain/', rftrain, name="rftrain"),
    path('nntrain/', nntrain, name="nntrain"),
    path('nbtrain/', nbtrain, name="nbtrain"),
    path('svmtrain/', svmtrain, name="svmtrain"),
    path('viewresults/', viewresults, name="viewresults"),
    
    path('upload/', upload, name="upload"),
    path('prediction/', prediction, name="jobprediction"),

  

]


from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)