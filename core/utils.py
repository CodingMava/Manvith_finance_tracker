import json, time, os
from decimal import Decimal
from pathlib import Path
from django.conf import settings
from django.utils import timezone

def _month_range(dt):
    start = dt.replace(day=1)
    end = (dt.replace(month=dt.month % 12 + 1, day=1)
           if dt.month < 12 else
           dt.replace(year=dt.year + 1, month=1, day=1))
    return start, end

def _data_dir():
    base = getattr(settings, "BASE_DIR", os.getcwd())
    d = Path(base) / "finance_data"
    d.mkdir(exist_ok=True)
    return d

def _data_file_for(user):
    return _data_dir() / f"user_{user.id}.json"

def _load_user_data(user):
    path = _data_file_for(user)
    if not path.exists():
        return {"transactions": [], "budgets": []}
    return json.loads(path.read_text())

def _save_user_data(user, data):
    _data_file_for(user).write_text(json.dumps(data, default=str))

def check_and_notify_budget(user, category, currency="USD"):
    from django.core.mail import send_mail
    from apps.tracker.models import Budget, Transaction
    from django.db.models import Sum

    try:
        budget = Budget.objects.get(owner=user, category=category, currency=currency)
    except Budget.DoesNotExist:
        return

    start, end = _month_range(timezone.now().date())
    spent = (
        Transaction.objects.filter(
            owner=user,
            category=category,
            transaction_type="expense",
            date__gte=start,
            date__lt=end,
        ).aggregate(Sum("amount"))["amount__sum"]
        or Decimal("0")
    )

    if spent > budget.amount:
        import logging
        logger = logging.getLogger(__name__)
        try:
            if user.email:
                logger.info(f"Budget exceeded for {user.username} - {category.name}. Sending email to {user.email}")
                send_mail(
                    "Budget exceeded",
                    f"You exceeded {category.name} ({currency}).\nSpent: {spent}\nLimit: {budget.amount}",
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
            else:
                logger.warning(f"Budget exceeded for {user.username} but no email set.")
        except Exception as e:
            logger.error(f"Failed to send budget notification to {user.email}: {e}", exc_info=True)
