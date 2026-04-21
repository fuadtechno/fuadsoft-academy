from django import forms
from django.core.exceptions import ValidationError
from datetime import date
from .models import FeeStructure, FeePayment, FeeDue

class BootstrapFormMixin:
    """Automatically adds Bootstrap classes to all form fields"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, (forms.TextInput, forms.Textarea, forms.NumberInput)):
                field.widget.attrs['class'] = 'form-control'
            elif isinstance(field, forms.DateInput):
                field.widget.attrs.update({'class': 'form-control', 'type': 'date'})
            elif isinstance(field, forms.Select):
                field.widget.attrs['class'] = 'form-select'
            elif isinstance(field, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'


class FeeStructureForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = FeeStructure
        fields = ['class_enrolled', 'fee_type', 'amount', 'description', 'due_date', 'academic_year', 'is_active']

    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        if due_date and due_date < date.today():
            raise ValidationError('Due date cannot be in the past.')
        return due_date