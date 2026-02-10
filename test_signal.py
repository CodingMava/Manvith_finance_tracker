import os
import django
import sys
from pathlib import Path

# Setup
sys.path.append(str(Path(__file__).resolve().parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from apps.tracker.models import Transaction, Category, Budget
from decimal import Decimal
from django.utils import timezone

def test_signal_flow():
    print("Starting signal flow test...")
    user = User.objects.get(username='manvith')
    
    # Ensure a category exists
    category, _ = Category.objects.get_or_create(owner=user, name='Food', type='expense')
    
    # Ensure a budget exists: $100
    Budget.objects.filter(owner=user, category=category, currency='USD').delete()
    budget = Budget.objects.create(owner=user, category=category, amount=Decimal('100.00'), currency='USD')
    
    print(f"Created budget: {budget.amount} {budget.currency} for {category.name}")

    # Delete old transactions for this month/cat to have a clean slate
    now = timezone.now()
    Transaction.objects.filter(
        owner=user, 
        category=category, 
        currency='USD',
        date__year=now.year,
        date__month=now.month
    ).delete()

    print("Creating transaction of $150 (Should trigger alert)...")
    transaction = Transaction.objects.create(
        owner=user,
        category=category,
        amount=Decimal('150.00'),
        currency='USD',
        transaction_type='expense',
        date=now.date()
    )
    
    print("Transaction created. Check terminal output for 'SIGNAL: Email sent' message.")

if __name__ == '__main__':
    test_signal_flow()
