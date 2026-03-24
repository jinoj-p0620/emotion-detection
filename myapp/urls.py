from django.contrib import admin
from django.urls import path

from myapp import views

urlpatterns = [
    path('login_get/', views.login_get),
    path('logouts/', views.logouts),
    path('login_post/', views.login_post),
    path('admin_home/', views.admin_home),

    path('view_staff/', views.view_staff),
    path('add_staff/', views.add_staff),
    path('add_staff_post/', views.add_staff_post),
    path('edit_staff/<id>', views.edit_staff),
    path('edit_staff_post/', views.edit_staff_post),
    path('delete_staff/<id>', views.delete_staff),
    path('admin_view_complaints/', views.admin_view_complaints),
    path('admin_send_reply_post/', views.admin_send_reply_post),
    path('admin_view_feedback/', views.admin_view_feedback),
    path('admin_view_patient/', views.admin_view_patient),
    path('view_work/', views.view_work),
    path('assign_work_post/', views.assign_work_post),
    path('upload_csv_view/', views.upload_csv_view),
    path('find_eeg_emotion/<id>', views.find_eeg_emotion),
    path('view_patient_report/<id>/', views.view_patient_report),


    path('staff_home/', views.staff_home),
    path('staff_view_patients/', views.staff_view_patients),
    path('staff_add_patient_post/', views.staff_add_patient_post),
    path('staff_edit_patient_post/', views.staff_edit_patient_post),
    path('staff_delete_patient/<id>', views.staff_delete_patient),
    path('staff_view_patient_report/<id>', views.staff_view_patient_report),
    path('staff_view_work/', views.staff_view_work),
    path('staff_submit_work_post/', views.staff_submit_work_post),
    path('staff_send_feedback/', views.staff_send_feedback),
    path('staff_send_feedback_post/', views.staff_send_feedback_post),
    path('staff_view_complaints/', views.staff_view_complaints),
    path('staff_send_complaint_post/', views.staff_send_complaint_post),

]
