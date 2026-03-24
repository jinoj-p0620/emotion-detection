from datetime import datetime

from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db.models import Count
import json
# Create your views here.
from myapp.eeg_prediction import predict_eeg_emotion
from myapp.models import *

def logouts(request):
    logout(request)
    return redirect('/myapp/login_get/')

def login_get(request):
    return render(request,'login_index.html')

def login_post(request):
    username=request.POST['username']
    password=request.POST['password']
    user=authenticate(request,username=username,password=password)
    if user is not None:
        if user.groups.filter(name='Admin').exists():
            login(request,user)
            return redirect('/myapp/admin_home/')
        elif user.groups.filter(name='Staff').exists():
            login(request,user)
            return redirect('/myapp/staff_home/')
        else:
            return HttpResponse(
                '''<script>alert('Invalid User');window.location='/myapp/login_get/'</script>''')
    return HttpResponse(
        '''<script>alert('Invalid Username or Password');window.location='/myapp/login_get/'</script>''')

#====================================================ADMIN==============================================================
#====================================================ADMIN==============================================================
#====================================================ADMIN==============================================================
#====================================================ADMIN==============================================================
#====================================================ADMIN==============================================================

@login_required(login_url='/myapp/login_get/')
def admin_home(request):
    staff_count = staff_table.objects.all().count()
    patient_count = patient_table.objects.all().count()
    total_complaints = complaint_table.objects.all().count()
    pending_complaints = complaint_table.objects.filter(reply='pending').count()
    context = {
        'staff_count': staff_count,
        'patient_count': patient_count,
        'total_complaints': total_complaints,
        'pending_complaints': pending_complaints,
    }
    return render(request, 'adminn/admin_index.html', context)

@login_required(login_url='/myapp/login_get/')
def view_staff(request):
    ob=staff_table.objects.all()
    return render(request,'adminn/view_staff.html',{"data":ob})

@login_required(login_url='/myapp/login_get/')
def add_staff(request):
    return render(request,'adminn/add_staff.html')

@login_required(login_url='/myapp/login_get/')
def add_staff_post(request):
    name = request.POST['name']
    email = request.POST['email']
    phone = request.POST['phone']
    qualification = request.POST['qualification']
    place = request.POST['place']
    post = request.POST['post']
    pin = request.POST['pin']
    img = request.FILES['image']
    username = request.POST['uname']
    password = request.POST['password']

    u=User.objects.filter(Q(email=email)|Q(username=username))
    if u.exists():
        return HttpResponse('''<script>alert('Username or Email Already Taken');window.location='/myapp/add_staff/#about'</script>''')
    ab = User.objects.create(username=username,password=make_password(password),email=email,first_name=name)

    ab.groups.add(Group.objects.get(name="Staff"))
    ob = staff_table()
    ob.LOGIN=ab
    ob.name=name
    ob.email=email
    ob.phone=phone
    ob.qualification=qualification
    ob.place=place
    ob.post=post
    ob.pin=pin
    ob.photo=img
    ob.save()
    return redirect('/myapp/view_staff/#about')

@login_required(login_url='/myapp/login_get/')
def edit_staff(request,id):
    request.session['s_id']=id
    obj=staff_table.objects.get(id=id)
    return render(request,'adminn/edit_staff.html',{"val":obj})

@login_required(login_url='/myapp/login_get/')
def edit_staff_post(request):
    name = request.POST['name']
    email = request.POST['email']
    phone = request.POST['phone']
    qualification = request.POST['qualification']
    place = request.POST['place']
    post = request.POST['post']
    pin = request.POST['pin']
    sid=request.session['s_id']

    ob = staff_table.objects.get(id=sid)
    if 'image' in request.FILES:
        img = request.FILES['image']
        ob.photo=img

    ob.name=name
    ob.email=email
    ob.phone=phone
    ob.qualification=qualification
    ob.place=place
    ob.post=post
    ob.pin=pin
    ob.save()
    return redirect('/myapp/view_staff/#about')

@login_required(login_url='/myapp/login_get/')
def delete_staff(request,id):
    ob = staff_table.objects.get(id=id)
    ab=ob.LOGIN
    ab.delete()
    return redirect('/myapp/view_staff/#about')

