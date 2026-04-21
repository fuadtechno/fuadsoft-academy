from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Avg, Max
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.urls import reverse_lazy
from datetime import datetime
from .models import Exam, Result, ReportCard
from students.models import Student
from classes.models import Class, Subject
from .forms import ExamForm


class AdminRequiredMixin(UserPassesTestMixin):
    """Only allow admins to access"""
    def test_func(self):
        return self.request.user.is_authenticated and (
            self.request.user.is_admin or self.request.user.is_superuser
        )


class TeacherOrAdminMixin(UserPassesTestMixin):
    """Allow teachers or admins"""
    def test_func(self):
        return self.request.user.is_authenticated and (
            self.request.user.is_admin or 
            self.request.user.is_teacher or 
            self.request.user.is_superuser
        )


class ExamListView(TeacherOrAdminMixin, ListView):
    model = Exam
    template_name = 'exams/exam_list.html'
    context_object_name = 'exams'
    paginate_by = 20

    def get_queryset(self):
        return (
            Exam.objects
            .select_related('class_enrolled', 'subject')
            .filter(
                class_enrolled=self.request.GET.get('class'),
                exam_type=self.request.GET.get('type')
            )
        )


class ExamCreateView(AdminRequiredMixin, CreateView):
    model = Exam
    form_class = ExamForm
    template_name = 'exams/exam_form.html'
    success_url = reverse_lazy('exam_list')

    def form_valid(self, form):
        messages.success(self.request, 'Exam created successfully.')
        response = super().form_valid(form)
        
        exam = self.object
        students = Student.objects.filter(
            class_enrolled=exam.class_enrolled,
            is_active=True
        )
        
        if students.exists():
            result_entries = [
                Result(exam=exam, student=student, marks_obtained=0)
                for student in students
            ]
            Result.objects.bulk_create(result_entries, ignore_conflicts=True)
            messages.info(self.request, f'Created {len(result_entries)} result entries for students.')
        
        return response

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)


class ExamUpdateView(AdminRequiredMixin, UpdateView):
    model = Exam
    form_class = ExamForm
    template_name = 'exams/exam_form.html'
    success_url = reverse_lazy('exam_list')

    def form_valid(self, form):
        messages.success(self.request, 'Exam updated successfully.')
        return super().form_valid(form)


class ExamDeleteView(AdminRequiredMixin, DeleteView):
    model = Exam
    template_name = 'exams/exam_confirm_delete.html'
    success_url = reverse_lazy('exam_list')

    def form_valid(self, form):
        messages.success(self.request, 'Exam deleted successfully.')
        return super().form_valid(form)


exam_list = ExamListView.as_view()
exam_create = ExamCreateView.as_view()
exam_update = ExamUpdateView.as_view()
exam_delete = ExamDeleteView.as_view()


@login_required
def add_result(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    students = Student.objects.filter(class_enrolled=exam.class_enrolled, is_active=True)

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        marks = request.POST.get('marks')
        remarks = request.POST.get('remarks', '')

        student = get_object_or_404(Student, id=student_id)
        result, created = Result.objects.update_or_create(
            exam=exam,
            student=student,
            defaults={'marks_obtained': marks, 'remarks': remarks}
        )
        messages.success(request, f'Result saved for {student.user.get_full_name}')
        return redirect('add_result', exam_id)

    results = Result.objects.filter(exam=exam)
    return render(request, 'exams/add_result.html', {'exam': exam, 'students': students, 'results': results})


@login_required
def view_results(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    results = Result.objects.filter(exam=exam).select_related('student__user')

    stats = {
        'total_students': results.count(),
        'average_marks': results.aggregate(Avg('marks_obtained'))['marks_obtained__avg'],
        'max_marks': results.aggregate(Max('marks_obtained'))['marks_obtained__max'],
    }

    return render(request, 'exams/view_results.html', {'exam': exam, 'results': results, 'stats': stats})


@login_required
def generate_report_card(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    results = Result.objects.filter(exam=exam).order_by('-marks_obtained')

    rank = 1
    for result in results:
        report_card, created = ReportCard.objects.update_or_create(
            student=result.student,
            exam=exam,
            defaults={
                'class_enrolled': exam.class_enrolled,
                'total_marks': exam.total_marks * exam.class_enrolled.subjects.count(),
                'obtained_marks': result.marks_obtained,
                'rank': rank,
            }
        )
        if not created:
            report_card.rank = rank
            report_card.save()
        rank += 1

    messages.success(request, 'Report cards generated successfully.')
    return redirect('exam_list')


@login_required
def export_results_pdf(request, exam_id):
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from django.contrib.auth.models import User

    exam = get_object_or_404(Exam, pk=exam_id)
    results = Result.objects.filter(exam=exam).select_related('student__user')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{exam.name}_results.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph(f"Exam Results: {exam.name}", styles['Title']))
    elements.append(Paragraph(f"Class: {exam.class_enrolled.name}", styles['Normal']))
    elements.append(Spacer(1, 0.25 * inch))

    data = [['Rank', 'Student ID', 'Name', 'Marks', 'Grade']]
    rank = 1
    for result in results:
        data.append([
            str(rank),
            result.student.student_id,
            result.student.user.get_full_name,
            str(result.marks_obtained),
            result.grade,
        ])
        rank += 1

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)
    doc.build(elements)
    return response