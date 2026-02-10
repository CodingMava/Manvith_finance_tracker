import os
import django
from django.conf import settings
import uuid

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from apps.tracker.models import Category, Transaction
from django.test import Client
from django.urls import reverse
from django.utils import timezone

print("Starting debug v2...")

try:
    username = f"user_{uuid.uuid4().hex[:8]}"
    print(f"Creating user {username}...")
    u = User.objects.create_user(username, 'test@debug.com', 'pass')
    print("User created.")
    
    print("Creating category...")
    c = Category.objects.create(name='Cat1', type='income', owner=u)
    print("Category created.")

    print("Logging in...")
    client = Client()
    client.login(username=username, password='pass')
    
    print("Testing Transaction Create...")
    date_str = str(timezone.now().date())
    print(f"Sending date: {date_str}")
    
    resp = client.post(reverse('transaction-create'), {
        'date': date_str,
        'amount': '100.00',
        'category': c.id,
        'transaction_type': 'expense',
        'description': 'Test Transaction',
        'currency': 'USD'
    })
    print(f"Transaction Create response: {resp.status_code}")
    
    if resp.status_code == 302:
        print("Transaction created successfully (Redirected).")
        # Verify it exists
        if Transaction.objects.filter(owner=u).exists():
            print("Transaction found in DB.")
        else:
            print("ERROR: Transaction NOT found in DB despite 302.")
    else:
        print(f"Response content prefix: {resp.content[:500]}")
        if 'form' in resp.context:
             print(f"Form errors: {resp.context['form'].errors}")

except Exception as e:
    print(f"Caught exception: {e}")
    import traceback
    traceback.print_exc()
