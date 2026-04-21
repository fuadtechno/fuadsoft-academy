from django.urls import path
from . import views

urlpatterns = [
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/create/', views.SubjectCreateView.as_view(), name='subject_create'),
    path('subjects/<int:pk>/update/', views.SubjectUpdateView.as_view(), name='subject_update'),
    path('subjects/<int:pk>/delete/', views.SubjectDeleteView.as_view(), name='subject_delete'),

    path('', views.class_list, name='class_list'),
    path('create/', views.ClassCreateView.as_view(), name='class_create'),
    path('<int:pk>/update/', views.ClassUpdateView.as_view(), name='class_update'),
    path('<int:pk>/delete/', views.ClassDeleteView.as_view(), name='class_delete'),

    path('sections/', views.section_list, name='section_list'),
    path('sections/create/', views.SectionCreateView.as_view(), name='section_create'),
    path('sections/<int:pk>/update/', views.SectionUpdateView.as_view(), name='section_update'),

    path('timetable/<int:class_id>/', views.timetable_view, name='timetable'),
    path('timetable/create/', views.TimetableCreateView.as_view(), name='timetable_create'),
]