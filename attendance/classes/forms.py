from django import forms
from django.core.exceptions import ValidationError
from datetime import date
from .models import Subject, Class, Section, Timetable

class BootstrapFormMixin:
    """Automatically adds Bootstrap classes to all form fields"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, forms.TextInput):
                field.widget.attrs['class'] = 'form-control'
            elif isinstance(field, forms.Textarea):
                field.widget.attrs['class'] = 'form-control'
            elif isinstance(field, forms.NumberInput):
                field.widget.attrs['class'] = 'form-control'
            elif isinstance(field, forms.DateInput):
                field.widget.attrs.update({'class': 'form-control', 'type': 'date'})
            elif isinstance(field, forms.TimeInput):
                field.widget.attrs.update({'class': 'form-control', 'type': 'time'})
            elif isinstance(field, forms.Select):
                field.widget.attrs['class'] = 'form-select'
            elif isinstance(field, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'


class SubjectForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code', 'description']


class ClassForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Class
        fields = ['name', 'level', 'section', 'subjects', 'academic_year', 'is_active']


class SectionForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Section
        fields = ['class_enrolled', 'name', 'capacity']


class TimetableForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Timetable
        fields = ['class_enrolled', 'subject', 'teacher', 'day', 'start_time', 'end_time', 'room']