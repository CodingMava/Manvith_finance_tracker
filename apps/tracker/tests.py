from django.test import TestCase, Client
from django.contrib.auth.models import User
from apps.tracker.models import Category, Transaction, Budget, Profile
from django.urls import reverse
from decimal import Decimal
from django.core import mail
from django.utils import timezone
import datetime

class TrackerTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')
        self.client.login(username='testuser', password='password123')
        
        # Setup initial categories
        self.cat_income = Category.objects.create(name='Salary', type='income', owner=self.user)
        self.cat_expense = Category.objects.create(name='Food', type='expense', owner=self.user)

    def test_category_management(self):
        """Test listing and adding categories"""
        # List
        resp = self.client.get(reverse('category-list'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Salary')
        self.assertContains(resp, 'Food')
        
        # Add new category
        resp = self.client.post(reverse('category-list'), {
            'name': 'Transport',
            'type': 'expense'
        })
        self.assertRedirects(resp, reverse('category-list'))
        self.assertTrue(Category.objects.filter(name='Transport', owner=self.user).exists())

    def test_transaction_crud(self):
        """Test transaction creation, listing, update, delete"""
        # Create
        resp = self.client.post(reverse('transaction-create'), {
            'date': str(timezone.now().date()),
            'amount': '100.00',
            'category': self.cat_expense.id,
            'transaction_type': 'expense',
            'description': 'Grocery shopping',
            'currency': 'USD'
        })
        self.assertRedirects(resp, reverse('transaction-list'))
        self.assertEqual(Transaction.objects.count(), 1)
        tx = Transaction.objects.first()
        self.assertEqual(tx.amount, Decimal('100.00'))
        
        # List
        resp = self.client.get(reverse('transaction-list'))
        self.assertContains(resp, '100.00 USD')
        self.assertContains(resp, 'Grocery shopping')

        # Update
        resp = self.client.post(reverse('transaction-update', args=[tx.id]), {
            'date': str(timezone.now().date()),
            'amount': '150.00', # Changed amount
            'category': self.cat_expense.id,
            'transaction_type': 'expense',
            'currency': 'USD'
        })
        self.assertRedirects(resp, reverse('transaction-list'))
        tx.refresh_from_db()
        self.assertEqual(tx.amount, Decimal('150.00'))

        # Delete
        resp = self.client.post(reverse('transaction-delete', args=[tx.id]))
        self.assertRedirects(resp, reverse('transaction-list'))
        self.assertEqual(Transaction.objects.count(), 0)

    def test_budget_and_notifications(self):
        """Test budget creation and email notification on limit exceeded"""
        # Set Budget for Food: $200
        resp = self.client.post(reverse('budget-list'), {
            'category': self.cat_expense.id,
            'amount': '200.00',
            'currency': 'USD'
        })
        self.assertRedirects(resp, reverse('budget-list'))
        self.assertTrue(Budget.objects.filter(category=self.cat_expense, amount=200).exists())

        # Add Expense $150 (Under budget)
        self.client.post(reverse('transaction-create'), {
            'date': timezone.now().date(),
            'amount': '150.00',
            'category': self.cat_expense.id,
            'transaction_type': 'expense',
            'currency': 'USD'
        })
        # Check no email sent
        self.assertEqual(len(mail.outbox), 0)

        # Add Expense $60 (Total $210 -> Exceeds $200)
        self.client.post(reverse('transaction-create'), {
            'date': timezone.now().date(),
            'amount': '60.00',
            'category': self.cat_expense.id,
            'transaction_type': 'expense',
            'currency': 'USD'
        })
        
        # Check email sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Budget Exceeded Alert', mail.outbox[0].subject)
        self.assertIn('Food', mail.outbox[0].body)
        self.assertIn('210.00', mail.outbox[0].body)

    def test_registration(self):
        """Test user registration"""
        self.client.logout()
        resp = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'password123'
        })
        self.assertRedirects(resp, reverse('index'))
        self.assertTrue(User.objects.filter(username='newuser').exists())
        # Check profile creation
        new_user = User.objects.get(username='newuser')
        self.assertTrue(Profile.objects.filter(user=new_user).exists())
