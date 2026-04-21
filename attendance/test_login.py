import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_project.settings')
django.setup()

from django.db import connection
from customers.models import Client
from accounts.models import User

# Switch to demo schema
demo = Client.objects.get(schema_name='demo')
connection.set_tenant(demo)

# Test login logic
identifier = 'fuetech'
password = 'test123'

# Find user
user = User.objects.filter(username__iexact=identifier).first()
print(f'User found: {user.username if user else None}')

# Verify password
if user and user.check_password(password):
    print('Login SUCCESS!')
else:
    print('Login FAILED!')