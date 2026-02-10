import os
import django
from django.conf import settings
import uuid
import sys

# Unbuffered output
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from apps.tracker.models import Category, Transaction
from django.test import Client
from django.urls import reverse
from django.utils import timezone

print("Starting debug v3...", flush=True)

try:
    username = f"user_{uuid.uuid4().hex[:8]}"
    print(f"Creating user {username}...", flush=True)
    u = User.objects.create_user(username, 'test@debug.com', 'pass')
    print("User created.", flush=True)
    
    print("Creating category...", flush=True)
    c = Category.objects.create(name='Cat1', type='income', owner=u)
    print("Category created.", flush=True)

    print("Logging in...", flush=True)
    client = Client()
    client.login(username=username, password='pass')
    
    print("Testing Transaction Create...", flush=True)
    date_str = str(timezone.now().date())
    
    try:
        resp = client.post(reverse('transaction-create'), {
            'date': date_str,
            'amount': '100.00',
            'category': c.id,
            'transaction_type': 'expense',
            'description': 'Test Transaction',
            'currency': 'USD'
        })
        print(f"Transaction Create response: {resp.status_code}", flush=True)
        if resp.status_code == 302:
            print("Transaction created successfully (Redirected).", flush=True)
        else:
            print(f"Response content prefix: {resp.content[:500]}", flush=True)
    except Exception as e:
        print(f"Transaction Create CRASHED: {e}", flush=True)
        import traceback
        traceback.print_exc()

    print("Testing Report View...", flush=True)
    try:
        resp = client.get(reverse('reports'))
        print(f"Report View response: {resp.status_code}", flush=True)
        if resp.status_code == 200:
            print("Report view loaded successfully.", flush=True)
            if b'Test Transaction' in resp.content or b'USD' in resp.content or b'Expense' in resp.content:
                 print("Report content verification: Data found.", flush=True)
            else:
                 print("Report content verification: Data NOT found (might be expected if filtering logic mismatch).", flush=True)
                 # print(resp.content.decode())
        else:
             print(f"Report view failed: {resp.status_code}", flush=True)
    except Exception as e:
        print(f"Report View CRASHED: {e}", flush=True)
        import traceback
        traceback.print_exc()

except Exception as e:
    print(f"Caught top-level exception: {e}", flush=True)
    import traceback
    traceback.print_exc()
