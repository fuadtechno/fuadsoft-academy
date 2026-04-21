from django.contrib import admin
from .models import Attendance, AttendanceSummary


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'class_enrolled', 'date', 'status', 'marked_by')
    list_filter = ('date', 'status', 'class_enrolled')
    search_fields = ('student__student_id', 'student__user__first_name', 'student__user__last_name')
    date_hierarchy = 'date'


@admin.register(AttendanceSummary)
class AttendanceSummaryAdmin(admin.ModelAdmin):
    list_display = ('class_enrolled', 'month', 'year', 'present_days', 'total_days', 'attendance_percentage')
    list_filter = ('month', 'year', 'class_enrolled')