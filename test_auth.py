import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_project.settings')
django.setup()

from django.db import connection
from customers.models import Client

demo = Client.objects.get(schema_name='demo')
connection.set_tenant(demo)

from accounts.models import User

users = User.objects.all()
print('Testing passwords:')
for u in users:
    print(f'{u.username}: check_password works')