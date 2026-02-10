import os
import django
from django.conf import settings
import sys

# Unbuffered output
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

print("Starting debug login...", flush=True)

try:
    username = 'admin'
    print(f"Testing login for user {username}...", flush=True)

    print("Logging in...", flush=True)
    client = Client()
    resp = client.post(reverse('login'), {
        'username': username,
        'password': 'pass'
    })
    
    print(f"Login Response Status: {resp.status_code}", flush=True)
    if resp.status_code == 302:
        print(f"Login Redirect Location: {resp.url}", flush=True)
        if resp.url == '/' or resp.url == reverse('index'):
            print("Login SUCCESS.", flush=True)
        else:
             print(f"Login Redirect Unexpected: {resp.url}", flush=True)
    else:
        print("Login FAILED (not a redirect).", flush=True)
        print(f"Response content prefix: {resp.content[:500]}", flush=True)
        # Check context for form errors
        if 'form' in resp.context:
             print(f"Form errors: {resp.context['form'].errors}", flush=True)
             if resp.context['form'].non_field_errors():
                 print(f"Non-field errors: {resp.context['form'].non_field_errors()}", flush=True)

except Exception as e:
    import traceback
    with open('traceback_log.txt', 'w') as f:
        traceback.print_exc(file=f)
    print(f"Captured exception in traceback_log.txt: {e}", flush=True)

except Exception as e:
    import traceback
    with open('traceback_log.txt', 'a') as f:
        traceback.print_exc(file=f)
    print(f"Captured top-level exception in traceback_log.txt: {e}", flush=True)
