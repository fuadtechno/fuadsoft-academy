from django.db.models import Sum, Count, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.urls import reverse_lazy
from .models import User
from .forms import LoginForm, RegistrationForm
from students.models import Student
from teachers.models import Teacher
from classes.models import Class, Subject
from attendance.models import Attendance
from fees.models import FeePayment
from notifications.models import Announcement
from exams.models import Exam, Result
from datetime import date


class RoleRequiredMixin(AccessMixin):
    role_required = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if self.role_required and request.user.role != self.role_required:
            if not request.user.is_superuser:
                return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['identifier'].strip()
            password = form.cleaned_data['password']
            
            # Ensure we're using the correct tenant schema
            if hasattr(request, 'tenant') and request.tenant:
                from django.db import connection
                connection.set_tenant(request.tenant)
            
            # Find user by email, phone, or username
            user = None
            if '@' in identifier:
                user = User.objects.filter(email__iexact=identifier).first()
            else:
                user = User.objects.filter(Q(username__iexact=identifier) | Q(phone__iexact=identifier)).first()
            
            # Verify password manually
            if user and user.check_password(password):
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
                full_name = f"{user.first_name} {user.last_name}".strip() or user.username
                messages.success(request, f'Welcome back, {full_name}!')
                return redirect('dashboard')
            else:
                if user:
                    messages.error(request, 'Invalid password')
                else:
                    messages.error(request, 'User not found')
        else:
            messages.error(request, 'Invalid form')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def user_register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Ensure we're using the correct tenant schema
            if hasattr(request, 'tenant') and request.tenant:
                from django.db import connection
                connection.set_tenant(request.tenant)
            
            # Save user with password (form.save() handles password hashing)
            user = form.save(commit=False)
            user.email = form.cleaned_data.get('email', '').lower()
            user.phone = form.cleaned_data.get('phone', '')
            user.is_active = True
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            user.save()
            
            login(request, user)
            full_name = f"{user.first_name} {user.last_name}".strip() or user.username
            messages.success(request, f'Welcome to SmartSchool Pro, {full_name}!')
            return redirect('dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required
def profile(request):
    return render(request, 'accounts/profile.html', {'user': request.user})


@login_required
def dashboard(request):
    from datetime import timedelta
    import calendar

    total_students = Student.objects.filter(is_active=True).count()
    total_teachers = Teacher.objects.filter(is_active=True).count()
    total_classes = Class.objects.filter(is_active=True).count()
    total_subjects = Subject.objects.count()

    today = date.today()
    today_attendance = Attendance.objects.filter(date=today)
    present_today = today_attendance.filter(status='present').count()
    total_today = today_attendance.count()
    attendance_rate = round((present_today / total_today * 100), 1) if total_today > 0 else 0

    total_revenue = FeePayment.objects.aggregate(total=Sum('amount_paid'))['total'] or 0

    student_distribution = (
        Class.objects.filter(is_active=True)
        .annotate(student_count=Count('students'))
        .values_list('name', 'student_count')
        .order_by('-student_count')[:7]
    )

    months_data = []
    for i in range(6, -1, -1):
        day_date = today - timedelta(days=i)
        day_name = day_date.strftime('%m/%d')
        day_total = FeePayment.objects.filter(
            payment_date=day_date
        ).aggregate(total=Sum('amount_paid'))['total'] or 0
        months_data.append({'month': day_name, 'amount': day_total})

    upcoming_exams = (
        Exam.objects.filter(date__gte=today)
        .select_related('class_enrolled', 'subject')
        .order_by('date')[:5]
    )

    recent_students = (
        Student.objects
        .select_related('user', 'class_enrolled')
        .only('id', 'student_id', 'user__first_name', 'user__last_name', 'class_enrolled__name')
        .order_by('-id')[:5]
    )

    capitalized_students = []
    for student in recent_students:
        capitalized_students.append({
            'id': student.id,
            'student_id': student.student_id,
            'name': student.user.get_capitalized_name(),
            'class': student.class_enrolled.name if student.class_enrolled else None
        })
    
    announcements = (
        Announcement.objects
        .filter(is_published=True, publish_date__lte=today)
        .order_by('-publish_date')[:3]
    )

    context = {
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_classes': total_classes,
        'total_subjects': total_subjects,
        'attendance_rate': attendance_rate,
        'revenue': total_revenue,
        'recent_students': capitalized_students,
        'announcements': announcements,
        'upcoming_exams': upcoming_exams,
        'student_distribution': list(student_distribution),
        'months_data': months_data,
    }
    return render(request, 'dashboard.html', context)


@login_required
def export_students_pdf(request):
    from .pdf_utils import generate_student_list_pdf
    students = Student.objects.select_related('user', 'class_enrolled').order_by('user__last_name')
    buffer = generate_student_list_pdf(students)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="students.pdf"'
    return response


@login_required
def export_fees_pdf(request):
    from .pdf_utils import generate_fee_collection_pdf
    payments = FeePayment.objects.select_related('student__user').order_by('-payment_date')[:500]
    buffer = generate_fee_collection_pdf(payments)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="fee_collection.pdf"'
    return response


@login_required
def export_results_pdf(request):
    from .pdf_utils import generate_exam_results_pdf
    results = Result.objects.select_related('student__user', 'exam__subject').order_by('-exam__date')[:500]
    buffer = generate_exam_results_pdf(results)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="exam_results.pdf"'
    return response


class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        role = self.request.GET.get('role')
        if role:
            queryset = queryset.filter(role=role)
        return queryset


class UserCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = User
    template_name = 'accounts/user_form.html'
    fields = ['username', 'email', 'password', 'first_name', 'last_name', 'role', 'phone', 'address']
    success_url = reverse_lazy('user_list')
    role_required = User.Role.ADMIN

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'User {form.instance.username} created successfully.')
        return response

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'accounts/user_form.html'
    fields = ['username', 'email', 'first_name', 'last_name', 'role', 'phone', 'address', 'photo', 'date_of_birth', 'is_active']
    success_url = reverse_lazy('user_list')

    def get_queryset(self):
        return User.objects.filter(role__in=[User.Role.TEACHER, User.Role.STUDENT])


class UserDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = User
    template_name = 'accounts/user_confirm_delete.html'
    success_url = reverse_lazy('user_list')
    role_required = User.Role.ADMIN