@login_required(login_url='/myapp/login_get/')
def admin_view_complaints(request):
    obj=complaint_table.objects.all()
    return render(request,'adminn/view_complaint.html',{"data":obj})

@login_required(login_url='/myapp/login_get/')
def admin_send_reply_post(request):
    send_reply=request.POST['reply_message']
    cid=request.POST['complaint_id']
    ob=complaint_table.objects.get(id=cid)
    ob.reply=send_reply
    ob.save()
    return redirect('/myapp/admin_view_complaints/#about')

@login_required(login_url='/myapp/login_get/')
def admin_view_feedback(request):
    obj=feedback_table.objects.all()
    return render(request,'adminn/view_feedback.html',{"data":obj})

@login_required(login_url='/myapp/login_get/')
def admin_view_patient(request):
    obj=patient_table.objects.all()
    return render(request,'adminn/view_patient.html',{"data":obj})

@login_required(login_url='/myapp/login_get/')
def view_work(request):
    data = assign_work_table.objects.all().order_by('-date')
    staff_data = staff_table.objects.all()
    return render(request, 'adminn/view_work.html', {
        'data': data,
        'staff_data': staff_data
    })


def assign_work_post(request):
    if request.method == 'POST':
        staff_id = request.POST['staff_id']
        work_file = request.FILES['work_file']
        last_date = request.POST['last_date']

        st_obj = staff_table.objects.get(id=staff_id)

        ob = assign_work_table()
        ob.STAFF = st_obj
        ob.work = work_file
        ob.last_date = last_date
        ob.date = datetime.now().date()
        ob.status = "pending"
        ob.submitted_work = "pending"
        ob.save()
        return redirect('/myapp/view_work/')

def view_patient_report(request, id):
    records = emotion_table.objects.filter(patient_id=id).order_by('date', 'time')
    emotion_list = ['Angry', 'Disgusted', 'Fearful', 'Happy', 'Sad', 'Suprised', 'Neutral']

    source_data = list(records.values('source', 'emotion').annotate(count=Count('id')))
    time_labels = [r.time.strftime("%H:%M") for r in records]
    emotion_values = [r.emotion for r in records]

    context = {
        "pid": id,
        "data": records,
        "source_json": json.dumps(source_data),
        "time_labels": json.dumps(time_labels),
        "emotion_values": json.dumps(emotion_values),
        "emotion_list": json.dumps(emotion_list),
    }
    return render(request, 'adminn/view_patient_report.html', context)

#====================================================STAFF==============================================================
#====================================================STAFF==============================================================
#====================================================STAFF==============================================================
#====================================================STAFF==============================================================
#====================================================STAFF==============================================================

@login_required(login_url='/myapp/login_get/')
def staff_home(request):
    return render(request, 'staff/staff_index.html')

@login_required(login_url='/myapp/login_get/')
def staff_view_patients(request):
    obj=patient_table.objects.filter(STAFF__LOGIN_id=request.user.id)
    return render(request,'staff/staff_view_patients.html',{"data":obj})


@login_required(login_url='/myapp/login_get/')
def staff_add_patient_post(request):
    if request.method == "POST":
        name = request.POST['name']
        phone = request.POST['phone']
        place = request.POST['place']
        post = request.POST['post']
        pin = request.POST['pin']
        photo = request.FILES['photo']

        staff_obj = staff_table.objects.get(LOGIN_id=request.user.id)

        db = patient_table()
        db.name = name
        db.phone = phone
        db.place = place
        db.post = post
        db.pin = pin
        db.photo = photo
        db.STAFF = staff_obj
        db.save()
        return redirect('/myapp/staff_view_patients/#main')


@login_required(login_url='/myapp/login_get/')
def staff_edit_patient_post(request):
    if request.method == "POST":
        pid = request.POST['pid']
        ob = patient_table.objects.get(id=pid)
        ob.name = request.POST['name']
        ob.phone = request.POST['phone']
        ob.place = request.POST['place']
        ob.post = request.POST['post']
        ob.pin = request.POST['pin']
        if 'photo' in request.FILES:
            ob.photo = request.FILES['photo']
        ob.save()
        return redirect('/myapp/staff_view_patients/#main')

@login_required(login_url='/myapp/login_get/')
def staff_delete_patient(request, id):
    patient_table.objects.get(id=id).delete()
    return redirect('/myapp/staff_view_patients/#main')

