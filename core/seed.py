import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spendwise.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Category, UserProfile, MLInsight, Expense, SavingsGoal, Alert
from datetime import date
from decimal import Decimal

print("🌱 Seeding database...")

# ── Categories ────────────────────────────────────────────
Category.objects.all().delete()

categories = [
    {'key': 'food',          'label': 'Food & Dining',  'icon': '🍔', 'color': '#F59E0B'},
    {'key': 'transport',     'label': 'Transport',       'icon': '🚗', 'color': '#6366F1'},
    {'key': 'shopping',      'label': 'Shopping',        'icon': '🛍️', 'color': '#EC4899'},
    {'key': 'utilities',     'label': 'Utilities',       'icon': '💡', 'color': '#2DD4BF'},
    {'key': 'health',        'label': 'Health',          'icon': '💊', 'color': '#10B981'},
    {'key': 'entertainment', 'label': 'Entertainment',   'icon': '🎮', 'color': '#8B5CF6'},
    {'key': 'savings',       'label': 'Savings',         'icon': '💰', 'color': '#1A2B47'},
    {'key': 'education',     'label': 'Education',       'icon': '📚', 'color': '#3B82F6'},
    {'key': 'other',         'label': 'Other',           'icon': '📦', 'color': '#94A3B8'},
]

for c in categories:
    Category.objects.create(**c)

print(f"  ✅ {len(categories)} categories created")

# ── Test User ─────────────────────────────────────────────
User.objects.filter(username='testuser').delete()

user = User.objects.create_user(
    username='testuser',
    email='user@gmail.com',
    password='user123',
    first_name='User Name',
)

# Manually ensure profile exists (in case signal didn't fire)
profile, _ = UserProfile.objects.get_or_create(user=user)
profile.income_type      = 'salary'
profile.income_cycle     = 'monthly'
profile.income_amount    = Decimal('18000')
profile.next_income_date = date(2025, 7, 1)
profile.savings_goal     = Decimal('5000')
profile.currency         = 'PHP'
profile.save()

print("  ✅ Test user created → email: user@gmail.com | password: user123")

# ── ML Insight ────────────────────────────────────────────
MLInsight.objects.filter(user=user).delete()
MLInsight.objects.create(
    user=user,
    user_cluster='Balanced',
    cluster_description='You balance spending and saving well across categories.',
    daily_burn_rate=Decimal('388.57'),
    days_remaining=14,
    risk_level='caution',
    model_accuracy=94.2,
    prediction='Funds will likely last until end of cycle with moderate spending.',
    recommendations=[
        'Reduce shopping expenses by ₱500 this week.',
        'Your food spending is above average — consider home cooking.',
        'You are on track with savings — keep it up!',
    ],
    weekly_trend=[
        {'day': 'Mon', 'amount': 275},
        {'day': 'Tue', 'amount': 420},
        {'day': 'Wed', 'amount': 180},
        {'day': 'Thu', 'amount': 650},
        {'day': 'Fri', 'amount': 390},
        {'day': 'Sat', 'amount': 820},
        {'day': 'Sun', 'amount': 210},
    ],
)

print("  ✅ ML insight created")

# ── Sample Expenses ───────────────────────────────────────
Expense.objects.filter(user=user).delete()

food          = Category.objects.get(key='food')
transport     = Category.objects.get(key='transport')
shopping      = Category.objects.get(key='shopping')
utilities     = Category.objects.get(key='utilities')
health        = Category.objects.get(key='health')
entertainment = Category.objects.get(key='entertainment')
savings_cat   = Category.objects.get(key='savings')

sample_expenses = [
    {'description': 'Jollibee',        'category': food,          'amount': 180,  'timestamp': '2025-06-10 12:00:00'},
    {'description': 'Grab Ride',       'category': transport,     'amount': 95,   'timestamp': '2025-06-10 08:30:00'},
    {'description': 'SM Shopping',     'category': shopping,      'amount': 1200, 'timestamp': '2025-06-09 15:00:00'},
    {'description': 'Meralco Bill',    'category': utilities,     'amount': 850,  'timestamp': '2025-06-09 09:00:00'},
    {'description': 'Mercury Drug',    'category': health,        'amount': 320,  'timestamp': '2025-06-08 11:00:00'},
    {'description': 'Netflix',         'category': entertainment, 'amount': 149,  'timestamp': '2025-06-08 20:00:00'},
    {'description': "McDonald's",      'category': food,          'amount': 220,  'timestamp': '2025-06-07 13:00:00'},
    {'description': 'Jeepney Fare',    'category': transport,     'amount': 30,   'timestamp': '2025-06-07 07:30:00'},
    {'description': 'Shopee Order',    'category': shopping,      'amount': 560,  'timestamp': '2025-06-06 16:00:00'},
    {'description': 'Savings Deposit', 'category': savings_cat,   'amount': 1500, 'timestamp': '2025-06-06 10:00:00'},
]

for e in sample_expenses:
    Expense.objects.create(user=user, **e)

print(f"  ✅ {len(sample_expenses)} sample expenses created")

# ── Savings Goals ─────────────────────────────────────────
SavingsGoal.objects.filter(user=user).delete()

goals = [
    {'name': 'Emergency Fund', 'target_amount': 10000, 'current_amount': 4500, 'deadline': date(2025, 12, 31)},
    {'name': 'New Laptop',     'target_amount': 35000, 'current_amount': 8200, 'deadline': date(2025, 12, 31)},
    {'name': 'Vacation Fund',  'target_amount': 20000, 'current_amount': 2000, 'deadline': date(2025, 12, 31)},
]

for g in goals:
    SavingsGoal.objects.create(user=user, **g)

print(f"  ✅ {len(goals)} savings goals created")

# ── Sample Alerts ─────────────────────────────────────────
Alert.objects.filter(user=user).delete()

alerts = [
    {'type': 'warning',  'title': 'Food Spending', 'message': "You've spent 40% more on food this week"},
    {'type': 'critical', 'title': 'Budget Risk',   'message': 'At current rate, funds may run out in 10 days'},
    {'type': 'success',  'title': 'Savings Goal',  'message': "You're on track to meet your savings goal"},
    {'type': 'info',     'title': 'Smart Tip',     'message': 'Reducing transport costs could save ₱600/month'},
]

for a in alerts:
    Alert.objects.create(user=user, **a)

print(f"  ✅ {len(alerts)} alerts created")

# ── Admin User ────────────────────────────────────────────
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@spendwise.com',
        password='admin123',
    )
    print("  ✅ Admin created → username: admin | password: admin123")
else:
    print("  ℹ️  Admin already exists")

print("\n🎉 Seeding complete!")