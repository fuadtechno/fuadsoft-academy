import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_project.settings')
django.setup()

from django.db import connection
from customers.models import Client

demo = Client.objects.get(schema_name='demo')
connection.set_tenant(demo)

with connection.cursor() as cursor:
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = current_schema()")
    tables = cursor.fetchall()
    print('Tables in demo schema:')
    for t in tables:
        print('  -', t[0])