from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from . models import *
import csv
from .GetHash import get_hash

from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
#from sklearn.linear_model import  LogisticRegression
from sklearn.naive_bayes import BernoulliNB
from sklearn.svm import LinearSVC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


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
        
        messages.error(request, "Account created successfully!")
        
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



# def dashboard(request):
#     return render(request, "user_home.html")
def dashboard(request):
    if "email" in request.session:
        email = request.session["email"]
        user = Users.objects.filter(username=email).first()
        return render(request, "user_home.html", {'user': user})
    else:
        return redirect('userlogoutdef')



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

        d=Resume_education.objects.filter(username__exact=email)
        return render(request, 'profile.html',{'educations': d, 'st1':True})

    else:
        return redirect('userlogoutdef')

def viewworkexperience(request):
    if "email" in request.session:
        email=request.session["email"]
        d=WorkExperience.objects.filter(username__exact=email)
        d2=Resume_experience.objects.filter(username=email)
        data = d2[0] if d2 else None

        return render(request, 'profile.html', {
            'experiences': d,
            'data': data,
            'st2': True
        })
    else:
        return redirect('userlogoutdef')

def viewskills(request):
    if "email" in request.session:
        email=request.session["email"]
        d=Resume_skills.objects.filter(username__exact=email)
        return render(request, 'profile.html',{'skills': d, 'st3':True})

    else:
        return redirect('userlogoutdef')



from .models import Resumes
from .forms import ResumeUploadForm
def upload_resume(request):
    
    if request.method == "POST":
        email=request.session["email"]
        messages.error(request, "")
        print(request.method, '88888888888')
        form = ResumeUploadForm(request.POST, request.FILES)
        uploaded_file = request.FILES.get("file")

        print(uploaded_file, '<<<<<<<<<<')

        if uploaded_file:
            if not uploaded_file.name.endswith(".docx"):
                messages.error(request, "Only .docx files are allowed!")
                return redirect("resume_upload")
        print(form.is_valid(), 'Form is vlaid')
        if form.is_valid():
            username = form.cleaned_data["username"]
            # Check if the username already exists\
            print(Resumes.objects.filter(username=username).exists(), '<<<<<<<<<<<<<<<')
            if Resumes.objects.filter(username=username).exists():
                messages.error(request, "Username already exists! Choose a different username.")
                
                return redirect("upload_resume")


            from . resume_parser import parse_resume
            basic_data=parse_resume(uploaded_file)
            print(basic_data)

            skills=basic_data['Skills']
            skills_txt=", ".join(skills)
            d=Resume_skills(username=email, skills=skills_txt)
            d.save()

            education=basic_data['Education']

            for s in education:
                d=Resume_education(username=email, degree=s)
                d.save()
            
            from . parse_exp import parse_resume
            resume_data=parse_resume(uploaded_file)
            
            exp=resume_data['Total Experience']
            d=Resume_experience(username=email, experience=exp)
            d.save()

            education=Resume_education.objects.filter(username=email)

            

                   


            
            form.save()
            return render(request, "upload_resume_edit.html", {"exp": exp, 'skills_txt':skills_txt, 'education':education})
            
        else:
            print('$$$$$$$$$$$$$$$$$')
            if Resumes.objects.filter(username=request.session["email"]).exists():
                messages.success(request, "Resume already uploaded !")

    else:
        
        form = ResumeUploadForm()

    resumes = Resumes.objects.filter(username=request.session["email"])
    return render(request, "upload_resume.html", {"form": form, "resumes": resumes})

def deleteresume(request):
    if "email" in request.session:
        email=request.session["email"]
        d=Resumes.objects.filter(username__exact=email)
        d.delete()
        d=Resume_education.objects.filter(username__exact=email)
        d.delete()
        d=Resume_experience.objects.filter(username__exact=email)
        d.delete()
        d=Resume_skills.objects.filter(username__exact=email)
        d.delete()
        messages.error(request, "Resume Deleted successfully!")
        return redirect("upload_resume")

    else:
        return redirect('userlogoutdef')



def update_resume_data(request):
    if request.method == "POST":
        email=request.session["email"]
        skills = request.POST.get('skills')
        exp = request.POST.get('exp')

        ids = request.POST.getlist('record_id')  
        contents = request.POST.getlist('content')

        print(zip(ids, contents), '<<<<<<<<<<<<<<<<<<<')

        for record_id, content in zip(ids, contents):
            print(record_id, content)
            record = Resume_education.objects.get(id=record_id)
            record.degree = content
            record.save()
        
        record=Resume_skills.objects.get(username=email)
        record.skills=skills
        record.save()
        
        record=Resume_experience.objects.get(username=email)
        record.experience=exp
        record.save()

        messages.error(request, "Resume Uploaded successfully!")
        return redirect("upload_resume")

        

        

    return redirect('/')    



