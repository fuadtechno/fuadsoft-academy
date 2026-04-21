from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Subject, Class, Section, Timetable


@login_required
def subject_list(request):
    subjects = Subject.objects.all()
    return render(request, 'classes/subject_list.html', {'subjects': subjects})


class SubjectCreateView(CreateView):
    model = Subject
    fields = ['name', 'code', 'description']
    template_name = 'classes/subject_form.html'
    success_url = reverse_lazy('subject_list')

    def form_valid(self, form):
        messages.success(self.request, 'Subject created successfully.')
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)


class SubjectUpdateView(UpdateView):
    model = Subject
    fields = ['name', 'code', 'description']
    template_name = 'classes/subject_form.html'
    success_url = reverse_lazy('subject_list')


class SubjectDeleteView(DeleteView):
    model = Subject
    template_name = 'classes/subject_confirm_delete.html'
    success_url = reverse_lazy('subject_list')


@login_required
def class_list(request):
    classes = Class.objects.all()
    return render(request, 'classes/class_list.html', {'classes': classes})


class ClassCreateView(CreateView):
    model = Class
    fields = ['name', 'level', 'section', 'subjects', 'academic_year', 'is_active']
    template_name = 'classes/class_form.html'
    success_url = reverse_lazy('class_list')

    def form_valid(self, form):
        messages.success(self.request, 'Class created successfully.')
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)


class ClassUpdateView(UpdateView):
    model = Class
    fields = ['name', 'level', 'section', 'subjects', 'class_teacher', 'academic_year', 'is_active']
    template_name = 'classes/class_form.html'
    success_url = reverse_lazy('class_list')


class ClassDeleteView(DeleteView):
    model = Class
    template_name = 'classes/class_confirm_delete.html'
    success_url = reverse_lazy('class_list')


@login_required
def section_list(request):
    sections = Section.objects.select_related('class_enrolled').all()
    return render(request, 'classes/section_list.html', {'sections': sections})


class SectionCreateView(CreateView):
    model = Section
    fields = ['class_enrolled', 'name', 'capacity']
    template_name = 'classes/section_form.html'
    success_url = reverse_lazy('section_list')

    def form_valid(self, form):
        messages.success(self.request, 'Section created successfully.')
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)


class SectionUpdateView(UpdateView):
    model = Section
    fields = ['name', 'capacity']
    template_name = 'classes/section_form.html'
    success_url = reverse_lazy('section_list')


@login_required
def timetable_view(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)
    timetable = Timetable.objects.filter(class_enrolled=class_id).order_by('day', 'start_time')
    return render(request, 'classes/timetable.html', {'class': class_obj, 'timetable': timetable})


class TimetableCreateView(CreateView):
    model = Timetable
    fields = ['class_enrolled', 'subject', 'teacher', 'day', 'start_time', 'end_time', 'room']
    template_name = 'classes/timetable_form.html'
    success_url = reverse_lazy('class_list')

    def form_valid(self, form):
        messages.success(self.request, 'Timetable entry created successfully.')
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)