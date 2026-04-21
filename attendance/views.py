from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Attendance, AttendanceSummary
from students.models import Student
from classes.models import Class


@login_required
def attendance_mark(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)
    students = Student.objects.filter(class_enrolled=class_obj, is_active=True).select_related('user')
    date = request.GET.get('date', timezone.now().date())

    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d').date()

    attendance_records = Attendance.objects.filter(
        class_enrolled=class_obj,
        date=date
    )

    return render(request, 'attendance/attendance_mark.html', {
        'class': class_obj,
        'students': students,
        'date': date,
        'records': attendance_records,
    })


@login_required
def mark_attendance(request):
    if request.method == 'POST':
        class_id = request.POST.get('class_id')
        date = request.POST.get('date')
        student_id = request.POST.get('student_id')
        status = request.POST.get('status')
        remarks = request.POST.get('remarks', '')

        class_obj = get_object_or_404(Class, id=class_id)
        student = get_object_or_404(Student, id=student_id)

        attendance, created = Attendance.objects.update_or_create(
            student=student,
            class_enrolled=class_obj,
            date=date,
            defaults={
                'status': status,
                'remarks': remarks,
                'marked_by': getattr(request.user, 'teacher_profile', None)
            }
        )

        return JsonResponse({'success': True, 'status': status})
    return JsonResponse({'success': False})


@login_required
def attendance_report(request):
    class_id = request.GET.get('class')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    classes = Class.objects.all()
    attendance = Attendance.objects.all()

    if class_id:
        attendance = attendance.filter(class_enrolled_id=class_id)
    if date_from:
        attendance = attendance.filter(date__gte=date_from)
    if date_to:
        attendance = attendance.filter(date__lte=date_to)

    attendance = attendance.select_related('student__user', 'class_enrolled')

    return render(request, 'attendance/attendance_report.html', {
        'attendance': attendance,
        'classes': classes,
    })


@login_required
def attendance_summary(request):
    class_id = request.GET.get('class')
    month = request.GET.get('month')
    year = request.GET.get('year')

    classes = Class.objects.all()
    summaries = AttendanceSummary.objects.all()

    if class_id:
        summaries = summaries.filter(class_enrolled_id=class_id)
    if month and year:
        summaries = summaries.filter(month=month, year=year)

    summaries = summaries.select_related('class_enrolled')

    return render(request, 'attendance/attendance_summary.html', {
        'summaries': summaries,
        'classes': classes,
    })


@login_required
def export_attendance_csv(request):
    import csv
    from django.http import HttpResponse

    class_id = request.GET.get('class')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    attendance = Attendance.objects.all()

    if class_id:
        attendance = attendance.filter(class_enrolled_id=class_id)
    if date_from:
        attendance = attendance.filter(date__gte=date_from)
    if date_to:
        attendance = attendance.filter(date__lte=date_to)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance.csv"'

    writer = csv.writer(response)
    writer.writerow(['Student ID', 'Student Name', 'Class', 'Date', 'Status', 'Remarks'])

    for record in attendance:
        writer.writerow([
            record.student.student_id,
            record.student.user.get_full_name,
            record.class_enrolled.name,
            record.date,
            record.status,
            record.remarks,
        ])

    return response