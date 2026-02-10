from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Sum
from django.utils import timezone
import logging
from .models import Transaction, Budget

logger = logging.getLogger(__name__)
print("DEBUG: apps.tracker.signals.py LOADED")

@receiver(post_save, sender=Transaction)
def transaction_saved(sender, instance, created, **kwargs):
    if instance.transaction_type != 'expense':
        return

    user = instance.owner
    category = instance.category
    currency = instance.currency
    
    # Check if there's a budget for this category and currency
    budgets = Budget.objects.filter(owner=user, category=category, currency=currency)
    
    for budget in budgets:
        now = timezone.now()
        total_expenses = Transaction.objects.filter(
            owner=user,
            category=category,
            currency=currency,
            transaction_type='expense',
            date__year=now.year,
            date__month=now.month
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Diagnostic logging
        print(f"SIGNAL: Checking budget for {user.username} - {category.name}")
        print(f"SIGNAL: Spent: {total_expenses}, Limit: {budget.amount}")

        if total_expenses > budget.amount:
            if user.email:
                subject = f"Budget Exceeded Alert: {category.name}"
                message = f"Warning! You have exceeded your budget for {category.name} ({currency}).\n\nLimit: {budget.amount}\nSpent: {total_expenses}"
                try:
                    logger.info(f"Sending signal-based budget email to {user.email}")
                    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
                    print(f"SIGNAL: Email sent to {user.email}")
                except Exception as e:
                    logger.error(f"Failed to send budget email in signal: {e}", exc_info=True)
            else:
                logger.warning(f"User {user.username} has no email address set for budget signal.")
