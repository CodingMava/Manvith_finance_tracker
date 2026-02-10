from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Transaction, Category, Budget
from .forms import TransactionForm, CategoryForm, BudgetForm
from django.core.mail import send_mail
from django.conf import settings

@login_required
def transaction_list(request):
    transactions = Transaction.objects.filter(owner=request.user).order_by('-date')
    return render(request, 'tracker/transaction_list.html', {'transactions': transactions})

@login_required
def transaction_create(request):
    if request.method == 'POST':
        form = TransactionForm(request.user, request.POST, request.FILES)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.owner = request.user
            
            # Text-based category handling
            cat_name = form.cleaned_data['category_name']
            cat_type = transaction.transaction_type
            category_obj, _ = Category.objects.get_or_create(
                owner=request.user, 
                name=cat_name, 
                type=cat_type
            )
            transaction.category = category_obj
            
            transaction.save()
            return redirect('transaction-list')
    else:
        form = TransactionForm(request.user)
    return render(request, 'tracker/transaction_form.html', {'form': form, 'title': 'Add Transaction'})

@login_required
def transaction_update(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = TransactionForm(request.user, request.POST, request.FILES, instance=transaction)
        if form.is_valid():
            transaction = form.save(commit=False)
            # Update category from text
            cat_name = form.cleaned_data['category_name']
            cat_type = transaction.transaction_type
            category_obj, _ = Category.objects.get_or_create(
                owner=request.user, 
                name=cat_name, 
                type=cat_type
            )
            transaction.category = category_obj
            transaction.save()
            return redirect('transaction-list')
    else:
        form = TransactionForm(request.user, instance=transaction)
    return render(request, 'tracker/transaction_form.html', {'form': form, 'title': 'Edit Transaction'})

@login_required
def transaction_delete(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, owner=request.user)
    if request.method == 'POST':
        transaction.delete()
        return redirect('transaction-list')
    return render(request, 'tracker/transaction_confirm_delete.html', {'transaction': transaction})

@login_required
def category_list(request):
    categories = Category.objects.filter(owner=request.user)
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.owner = request.user
            category.save()
            return redirect('category-list')
    else:
        form = CategoryForm()
    return render(request, 'tracker/category_list.html', {'categories': categories, 'form': form})

from django.db.models import ProtectedError
from django.contrib import messages

@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk, owner=request.user)
    if request.method == 'POST':
        try:
            category.delete()
            messages.success(request, f"Category '{category.name}' deleted.")
            return redirect('category-list')
        except ProtectedError:
            messages.error(request, f"Cannot delete '{category.name}' because it has existing transactions. Please delete the transactions first.")
            return redirect('category-list')
    return render(request, 'tracker/category_confirm_delete.html', {'category': category})

@login_required
def budget_list(request):
    budgets = Budget.objects.filter(owner=request.user)
    
    # Calculate spent amount for each budget in current month
    from django.utils import timezone
    now = timezone.now()
    
    for b in budgets:
        spent = Transaction.objects.filter(
            owner=request.user,
            category=b.category,
            currency=b.currency,
            transaction_type='expense',
            date__year=now.year,
            date__month=now.month
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        b.spent = float(spent)
        b.remaining = float(b.amount) - b.spent
        b.overage = abs(b.remaining) if b.remaining < 0 else 0
        b.percent = min(100, (b.spent / float(b.amount)) * 100) if b.amount > 0 else 0
        status_class = "bg-error" if b.percent > 90 else "bg-warning" if b.percent > 70 else "bg-success"
        b.progress_html = f'<div class="progress-bar {status_class}" style="width: {b.percent}%; "></div>'
        
        # Pre-calculated strings for template to avoid leakage
        b.limit_text = f"{b.currency} {float(b.amount):.2f}"
        b.spent_text = f"{b.currency} {b.spent:.2f}"
        b.remaining_text = f"{b.currency} {b.remaining:.2f}"
        b.overage_text = f"{b.currency} {b.overage:.2f}"

    if request.method == 'POST':
        form = BudgetForm(request.user, request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.owner = request.user
            
            # Manual category creation
            cat_name = form.cleaned_data['category_name']
            category_obj, _ = Category.objects.get_or_create(
                owner=request.user,
                name=cat_name,
                type='expense'
            )
            budget.category = category_obj
            budget.save()
            return redirect('budget-list')
    else:
        form = BudgetForm(request.user)
    return render(request, 'tracker/budget_list.html', {'budgets': budgets, 'form': form})

@login_required
def budget_delete(request, pk):
    budget = get_object_or_404(Budget, pk=pk, owner=request.user)
    if request.method == 'POST':
        budget.delete()
        return redirect('budget-list')
    return render(request, 'tracker/budget_confirm_delete.html', {'budget': budget})

import json

@login_required
def report_view(request):
    # Category Distribution (Expenses only)
    category_data = Category.objects.filter(owner=request.user, type='expense')\
        .annotate(total=Sum('transaction__amount'))\
        .filter(total__gt=0)\
        .values('name', 'total')
    
    category_list_data = list(category_data)
    for i in category_list_data:
        i['total'] = float(i['total'])

    # Monthly Trends - Support Multi-Currency
    from django.db.models.functions import TruncMonth
    monthly_stats = Transaction.objects.filter(owner=request.user)\
        .annotate(month=TruncMonth('date'))\
        .values('month', 'currency', 'transaction_type')\
        .annotate(total=Sum('amount'))\
        .order_by('month', 'currency')
    
    # Restructure for easier consumption in template
    reports_map = {}
    for item in monthly_stats:
        m_key = item['month'].strftime("%Y-%m")
        cur = item['currency']
        composite_key = f"{m_key}_{cur}"
        
        if composite_key not in reports_map:
            reports_map[composite_key] = {
                'month': item['month'], 
                'currency': cur,
                'income': 0, 
                'expense': 0, 
                'month_label': f"{item['month'].strftime('%b %Y')} ({cur})"
            }
        
        t_type = item['transaction_type']
        val = float(item['total'])
        if t_type == 'income':
            reports_map[composite_key]['income'] += val
        elif t_type == 'expense':
            reports_map[composite_key]['expense'] += abs(val)

    # Finalize net (Savings = Income - Expense)
    for report in reports_map.values():
        report['net'] = report['income'] - report['expense']

    sorted_reports = sorted(reports_map.values(), key=lambda x: (x['month'], x['currency']))

    context = {
        'reports': sorted_reports,
        'report_json': json.dumps(sorted_reports, default=str),
        'category_json': json.dumps(category_list_data),
    }
    return render(request, 'tracker/reports.html', context)

