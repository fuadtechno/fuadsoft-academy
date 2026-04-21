from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'user', 'class_enrolled', 'section', 'parent_name', 'is_active')
    list_filter = ('is_active', 'class_enrolled', 'section')
    search_fields = ('student_id', 'user__first_name', 'user__last_name', 'parent_name')
    list_editable = ('is_active',)
    raw_id_fields = ('user',)