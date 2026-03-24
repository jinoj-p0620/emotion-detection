from django.db import models
from django.contrib.auth.models import User,Group

# Create your models here.

class staff_table(models.Model):
    LOGIN = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    qualification = models.CharField(max_length=100)
    place = models.CharField(max_length=100)
    post = models.CharField(max_length=100)
    pin = models.CharField(max_length=100)
    photo = models.FileField()

class patient_table(models.Model):
    STAFF = models.ForeignKey(staff_table, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    place = models.CharField(max_length=100)
    post = models.CharField(max_length=100)
    pin = models.CharField(max_length=100)
    photo = models.FileField()

class patient_report_table(models.Model):
    PATIENT = models.ForeignKey(patient_table, on_delete=models.CASCADE)
    report = models.FileField()
    date = models.DateField()

class feedback_table(models.Model):
    STAFF = models.ForeignKey(staff_table, on_delete=models.CASCADE)
    feedback = models.CharField(max_length=200)
    date = models.DateField()

class complaint_table(models.Model):
    STAFF = models.ForeignKey(staff_table, on_delete=models.CASCADE)
    complaint = models.CharField(max_length=200)
    date = models.DateField()
    reply = models.CharField(max_length=200)

class assign_work_table(models.Model):
    STAFF = models.ForeignKey(staff_table, on_delete=models.CASCADE)
    work = models.FileField()
    submitted_work = models.FileField()
    status = models.CharField(max_length=200)
    last_date=models.DateField()
    date=models.DateField()


class emotion_table(models.Model):
    patient_id = models.ForeignKey(patient_table, on_delete=models.CASCADE)
    emotion = models.CharField(max_length=100)
    source = models.CharField(max_length=100)
    date = models.DateField()
    time = models.TimeField()
