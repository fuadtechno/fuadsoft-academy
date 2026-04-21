from django import forms
from django.core.exceptions import ValidationError
from datetime import date, datetime
from .models import Exam

class BootstrapFormMixin:
    """Automatically adds Bootstrap classes to all form fields"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, (forms.TextInput, forms.Textarea, forms.NumberInput)):
                field.widget.attrs['class'] = 'form-control'
            elif isinstance(field, forms.DateInput):
                field.widget.attrs.update({'class': 'form-control', 'type': 'date'})
            elif isinstance(field, forms.TimeInput):
                field.widget.attrs.update({'class': 'form-control', 'type': 'time'})
            elif isinstance(field, forms.Select):
                field.widget.attrs['class'] = 'form-select'
            elif isinstance(field, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'


class ExamForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['name', 'class_enrolled', 'subject', 'exam_type', 'date', 'start_time', 'end_time', 'total_marks', 'passing_marks', 'instructions']

    def clean_date(self):
        exam_date = self.cleaned_data.get('date')
        if exam_date and exam_date < date.today():
            raise ValidationError('Exam date cannot be in the past.')
        return exam_date

    def clean_total_marks(self):
        total = self.cleaned_data.get('total_marks')
        if total and total <= 0:
            raise ValidationError('Total marks must be greater than 0.')
        return total

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        total_marks = cleaned_data.get('total_marks')
        passing_marks = cleaned_data.get('passing_marks')
        
        if start_time and end_time and end_time <= start_time:
            raise ValidationError('End time must be after start time.')
        
        if passing_marks and total_marks:
            if passing_marks > total_marks:
                raise ValidationError('Passing marks cannot exceed total marks!')
            if passing_marks < 0:
                raise ValidationError('Passing marks cannot be negative.')
        
        return cleaned_data