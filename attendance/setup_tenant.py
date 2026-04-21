import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_project.settings')
django.setup()

from django.db import connection
from customers.models import Client, Domain
from django.contrib.auth import get_user_model

User = get_user_model()

print("=== Setting up Multi-Tenant Configuration ===\n")

# Create public schema
public_tenant, created = Client.objects.get_or_create(
    schema_name='public',
    defaults={
        'name': 'GlobalEdu SaaS',
        'is_active': True,
    }
)
if created:
    print("Created public tenant: GlobalEdu SaaS (schema: public)")
else:
    print("Public tenant already exists: GlobalEdu SaaS")

# Ensure public domain exists
if not Domain.objects.filter(domain='localhost').exists():
    Domain.objects.create(tenant=public_tenant, domain='localhost', is_primary=True)
    print("Created domain: localhost -> public")

# Create demo schema
demo_tenant, created = Client.objects.get_or_create(
    schema_name='demo',
    defaults={
        'name': 'Demo School',
        'is_active': True,
    }
)
if created:
    print("Created demo tenant: Demo School (schema: demo)")
else:
    print("Demo tenant already exists: Demo School")

# Ensure demo domain exists
if not Domain.objects.filter(domain='demo.edu-saas.com').exists():
    Domain.objects.create(tenant=demo_tenant, domain='demo.edu-saas.com', is_primary=True)
    print("Created domain: demo.edu-saas.com -> demo")

print("\n=== Tenant Setup Complete ===\n")

# Now let's set up the superuser in the demo schema
print("=== Setting up Superuser for Demo Schema ===\n")

# Switch to demo schema
connection.set_tenant(demo_tenant)

# Check if admin exists
admin_exists = User.objects.filter(username='admin').exists()
if not admin_exists:
    admin_user = User.objects.create_superuser(
        username='admin',
        email='admin@demo.edu-saas.com',
        password='admin123',
        first_name='Admin',
        last_name='User'
    )
    print(f"Created superuser 'admin' in demo schema with password 'admin123'")
else:
    # Update password to ensure it's correct
    admin_user = User.objects.get(username='admin')
    admin_user.set_password('admin123')
    admin_user.save()
    print(f"Updated superuser 'admin' password in demo schema")

print("\n=== All Setup Complete ===")
print("\nAccess URLs:")
print("  - Local: http://localhost/")
print("  - Demo: http://demo.edu-saas.com/")
print("\nLogin credentials:")
print("  - Username: admin")
print("  - Password: admin123")