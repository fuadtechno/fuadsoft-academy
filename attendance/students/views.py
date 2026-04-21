from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Student
from .forms import StudentCreationForm, StudentUpdateForm


@login_required
def student_list(request):
    students = Student.objects.select_related('user', 'class_enrolled', 'section').all()
    search = request.GET.get('search')
    class_id = request.GET.get('class')
    if search:
        students = students.filter(
            Q(student_id__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(parent_name__icontains=search)
        )
    if class_id:
        students = students.filter(class_enrolled_id=class_id)
    return render(request, 'students/student_list.html', {'students': students})


@login_required
def student_detail(request, pk):
    student = get_object_or_404(Student.objects.select_related('user', 'class_enrolled', 'section'), pk=pk)
    return render(request, 'students/student_detail.html', {'student': student})


class StudentCreateView(CreateView):
    model = Student
    form_class = StudentCreationForm
    template_name = 'students/student_form.html'
    success_url = reverse_lazy('student_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Student created successfully.')
        return response

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)


class StudentUpdateView(UpdateView):
    model = Student
    form_class = StudentUpdateForm
    template_name = 'students/student_form.html'
    success_url = reverse_lazy('student_list')


class StudentDeleteView(DeleteView):
    model = Student
    template_name = 'students/student_confirm_delete.html'
    success_url = reverse_lazy('student_list')

    def form_valid(self, form):
        student = self.get_object()
        student.user.delete()
        return super().form_valid(form)