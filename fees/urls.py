from django.urls import path
from . import views

urlpatterns = [
    path('structure/', views.fee_structure_list, name='fee_structure_list'),
    path('structure/create/', views.fee_structure_create, name='fee_structure_create'),
    path('structure/<int:pk>/update/', views.fee_structure_update, name='fee_structure_update'),

    path('', views.fee_payment, name='fee_payment'),
    path('record/', views.record_payment, name='record_payment'),
    path('dues/', views.fee_dues, name='fee_dues'),
    path('receipt/<int:payment_id>/', views.generate_receipt, name='generate_receipt'),
    path('revenue/', views.revenue_report, name='revenue_report'),
]