def adminlogin(request):
    return render(request, 'admin.html')


def adminloginaction(request):
    userid=request.POST['aid']
    pwd=request.POST['pwd']
    print(userid, pwd,'<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
    if userid=='admin' and pwd=="admin":
        request.session['adminid']='admin'
        #messages.success(request, "Logged in successfully!")
        return redirect("admindashboard")
    else:
        messages.error(request, "Login data is invalid !")
        return redirect("adminlogin")

def admindashboard(request):
    return render(request, 'adminhome.html')


def adminlogout(request):
    return render(request, 'admin.html')


def skillsdataset(request):
    if request.method=='POST':
        file_path='SkillsDataset.csv'
        
        SkillsDataset.objects.all().delete()
        
        with open(file_path, encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile)
            print(reader)
            
            for row in reader:
                print(row)
                try:
                    SkillsDataset.objects.create(
                        #Role,Skills,Soft Skills,Advanced Concepts,Suggested Certifications & Courses
                        Role=row['Role'],
                        Skills=row['Skills'],
                        SoftSkills=row['Soft Skills'],
                        AdvancedConcepts=row['Advanced Concepts'],
                        Certifications=row['Suggested Certifications & Courses']
                        
                    )
                    
                except Exception as e:
                    print(f"Error saving {row}: {e}")
        d=SkillsDataset.objects.all()
        return render(request, 'skillsdataset.html', {'msg':'Skills dataset uploaded successfully !!', 'data':d})
    else:
        d=SkillsDataset.objects.all()
        return render(request, 'skillsdataset.html',{'data':d} )




def editdegree(request):
    if request.method=='POST':
        id=request.POST['id']
        degree=request.POST['degree']
        d=Resume_education.objects.filter(id=id).update(degree=degree)
        messages.success(request, "Education data updated !!")
        return redirect(vieweducation)

    else:
        email=request.session["email"]
        id=request.GET['id']
        
        d=Resume_education.objects.filter(username=email, id=id)
        return render(request, 'editdegree.html',{'data': d[0]} )



def deletedegree(request):
    if request.method=='POST':
        id=request.POST['id']
        d=Resume_education.objects.filter(id=id).delete()
        messages.success(request, "Education data deleted !!")
        return redirect(vieweducation)

    else:
        pass




def editexp(request):
    if request.method=='POST':
        print(request.POST)
        id=request.POST['id']
        company=request.POST['company']
        job_title=request.POST['job_title']
        exp=request.POST['exp']
        start_date=request.POST['start_date']
        end_date=request.POST['end_date']
        
        d=WorkExperience.objects.filter(id=id).update(job_title=job_title, company=company, start_date=start_date, end_date=end_date, experience=exp)
        
        messages.success(request, "Experience data updated !!")
        return redirect(viewworkexperience)

    else:
        email=request.session["email"]
        id=request.GET['id']
        
        d=WorkExperience.objects.filter(username=email, id=id)
        return render(request, 'editexp.html',{'data': d[0]} )



def deleteexp(request):
    if request.method=='POST':
        id=request.POST['id']
        d=WorkExperience.objects.filter(id=id).delete()
        messages.success(request, "Experience data deleted !!")
        return redirect(viewworkexperience)

    else:
        pass



def editskill(request):
    if request.method=='POST':
        print(request.POST)
        id=request.POST['id']
        skill=request.POST['skill']
        
        d=Resume_skills.objects.filter(id=id).update(skills=skill)
        
        messages.success(request, "Skill data updated !!")
        return redirect(viewskills)

    else:
        email=request.session["email"]
        id=request.GET['id']
        
        d=Resume_skills.objects.filter(username=email, id=id)
        return render(request, 'editskill.html',{'data': d[0]} )



def deleteskill(request):
    if request.method=='POST':
        id=request.POST['id']
        #d=Resume_experience.objects.filter(id=id).delete()
        messages.success(request, "Skill data deleted !!")
        return redirect(viewskills)

    else:
        pass


def analyseskillset(request):
    d=SkillsDataset.objects.filter()
    return render(request, 'analyseskill.html',{'data': d} )

def analyse_skillset(request):
    career=request.GET['career']
    email=request.session["email"]
    
    temp1=SkillsDataset.objects.filter(Role=career).first()
    req_skills=[]
    for r in temp1.Skills.split(','):
        req_skills.append(r)
    
    temp2=Resume_skills.objects.filter(username=email)
    user_skills=[]

    for r in temp2:
        row=r.skills
        for r2 in row.split(','):
            user_skills.append(r2)
    
    print(req_skills, user_skills)

    unique_skills = list(set(req_skills) - set(user_skills))

    list1 = [word.lower() for word in req_skills]
    list2 = [word.lower() for word in user_skills]



    matches = sum(1 for word in list1 if word in list2)
    percentage = (matches / len(list1)) * 100 if list1 else 0
    d=SkillsDataset.objects.filter()
    red_status=100-percentage

    d2=SkillsDataset.objects.filter(Role=career)
    

    return render(request, 'analyseskill.html',{'green_status': percentage,'red_status': red_status, 'data': d,'stz':True, 'req_skills':", ".join(req_skills), 'user_skills':", ".join(user_skills),'unique_skills':", ".join(unique_skills), 'tot_data':d2} )



def prediction_job(request):
    
    email=request.session["email"]
    from collections import defaultdict
    
    
    temp2=Resume_skills.objects.filter(username=email)
    user_skills=[]

    for r in temp2:
        row=r.skills
        for r2 in row.split(','):
            user_skills.append(r2)
    
    scores = defaultdict(float)
    
    dataset=SkillsDataset.objects.all()
    for d1 in dataset:
        req_skills=[]
        for r in d1.Skills.split(','):
            req_skills.append(r)
        
    
    
        list1 = [word.lower() for word in req_skills]
        list2 = [word.lower() for word in user_skills]

        matches = sum(1 for word in list1 if word in list2)
        percentage = round((matches / len(list1)) * 100, 2) if list1 else 0
        scores[d1.Role] = percentage
    
    best_id = max(scores, key=scores.get)
    scores=dict(scores)
    scores = dict(sorted(scores.items(), key=lambda item: item[1], reverse=True))

    

    return render(request, 'prediction_job.html',{'best':best_id, 'scores':scores} )



def analyse_skillset2(request):
    career=request.GET['career']
    email=request.session["email"]
    
    temp1=SkillsDataset.objects.filter(Role=career).first()
    req_skills=[]
    for r in temp1.Skills.split(','):
        req_skills.append(r)
    
    temp2=Resume_skills.objects.filter(username=email)
    user_skills=[]

    for r in temp2:
        row=r.skills
        for r2 in row.split(','):
            user_skills.append(r2)
    
    print(req_skills, user_skills)
    unique_skills = list(set(req_skills) - set(user_skills))


    list1 = [word.lower() for word in req_skills]
    list2 = [word.lower() for word in user_skills]

    matches = sum(1 for word in list1 if word in list2)
    percentage = (matches / len(list1)) * 100 if list1 else 0
    d=SkillsDataset.objects.filter()
    red_status=100-percentage

    d2=SkillsDataset.objects.filter(Role=career)
    

    return render(request, 'analyseskill2.html',{'green_status': percentage,'red_status': red_status, 'data': d,'stz':True, 'req_skills':", ".join(req_skills), 'user_skills':", ".join(user_skills), 'tot_data':d2, 'unique_skills':", ".join(unique_skills)} )



def classification(request):
    return render(request, 'classification.html')

def nbtrain(request):
    alg = BernoulliNB()

    from .Classification import Classification
    model = Classification(alg)
    
    
    sc=model.train()
    
    d = performance.objects.filter(alg_name='Naive Bayes')
    d.delete()

    
    d = performance(alg_name='Naive Bayes', sc1=sc[0], sc2=sc[1], sc3=sc[2], sc4=sc[3])
    d.save()
    
    return render(request, 'classification.html', {'msg': "Naive Bayes Classification completed"})


def rftrain(request):
    alg = RandomForestClassifier()

    
    d = performance.objects.filter(alg_name='Random Forest')
    d.delete()
    
    
    from .Classification import Classification
    model = Classification(alg)
    
    sc=model.train()
    
    d = performance(alg_name='Random Forest', sc1=sc[0], sc2=sc[1], sc3=sc[2], sc4=sc[3])
    d.save()
    
    
    return render(request, 'classification.html', {'msg': "Random Forest Classification completed"})
    

def svmtrain(request):
    alg = LinearSVC()


    d = performance.objects.filter(alg_name='SVM')
    d.delete()
    
    
    from .Classification import Classification

    model = Classification(alg)
    
    sc=model.train()
    d = performance(alg_name='SVM', sc1=sc[0], sc2=sc[1], sc3=sc[2], sc4=sc[3])
    d.save()
    
    return render(request, 'classification.html', {'msg': "SVM Classification completed"})


def nntrain(request):
    alg = MLPClassifier()


    d = performance.objects.filter(alg_name='Neural Networks')
    d.delete()
    
    from .Classification import Classification

    model = Classification(alg)
    sc=model.train()
    
    d = performance(alg_name='Neural Networks', sc1=sc[0], sc2=sc[1], sc3=sc[2], sc4=sc[3])
    d.save()
    
    return render(request, 'classification.html', {'msg': "Neural Networks Classification completed"})
    
    
    
    
    

def viewresults(request):
    from .Graphs import viewg
    
    d = performance.objects.all()
    val = dict({})
    for d1 in d:
        val[d1.alg_name] = d1.sc1
        
    try:viewg(val, 'accuracy.png', 'Accuracy')
    except:pass
    
    val = dict({})
    for d1 in d:
        val[d1.alg_name] = d1.sc2
    try:viewg(val, 'precision.png', 'Precision')
    except:pass
    
    val = dict({})
    for d1 in d:
        val[d1.alg_name] = d1.sc3
    try:viewg(val, 'recall.png', 'Recall')
    except:pass

    val = dict({})
    for d1 in d:
        val[d1.alg_name] = d1.sc4
    try:viewg(val, 'f1.png', 'F1 Score')
    except:pass

    return render(request, 'viewacc.html', {'data': d})



    

import csv
def upload(request):
    if  request.method=='POST':

        file_path=request.POST['file']
        
        with open(file_path, encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile)
        
        
            for row in reader:
                dataset.objects.update_or_create(
                    job_id=row["Job_ID"],
                    defaults={
                        "skills": row["Skills"],
                        "years_of_experience": int(row["Years_of_Experience"]),
                        "predicted_job_title": row["Predicted_Job_Title"],
                        "company_name": row["Company_Name"],
                        "company_location": row["Company_Location"],
                        "industry": row["Industry"],
                        "salary_usd": int(row["Salary (USD)"]),
                        "education_level": row["Education_Level"],
                    }
                )


        return render(request, 'dataset.html', {'msg': "Dataset Uploaded Successfully"})
    
    else:
        d=dataset.objects.filter()
        return render(request, 'dataset.html', {'data':d})    
    



    


def prediction(request):
    if request.method == 'POST':
        exp = request.POST['exp']
        edu = request.POST['edu']
        skills = request.POST['skills']

        try:
            user_profile = f"{skills} {edu} {exp}"

            # Fetch all job entries from the database
            jobs = list(dataset.objects.all())

            # Create job documents (text blobs)
            job_documents = [f"{job.skills} {job.education_level} {job.years_of_experience}" for job in jobs]

            # Add user profile at the start
            documents = [user_profile] + job_documents

            # TF-IDF Vectorization
            vectorizer = TfidfVectorizer()
            vectors = vectorizer.fit_transform(documents)

            # Compute cosine similarity between user and all jobs
            cosine_scores = cosine_similarity(vectors[0:1], vectors[1:]).flatten()

            # Top 9 most relevant jobs
            top_indices = cosine_scores.argsort()[-9:][::-1]
            relevant_jobs = [jobs[i] for i in top_indices]

            # Show top 1 as the predicted job + relevant suggestions
            predicted_job = relevant_jobs[0]

        except Exception as e:
            print("Prediction error:", e)
            return render(request, 'user_home.html', {'message': 'Something went wrong. Try again.'})

        return render(request, 'predictionres.html', {'data': [predicted_job], 'relevant': relevant_jobs})
    
    else:
        email=request.session['email']
        education=''; skills='';experience=''
        
        d=Resume_education.objects.filter(username=email)
        temp=[]
        for d1 in d:
            w=d1.degree.replace('.', '')
            temp.append(w)
        education=', '.join(temp)

        try:
            d=Resume_skills.objects.filter(username=email)[0]
            skills=d.skills
        except:pass

        try:
            d=Resume_experience.objects.filter(username=email)[0]
            text=d.experience
            for char in text:
                if char.isdigit():
                    experience += char
        except:pass



        
        return render(request, 'prediction.html', {'skills':skills, "education":education, "experience":experience})    
    

