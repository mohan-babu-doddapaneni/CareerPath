


from django.urls import path
from .views import *

urlpatterns = [
    path("", home, name="home"),
    path("register/", register, name="register"),
    path("login/", login_user, name="login"),
    path("dashboard/", dashboard, name="dashboard"),
    path('userhome/', user_home, name="userhomedef"),  # Renamed from userhomedef
    path('userlogout/', user_logout, name="userlogoutdef"), # Renamed from userlogoutdef
    path('addeducation/', add_education, name="addeducation"), # Renamed from addeducation
    path('addworkexperience/', add_work_experience, name="addworkexperience"), # Renamed from addworkexperience
    path('addskills/', add_skills, name="addskills"), # Renamed from addskills

    path('profile/', profile, name="profile"),
    
    path('vieweducation/', view_education, name="vieweducation"), # Renamed from vieweducation
    path('viewworkexperience/', view_work_experience, name="viewworkexperience"), # Renamed from viewworkexperience
    path('viewskills/', view_skills, name="viewskills"), # Renamed from viewskills
    path('upload_resume/', upload_resume, name='upload_resume'),
    path('deleteresume/', delete_resume, name='deleteresume'), # Renamed from deleteresume
    path('update_resume_data/', update_resume_data, name="update_resume_data"),
    
    path('skillsdataset/', upload_skills_dataset, name="skillsdataset"), # Renamed from skillsdataset
    path('editdegree/', edit_degree, name="editdegree"), # Renamed from editdegree
    path('deletedegree/', delete_degree, name="deletedegree"), # Renamed from deletedegree
    
    
    path('editexp/', edit_experience, name="editexp"), # Renamed from editexp
    path('deleteexp/', delete_experience, name="deleteexp"), # Renamed from deleteexp
    
    # Duplicate entries for editdegree and deletedegree, pointing to new names
    path('editdegree/', edit_degree, name="editdegree_duplicate"), 
    path('deletedegree/', delete_degree, name="deletedegree_duplicate"),
    
    
    path('editskill/', edit_skill, name="editskill"), # Renamed from editskill
    path('deleteskill/', delete_skill, name="deleteskill"), # Renamed from deleteskill
    
    
    
    
    path('analyseskillset/', analyseskillset, name="analyseskillset"), # Kept as is
    path('analyse_skillset/', analyse_skillset, name='analyse_skillset'), # Kept as is
    path('prediction_job/', prediction_job, name='prediction_job'), # Kept as is
    path('analyse_skillset2/', analyse_skillset2, name='analyse_skillset2'), # Kept as is


    path('classification/', classification, name="classification"), # Kept as is
    path('rftrain/', train_random_forest, name="rftrain"), # Renamed from rftrain
    path('nntrain/', train_neural_network, name="nntrain"), # Renamed from nntrain
    path('nbtrain/', train_naive_bayes, name="nbtrain"), # Renamed from nbtrain
    path('svmtrain/', train_svm, name="svmtrain"), # Renamed from svmtrain
    path('viewresults/', view_results, name="viewresults"), # Renamed from viewresults
    
    path('upload/', upload_job_dataset, name="upload"), # Renamed from upload
    path('prediction/', prediction, name="jobprediction"), # Kept as is

  

]


from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)