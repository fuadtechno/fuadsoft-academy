from django.contrib import admin
from .models import Exam, Result, ReportCard


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('name', 'class_enrolled', 'subject', 'exam_type', 'date', 'total_marks', 'is_active')
    list_filter = ('exam_type', 'date', 'class_enrolled')
    search_fields = ('name', 'class_enrolled__name')


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'marks_obtained', 'grade')
    list_filter = ('exam', 'grade')
    search_fields = ('student__student_id', 'student__user__first_name')


@admin.register(ReportCard)
class ReportCardAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'obtained_marks', 'percentage', 'grade', 'rank')
    list_filter = ('exam', 'grade')
    search_fields = ('student__student_id',)