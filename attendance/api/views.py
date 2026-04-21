from django.db import models
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from accounts.models import User
from students.models import Student
from teachers.models import Teacher
from classes.models import Class, Section, Subject
from attendance.models import Attendance
from exams.models import Exam, Result
from fees.models import FeeStructure, FeePayment
from .serializers import (
    UserSerializer, StudentSerializer, TeacherSerializer,
    ClassSerializer, SectionSerializer, SubjectSerializer,
    AttendanceSerializer, ExamSerializer, ResultSerializer,
    FeeStructureSerializer, FeePaymentSerializer
)


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_admin


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        return queryset


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.select_related('user', 'class_enrolled').all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        class_id = self.request.query_params.get('class')
        if class_id:
            queryset = queryset.filter(class_enrolled_id=class_id)
        return queryset


class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.select_related('user').all()
    serializer_class = TeacherSerializer
    permission_classes = [permissions.IsAuthenticated]


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ClassViewSet(viewsets.ModelViewSet):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.select_related('student__user', 'class_enrolled').all()
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        class_id = self.request.query_params.get('class')
        date = self.request.query_params.get('date')
        if class_id:
            queryset = queryset.filter(class_enrolled_id=class_id)
        if date:
            queryset = queryset.filter(date=date)
        return queryset


class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.select_related('class_enrolled', 'subject').all()
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        class_id = self.request.query_params.get('class')
        if class_id:
            queryset = queryset.filter(class_enrolled_id=class_id)
        return queryset


class ResultViewSet(viewsets.ModelViewSet):
    queryset = Result.objects.select_related('student__user', 'exam').all()
    serializer_class = ResultSerializer
    permission_classes = [permissions.IsAuthenticated]


class FeeStructureViewSet(viewsets.ModelViewSet):
    queryset = FeeStructure.objects.select_related('class_enrolled').all()
    serializer_class = FeeStructureSerializer
    permission_classes = [permissions.IsAuthenticated]


class FeePaymentViewSet(viewsets.ModelViewSet):
    queryset = FeePayment.objects.select_related('student__user', 'fee_structure').all()
    serializer_class = FeePaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def by_student(self, request):
        student_id = request.query_params.get('student_id')
        payments = self.queryset.filter(student_id=student_id)
        serializer = self.get_serializer(payments, many=True)
        return Response(serializer.data)


class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        data = {
            'total_students': Student.objects.filter(is_active=True).count(),
            'total_teachers': Teacher.objects.filter(is_active=True).count(),
            'total_classes': Class.objects.filter(is_active=True).count(),
            'total_subjects': Subject.objects.count(),
            'total_exams': Exam.objects.count(),
            'total_fee_collected': FeePayment.objects.aggregate(total=models.Sum('amount_paid'))['total'] or 0,
        }
        return Response(data)