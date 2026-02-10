from django.urls import path
from . import views

urlpatterns = [
    path('transactions/', views.transaction_list, name='transaction-list'),
    path('transactions/add/', views.transaction_create, name='transaction-create'),
    path('transactions/<int:pk>/edit/', views.transaction_update, name='transaction-update'),
    path('transactions/<int:pk>/delete/', views.transaction_delete, name='transaction-delete'),
    
    path('categories/', views.category_list, name='category-list'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category-delete'),
    
    path('budgets/', views.budget_list, name='budget-list'),
    path('budgets/<int:pk>/delete/', views.budget_delete, name='budget-delete'),
    
    path('reports/', views.report_view, name='reports'),
    path('debug-email/', views.debug_email_view, name='debug-email'),
]
