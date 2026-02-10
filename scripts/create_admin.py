import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User

try:
    if not User.objects.filter(username='admin').exists():
        print("Creating admin user...")
        User.objects.create_superuser('admin', 'admin@example.com', 'password')
        print("Admin user created: admin / password")
    else:
        print("Admin user already exists.")
        # Reset password just in case
        u = User.objects.get(username='admin')
        u.set_password('password')
        u.save()
        print("Admin password reset to: password")
except Exception as e:
    print(f"Error creating admin: {e}")