@login_required(login_url='/myapp/login_get/')
def staff_view_work(request):
    obj = assign_work_table.objects.filter(STAFF__LOGIN_id=request.user.id).order_by('-date')
    today = datetime.now().date()
    return render(request, 'staff/staff_view_works.html', {"data": obj, "today": today})

@login_required(login_url='/myapp/login_get/')
def staff_submit_work_post(request):
    if request.method == "POST":
        work_id = request.POST['work_id']
        submission = request.FILES['submission_file']
        ob = assign_work_table.objects.get(id=work_id)
        ob.submitted_work = submission
        ob.status = "completed"
        ob.save()
        return redirect('/myapp/staff_view_work/#main')

@login_required(login_url='/myapp/login_get/')
def staff_send_feedback(request):
    return render(request, 'staff/staff_send_feedback.html')

@login_required(login_url='/myapp/login_get/')
def staff_send_feedback_post(request):
    if request.method == "POST":
        content = request.POST['feedback_text']
        staff_obj = staff_table.objects.get(LOGIN_id=request.user.id)
        db = feedback_table()
        db.STAFF = staff_obj
        db.feedback = content
        db.date = datetime.now().date()
        db.save()
        return redirect('/myapp/staff_home/')

@login_required(login_url='/myapp/login_get/')
def staff_view_complaints(request):
    obj = complaint_table.objects.filter(STAFF__LOGIN_id=request.user.id).order_by('-date')
    return render(request, 'staff/staff_view_complaints.html', {"data": obj})

@login_required(login_url='/myapp/login_get/')
def staff_send_complaint_post(request):
    if request.method == "POST":
        complaint_text = request.POST['complaint_text']
        staff_obj = staff_table.objects.get(LOGIN_id=request.user.id)
        db = complaint_table()
        db.STAFF = staff_obj
        db.complaint = complaint_text
        db.date = datetime.now().date()
        db.reply = "pending"
        db.save()
        return redirect('/myapp/staff_view_complaints/#main')

@login_required(login_url='/myapp/login_get/')
def staff_view_patient_report(request, id):
    records = emotion_table.objects.filter(patient_id=id).order_by('date', 'time')
    emotion_list = ['Angry', 'Disgusted', 'Fearful', 'Happy', 'Sad', 'Suprised', 'Neutral']

    source_data = list(records.values('source', 'emotion').annotate(count=Count('id')))
    time_labels = [r.time.strftime("%H:%M") for r in records]
    emotion_values = [r.emotion for r in records]

    context = {
        "pid": id,
        "data": records,
        "source_json": json.dumps(source_data),
        "time_labels": json.dumps(time_labels),
        "emotion_values": json.dumps(emotion_values),
        "emotion_list": json.dumps(emotion_list),
    }
    return render(request, 'staff/staff_view_patient_report.html', context)


#================================================MAIN===================================================================
#================================================MAIN===================================================================
#================================================MAIN===================================================================
#================================================MAIN===================================================================
#================================================MAIN===================================================================

def find_eeg_emotion(request,id):
    request.session['pid']=id
    ob=emotion_table.objects.filter(patient_id=id,source='EEG')
    print(ob)
    return render(request,'staff/upload_eeg.html',{"data":ob})

from django.contrib import messages
def upload_csv_view(request):
    patient_id = request.session['pid']
    if request.method == 'POST' and request.FILES.get('csv_file'):
        file = request.FILES['csv_file']
        result = predict_eeg_emotion(file)
        emotion_map = {
            'NEGATIVE': 'Sad',
            'POSITIVE': 'Happy',
            'NEUTRAL': 'Neutral'
        }
        res = emotion_map.get(str(result).upper(), "Unknown")
        request.session['prediction_result'] = res
        messages.success(request, "EEG Data Processed Successfully!")

        ob=emotion_table()
        ob.patient_id=patient_table.objects.get(id=patient_id)
        ob.emotion=res
        ob.source='EEG'
        ob.date=datetime.now().today()
        ob.time=datetime.now().time()
        ob.save()
        return redirect(f'/myapp/find_eeg_emotion/{patient_id}')
    return redirect(f'/myapp/find_eeg_emotion/{patient_id}')
