from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .forms import RegistrationForm
from django.contrib.auth.forms import AuthenticationForm
from apps.tracker.models import Transaction
from django.db.models import Sum
import json
from django.contrib.auth.models import User
from apps.tracker.models import Profile

@login_required
def index(request):
    # Aggregate income and expenses separately
    income_qs = Transaction.objects.filter(owner=request.user, transaction_type='income')\
        .values("currency")\
        .annotate(total=Sum("amount"))
    
    expense_qs = Transaction.objects.filter(owner=request.user, transaction_type='expense')\
        .values("currency")\
        .annotate(total=Sum("amount"))
    
    savings_qs = Transaction.objects.filter(owner=request.user, transaction_type='savings')\
        .values("currency")\
        .annotate(total=Sum("amount"))
    
    # Map data for easy lookup
    income_map = {item['currency']: float(item['total']) for item in income_qs}
    expense_map = {item['currency']: float(item['total']) for item in expense_qs}
    
    currencies = set(income_map.keys()) | set(expense_map.keys())
    savings_data = []
    for cur in currencies:
        inc = income_map.get(cur, 0)
        exp = expense_map.get(cur, 0)
        # Net savings = (Income - Expense)
        savings_data.append({
            'currency': cur,
            'income': inc,
            'expense': exp,
            'net_savings': inc - exp
        })

    context = {
        "savings_data": savings_data,
        "savings_json": json.dumps(savings_data),
    }
    return render(request, "index.html", context)

def register(request):
    form = RegistrationForm(request.POST or None)
    if form.is_valid():
        user = User.objects.create_user(
            username=form.cleaned_data["username"],
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password"]
        )
        # Profile is created via signal or manually here if no signal
        # Assuming signal for now, or just create it
        if not hasattr(user, 'profile'):
            Profile.objects.create(user=user)
            
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect("index")
    return render(request, "register.html", {"form": form})

@login_required
def profile_view(request):
    return render(request, "core/profile.html", {"user": request.user})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("index")
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("login")
