from django.contrib import admin
from .models import Subject, Class, Section, Timetable


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'description')
    search_fields = ('name', 'code')


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'section', 'academic_year', 'class_teacher', 'is_active')
    list_filter = ('academic_year', 'is_active', 'level')
    search_fields = ('name', 'section')
    filter_horizontal = ('subjects',)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('class_enrolled', 'name', 'capacity')
    list_filter = ('class_enrolled',)


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ('class_enrolled', 'subject', 'teacher', 'day', 'start_time', 'end_time')
    list_filter = ('class_enrolled', 'day')
    search_fields = ('class_enrolled__name', 'subject__name')