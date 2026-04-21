from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts import views as accounts_views
from accounts.views import dashboard, export_students_pdf, export_fees_pdf, export_results_pdf

urlpatterns = [
    path('admin/', admin.site.urls),

    path('accounts/', include('accounts.urls')),
    path('students/', include('students.urls')),
    path('teachers/', include('teachers.urls')),
    path('classes/', include('classes.urls')),
    path('attendance/', include('attendance.urls')),
    path('exams/', include('exams.urls')),
    path('fees/', include('fees.urls')),
    path('notifications/', include('notifications.urls')),
    path('api/', include('api.urls')),

    path('dashboard/', dashboard, name='dashboard'),
    path('export/students/', export_students_pdf, name='export_students_pdf'),
    path('export/fees/', export_fees_pdf, name='export_fees_pdf'),
    path('export/results/', export_results_pdf, name='export_results_pdf'),
    path('', accounts_views.user_login, name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)