from django import forms
from .models import Transaction, Category, Budget

class TransactionForm(forms.ModelForm):
    category_name = forms.CharField(max_length=100, label="Category Name", help_text="e.g. Food, Salary")

    class Meta:
        model = Transaction
        fields = ['date', 'amount', 'currency', 'transaction_type', 'description', 'receipt']
        labels = {
            'date': "Date",
            'amount': "Amount",
            'currency': "Currency",
            'transaction_type': "Type",
            'description': "Notes",
            'receipt': "Receipt"
        }
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.category:
            self.initial['category_name'] = self.instance.category.name

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'type']

class BudgetForm(forms.ModelForm):
    category_name = forms.CharField(max_length=100, label="Category Name", help_text="e.g. Food, Entertainment")

    class Meta:
        model = Budget
        fields = ['amount', 'currency']

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.category:
            self.initial['category_name'] = self.instance.category.name
