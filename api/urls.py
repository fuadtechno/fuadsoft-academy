from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'students', views.StudentViewSet)
router.register(r'teachers', views.TeacherViewSet)
router.register(r'subjects', views.SubjectViewSet)
router.register(r'classes', views.ClassViewSet)
router.register(r'sections', views.SectionViewSet)
router.register(r'attendance', views.AttendanceViewSet)
router.register(r'exams', views.ExamViewSet)
router.register(r'results', views.ResultViewSet)
router.register(r'fee-structures', views.FeeStructureViewSet)
router.register(r'fee-payments', views.FeePaymentViewSet)
router.register(r'dashboard', views.DashboardViewSet, basename='dashboard')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]