import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from apps.tracker.models import Category
from django.test import Client
from django.urls import reverse

print("Starting debug...")

try:
    print("Creating user...")
    u = User.objects.create_user('testdebug', 'test@debug.com', 'pass')
    print("User created.")
    
    print("Creating category...")
    c = Category.objects.create(name='Cat1', type='income', owner=u)
    print("Category created.")

    print("Logging in...")
    client.login(username='testdebug', password='pass') # Use the user created above
    
    print("Testing Transaction Create...")
    from django.utils import timezone
    resp = client.post(reverse('transaction-create'), {
        'date': str(timezone.now().date()),
        'amount': '100.00',
        'category': c.id,
        'transaction_type': 'expense',
        'description': 'Test Transaction',
        'currency': 'USD'
    })
    print(f"Transaction Create response: {resp.status_code}")
    if resp.status_code != 302:
        print(f"Response content prefix: {resp.content[:200]}")
        if 'form' in resp.context:
             print(f"Form errors: {resp.context['form'].errors}")
    else:
        print("Transaction created successfully.")

except Exception as e:
    print(f"Caught exception: {e}")
    import traceback
    traceback.print_exc()
