import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_project.settings')
django.setup()

from django.db import connection
from customers.models import Client

demo = Client.objects.get(schema_name='demo')
connection.set_tenant(demo)

from accounts.models import User
from accounts.forms import LoginForm

# Test form validation
form_data = {'identifier': 'fuetech', 'password': 'test123'}
form = LoginForm(data=form_data)
print('Form valid:', form.is_valid())
print('Form errors:', form.errors)

# Test view logic
if form.is_valid():
    identifier = form.cleaned_data['identifier'].strip()
    password = form.cleaned_data['password']
    
    user = User.objects.filter(username__iexact=identifier).first()
    print('User found:', user.username if user else None)
    
    if user:
        print('Password check:', user.check_password(password))