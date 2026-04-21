from django import forms
from django.core.exceptions import ValidationError
from datetime import date, datetime
from .models import Announcement, Notification

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


class AnnouncementForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'message', 'priority', 'target_role', 'publish_date', 'expiry_date', 'is_published']

    def clean_publish_date(self):
        publish_date = self.cleaned_data.get('publish_date')
        if publish_date and publish_date < date.today():
            raise ValidationError('Publish date cannot be in the past.')
        return publish_date