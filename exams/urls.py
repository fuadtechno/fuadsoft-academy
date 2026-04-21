from django.urls import path
from . import views

urlpatterns = [
    path('', views.exam_list, name='exam_list'),
    path('create/', views.exam_create, name='exam_create'),
    path('<int:pk>/update/', views.exam_update, name='exam_update'),
    path('<int:pk>/delete/', views.exam_delete, name='exam_delete'),
    path('<int:exam_id>/results/', views.add_result, name='add_result'),
    path('<int:exam_id>/view-results/', views.view_results, name='view_results'),
    path('<int:exam_id>/generate-report/', views.generate_report_card, name='generate_report_card'),
    path('<int:exam_id>/export-pdf/', views.export_results_pdf, name='export_results_pdf'),
]