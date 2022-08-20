from django.urls import path

from . import views

urlpatterns = [
    path('api/category/create/', views.add_category, name = 'add-category'),
    path('api/category/list/<str:linkID>', views.list_categories, name = 'list-category'),
    path('api/category/update/<int:pk>', views.update_category, name = 'update-category'),
    path('api/category/delete/<int:pk>', views.delete_category, name = 'delete-category'),

    path('api/budget/create/', views.add_budget, name = 'add-budget'),
    path('api/budget/list/<str:linkID>', views.list_budgets, name = 'list-budget'),
    path('api/budget/update/<str:linkID>', views.update_budget, name = 'update-budget'),
    path('api/budget/delete/<str:linkID>', views.delete_budget, name = 'delete-budget'),
    path('api/budget/balance/<str:linkID>', views.get_balance, name = 'balance'),
    path('api/budget/sum/<str:linkID>', views.get_sum, name = 'sum'),

    path('api/transaction/create/', views.add_transaction, name = 'add-transaction'),
    path('api/transaction/list/<str:linkID>', views.list_transactions, name = 'list-transaction'),
    path('api/transaction/update/<int:pk>', views.update_transaction, name = 'update-transaction'),
    path('api/transaction/delete/<int:pk>', views.delete_transaction, name = 'delete-transaction'),

    path('api/purchase/create/', views.add_purchase, name = 'add-purchase'),
    path('api/purchase/list/<str:linkID>', views.list_purchases, name = 'list-purchase'),
    path('api/purchase/update/<int:pk>', views.update_purchase, name = 'update-purchase'),
    path('api/purchase/delete/<int:pk>', views.delete_purchase, name = 'delete-purchase'),
    path('api/purchase/complete/<int:pk>', views.complete_purchase, name = 'complete-purchase'),

    path('yearly/<str:linkID>', views.yearly_view, name= 'yearly-view'),
    path('monthly/<str:linkID>', views.monthly_view, name= 'monthly-view'),
]