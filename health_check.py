import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_project.settings')
django.setup()

from django.db import connection
from customers.models import Client, Domain

print("=== Database & Tenant Health Check ===\n")

# 1. PostgreSQL connection test
print("1. PostgreSQL Connection:")
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        print("   [OK] PostgreSQL is reachable")
except Exception as e:
    print("   [X] PostgreSQL error:", e)

# 2. Check schemas
print("\n2. Schemas:")
tenants = Client.objects.all()
for t in tenants:
    print("   -", t.name, "(schema:", t.schema_name + ")")

# 3. Domain routing
print("\n3. Domain Routing:")
domains = Domain.objects.select_related('tenant').all()
for d in domains:
    print("   -", d.domain, "->", d.tenant.name, "(", d.tenant.schema_name + ")")

# 4. Check admin in demo schema
print("\n4. Admin User in Demo Schema:")
demo_tenant = Client.objects.filter(schema_name='demo').first()
if demo_tenant:
    connection.set_tenant(demo_tenant)
    from django.contrib.auth import get_user_model
    User = get_user_model()
    admin = User.objects.filter(username='admin', is_superuser=True).first()
    if admin:
        print("   [OK] Superuser 'admin' exists in demo schema")
    else:
        print("   [X] No superuser found in demo schema")

# 5. Static files check
print("\n5. Static Files:")
import os.path
static_root = os.path.join(os.path.dirname(__file__), 'staticfiles')
if os.path.exists(static_root):
    count = len(os.listdir(static_root))
    print("   [!] staticfiles/ exists with", count, "items")
    print("   Run: python manage.py collectstatic")
else:
    print("   [INFO] staticfiles/ not created yet")
    print("   Run: python manage.py collectstatic")

print("\n=== Health Check Complete ===")