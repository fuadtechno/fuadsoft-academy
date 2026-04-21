from rest_framework import serializers
from accounts.models import User
from students.models import Student
from teachers.models import Teacher
from classes.models import Class, Section, Subject
from attendance.models import Attendance
from exams.models import Exam, Result
from fees.models import FeeStructure, FeePayment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone', 'is_active']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class_name = serializers.CharField(source='class_enrolled.name', read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'student_id', 'user', 'class_enrolled', 'class_name', 'section', 'parent_name', 'parent_phone', 'parent_email', 'is_active']


class TeacherSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Teacher
        fields = ['id', 'teacher_id', 'user', 'qualification', 'specialization', 'experience_years', 'is_active']


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'description']


class ClassSerializer(serializers.ModelSerializer):
    subjects = SubjectSerializer(many=True, read_only=True)

    class Meta:
        model = Class
        fields = ['id', 'name', 'level', 'section', 'subjects', 'class_teacher', 'academic_year', 'is_active']


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['id', 'class_enrolled', 'name', 'capacity']


class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)

    class Meta:
        model = Attendance
        fields = ['id', 'class_enrolled', 'student', 'student_name', 'student_id', 'date', 'status', 'remarks']


class ExamSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source='class_enrolled.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)

    class Meta:
        model = Exam
        fields = ['id', 'name', 'class_enrolled', 'class_name', 'subject', 'subject_name', 'exam_type', 'date', 'total_marks', 'passing_marks']


class ResultSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)

    class Meta:
        model = Result
        fields = ['id', 'exam', 'student', 'student_name', 'student_id', 'marks_obtained', 'grade', 'remarks']


class FeeStructureSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source='class_enrolled.name', read_only=True)

    class Meta:
        model = FeeStructure
        fields = ['id', 'class_enrolled', 'class_name', 'fee_type', 'amount', 'due_date', 'academic_year']


class FeePaymentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    receipt_number = serializers.CharField(read_only=True)

    class Meta:
        model = FeePayment
        fields = ['id', 'student', 'student_name', 'fee_structure', 'amount_paid', 'payment_date', 'payment_method', 'receipt_number']