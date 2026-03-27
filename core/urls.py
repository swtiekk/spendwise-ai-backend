from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('auth/register/',    views.RegisterView.as_view()),
    path('auth/me/',          views.current_user_view),

    # Profile
    path('profile/',          views.profile_view),

    # Categories
    path('categories/',       views.categories_view),

    # Expenses
    path('expenses/',         views.ExpenseListCreateView.as_view()),
    path('expenses/<int:pk>/', views.ExpenseDetailView.as_view()),
    path('expenses/stats/',   views.expense_stats_view),

    # Income
    path('income/',           views.IncomeListCreateView.as_view()),

    # Dashboard
    path('dashboard/',        views.dashboard_view),

    # Savings Goals
    path('savings-goals/',          views.SavingsGoalListCreateView.as_view()),
    path('savings-goals/<int:pk>/', views.SavingsGoalDetailView.as_view()),

    # Alerts
    path('alerts/',                    views.alerts_view),
    path('alerts/<int:pk>/read/',      views.mark_alert_read),

    # ML & Smart Purchase
    path('insights/',         views.insights_view),
    path('smart-purchase/',   views.smart_purchase_view),

    # Admin
    path('admin/users/',      views.admin_users_view),
    path('admin/dashboard/',  views.admin_dashboard_view),
]