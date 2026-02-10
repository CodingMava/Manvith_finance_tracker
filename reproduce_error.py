import os
import django
from django.conf import settings

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
from django.conf import settings

# Force SQLite for reproduction
if not settings.configured:
    django.setup()

from django.db import connections
# This is a bit hacky, better to do it before setup or use a test settings file
# But since settings were already loaded, let's try to monkey-patch
settings.DATABASES['default'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': 'db.sqlite3', # Use existing local db
}

from django.contrib.auth.models import User
from apps.tracker.models import Category, Transaction, Budget
from apps.tracker.views import check_budget_exceeded
from decimal import Decimal
from django.utils import timezone

def reproduce():
    print("Setting up reproduction data...")
    user, _ = User.objects.get_or_create(username='reproduction_user')
    user.email = 'test@example.com'
    user.save()

    category, _ = Category.objects.get_or_create(owner=user, name='TestFood', type='expense')
    
    # Create budget
    budget, _ = Budget.objects.get_or_create(owner=user, category=category, currency='USD', defaults={'amount': Decimal('100.00')})
    budget.amount = Decimal('100.00')
    budget.save()

    # Add transactions to exceed budget
    Transaction.objects.filter(owner=user, category=category).delete()
    Transaction.objects.create(
        owner=user,
        category=category,
        amount=Decimal('150.00'),
        currency='USD',
        transaction_type='expense',
        date=timezone.now().date()
    )

    print(f"Calling check_budget_exceeded for user {user.username} and category {category.name}...")
    try:
        check_budget_exceeded(user, category)
        print("check_budget_exceeded finished without raising top-level exception.")
    except Exception as e:
        print(f"REPRODUCED: check_budget_exceeded raised an exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    reproduce()
