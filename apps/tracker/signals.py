from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Sum
from django.utils import timezone
import logging
from .models import Transaction, Budget

from django.contrib.auth.models import User

logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        from .models import Profile
        Profile.objects.get_or_create(user=instance)
        logger.info(f"Automatically created profile for user: {instance.username}")

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
        logger.info(f"SIGNAL: Checking budget for {user.username} - {category.name} (Spent: {total_expenses}, Limit: {budget.amount})")

        if total_expenses > budget.amount:
            # Use profile email if set, otherwise fallback to registration email
            profile = getattr(user, 'profile', None)
            recipient = profile.notification_email if profile and profile.notification_email else user.email
            
            if recipient:
                subject = f"Budget Exceeded Alert: {category.name}"
                message = f"Warning! You have exceeded your budget for {category.name} ({currency}).\n\nLimit: {budget.amount}\nSpent: {total_expenses}"
                
                def send_email_async(sub, msg, from_mail, to_mail):
                    import socket
                    # Set a timeout for the socket connection to avoid hanging the thread
                    socket.setdefaulttimeout(10)
                    try:
                        logger.info(f"Background thread: Attempting to send budget email to {to_mail}")
                        send_mail(sub, msg, from_mail, [to_mail], fail_silently=False)
                        logger.info(f"Background thread: Email sent successfully to {to_mail}")
                    except Exception as e:
                        logger.error(f"Background thread: Failed to send budget email: {e}")

                import threading
                email_thread = threading.Thread(
                    target=send_email_async,
                    args=(subject, message, settings.DEFAULT_FROM_EMAIL, recipient)
                )
                email_thread.daemon = True
                email_thread.start()
                logger.info(f"Budget threshold hit for {user.username} - {category.name}. Started background thread for email to {recipient}")
            else:
                logger.warning(f"User {user.username} has no email address set for budget signal.")
        else:
             logger.info(f"SIGNAL: Budget NOT exceeded for {user.username} - {category.name} (Spent: {total_expenses}, Limit: {budget.amount})")
