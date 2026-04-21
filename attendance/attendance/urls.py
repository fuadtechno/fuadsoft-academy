from django.urls import path
from . import views

urlpatterns = [
    path('mark/<int:class_id>/', views.attendance_mark, name='attendance_mark'),
    path('mark/', views.mark_attendance, name='mark_attendance'),
    path('report/', views.attendance_report, name='attendance_report'),
    path('summary/', views.attendance_summary, name='attendance_summary'),
    path('export/', views.export_attendance_csv, name='export_attendance_csv'),
]