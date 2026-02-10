import os
import django
from django.conf import settings
import uuid

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

print("Starting debug v4...")

try:
    client = Client()
    username = f"newuser_{uuid.uuid4().hex[:6]}"
    email = f"{username}@example.com"
    
    print(f"Testing registration for {username}...")
    resp = client.post(reverse('register'), {
        'username': username,
        'email': email,
        'password': 'password123'
    })
    
    print(f"Registration status: {resp.status_code}")
    if resp.status_code == 302:
        print("Registration successful (Redirection).")
    else:
        print("Registration failed.")
        if 'form' in resp.context:
            print(f"Form errors: {resp.context['form'].errors}")

    print("Checking if user exists in DB...")
    if User.objects.filter(username=username).exists():
        print("User found in DB.")
    else:
        print("User NOT found in DB.")

    print("Testing Dashboard (Login required)...")
    client.login(username=username, password='password123')
    resp = client.get(reverse('index'))
    print(f"Dashboard status: {resp.status_code}")
    if resp.status_code != 200:
        print(f"Dashboard failed to load. Response content snippet: {resp.content[:200]}")
    else:
        print("Dashboard loaded successfully.")

except Exception as e:
    print(f"Caught exception: {e}")
    import traceback
    traceback.print_exc()
