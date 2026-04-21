from django.urls import path
from . import views

urlpatterns = [
    path('announcements/', views.announcement_list, name='announcement_list'),
    path('announcements/create/', views.announcement_create, name='announcement_create'),
    path('announcements/<int:pk>/update/', views.announcement_update, name='announcement_update'),
    path('announcements/<int:pk>/delete/', views.announcement_delete, name='announcement_delete'),

    path('', views.my_notifications, name='my_notifications'),
    path('<int:pk>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('email/', views.send_email_notification, name='send_email_notification'),
]