from decimal import Decimal
from django.contrib.auth.models import User
from django.db.models import Sum
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Alert, Category, Expense, Income, MLInsight, SavingsGoal, SmartPurchaseLog, UserProfile
from .serializers import (
    AlertSerializer, CategorySerializer, ExpenseSerializer, IncomeSerializer,
    MLInsightSerializer, RegisterSerializer, SavingsGoalSerializer,
    SmartPurchaseSerializer, UserProfileSerializer, UserSerializer,
)


# ── Auth ──────────────────────────────────────────────────────────────────────

class RegisterView(generics.CreateAPIView):
    queryset            = User.objects.all()
    serializer_class    = RegisterSerializer
    permission_classes  = [permissions.AllowAny]


@api_view(['GET'])
def current_user_view(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


# ── Profile ───────────────────────────────────────────────────────────────────

@api_view(['GET', 'PATCH'])
def profile_view(request):
    profile = request.user.profile
    if request.method == 'GET':
        return Response(UserProfileSerializer(profile).data)
    serializer = UserProfileSerializer(profile, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)


# ── Categories ────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def categories_view(request):
    categories = Category.objects.all()
    return Response(CategorySerializer(categories, many=True).data)


# ── Expenses ──────────────────────────────────────────────────────────────────

class ExpenseListCreateView(generics.ListCreateAPIView):
    serializer_class = ExpenseSerializer

    def get_queryset(self):
        qs = Expense.objects.filter(user=self.request.user)
        start = self.request.query_params.get('start_date')
        end   = self.request.query_params.get('end_date')
        cat   = self.request.query_params.get('category')
        if start: qs = qs.filter(timestamp__date__gte=start)
        if end:   qs = qs.filter(timestamp__date__lte=end)
        if cat:   qs = qs.filter(category__key=cat)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ExpenseDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ExpenseSerializer

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)


# ── Income ────────────────────────────────────────────────────────────────────

class IncomeListCreateView(generics.ListCreateAPIView):
    serializer_class = IncomeSerializer

    def get_queryset(self):
        return Income.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ── Dashboard ─────────────────────────────────────────────────────────────────

@api_view(['GET'])
def dashboard_view(request):
    user     = request.user
    expenses = Expense.objects.filter(user=user)
    incomes  = Income.objects.filter(user=user)
    profile  = user.profile

    total_expenses = expenses.aggregate(t=Sum('amount'))['t'] or Decimal('0')
    total_income   = incomes.aggregate(t=Sum('amount'))['t'] or Decimal(str(profile.income_amount))
    balance        = total_income - total_expenses

    # Category breakdown
    breakdown = {}
    for exp in expenses:
        key = exp.category.key if exp.category else 'other'
        breakdown[key] = float(breakdown.get(key, 0)) + float(exp.amount)

    return Response({
        'balance':            float(balance),
        'total_expenses':     float(total_expenses),
        'total_income':       float(total_income),
        'average_daily_spend': float(total_expenses) / 30,
        'savings_goal':       float(profile.savings_goal),
        'category_breakdown': breakdown,
    })


# ── Expense Stats ─────────────────────────────────────────────────────────────

@api_view(['GET'])
def expense_stats_view(request):
    user     = request.user
    expenses = Expense.objects.filter(user=user)
    profile  = user.profile

    total    = expenses.aggregate(t=Sum('amount'))['t'] or Decimal('0')
    income   = Decimal(str(profile.income_amount))
    balance  = income - total
    breakdown = {}
    for exp in expenses:
        key = exp.category.key if exp.category else 'other'
        breakdown[key] = float(breakdown.get(key, 0)) + float(exp.amount)

    return Response({
        'total_expenses':      float(total),
        'total_income':        float(income),
        'balance':             float(balance),
        'average_daily_spend': float(total) / 30,
        'days_remaining':      14,
        'category_breakdown':  breakdown,
    })


# ── Savings Goals ─────────────────────────────────────────────────────────────

class SavingsGoalListCreateView(generics.ListCreateAPIView):
    serializer_class = SavingsGoalSerializer

    def get_queryset(self):
        return SavingsGoal.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SavingsGoalDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SavingsGoalSerializer

    def get_queryset(self):
        return SavingsGoal.objects.filter(user=self.request.user)


# ── Alerts ────────────────────────────────────────────────────────────────────

@api_view(['GET'])
def alerts_view(request):
    alerts = Alert.objects.filter(user=request.user)
    return Response(AlertSerializer(alerts, many=True).data)


@api_view(['PATCH'])
def mark_alert_read(request, pk):
    try:
        alert = Alert.objects.get(pk=pk, user=request.user)
        alert.is_read = True
        alert.save()
        return Response({'status': 'marked as read'})
    except Alert.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)


# ── ML Insights ───────────────────────────────────────────────────────────────

@api_view(['GET'])
def insights_view(request):
    insight, _ = MLInsight.objects.get_or_create(user=request.user)
    return Response(MLInsightSerializer(insight).data)


# ── Smart Purchase ────────────────────────────────────────────────────────────

@api_view(['POST'])
def smart_purchase_view(request):
    amount      = Decimal(str(request.data.get('amount', 0)))
    category    = request.data.get('category', 'other')
    description = request.data.get('description', '')

    # Risk logic (mirrors your insightsService.ts)
    if amount < 1500:
        decision   = 'safe'
        risk_score = int(amount / 1500 * 30)
        reasoning  = f"₱{amount:,.2f} is within your safe spending range."
        suggestions = ['You can proceed.', 'Log it immediately after buying.']
    elif amount < 3000:
        decision   = 'caution'
        risk_score = int(30 + (amount - 1500) / 1500 * 40)
        reasoning  = f"₱{amount:,.2f} is manageable but will reduce your remaining budget significantly."
        suggestions = ['Only proceed if this is a priority.', 'Look for a lower-cost alternative.']
    else:
        decision   = 'risky'
        risk_score = min(100, int(70 + (amount - 3000) / 1000 * 10))
        reasoning  = f"₱{amount:,.2f} exceeds safe spending limits based on your current balance."
        suggestions = ['Defer until next pay cycle.', 'Review your spending breakdown first.']

    profile = request.user.profile
    income  = Decimal(str(profile.income_amount))
    expenses_total = Expense.objects.filter(user=request.user).aggregate(t=Sum('amount'))['t'] or Decimal('0')
    balance = income - expenses_total

    log = SmartPurchaseLog.objects.create(
        user=request.user,
        amount=amount,
        category=category,
        description=description,
        decision=decision,
        risk_score=risk_score,
        reasoning=reasoning,
        suggestions=suggestions,
    )

    return Response({
        'decision':                   decision,
        'risk_score':                 risk_score,
        'reasoning':                  reasoning,
        'suggestions':                suggestions,
        'current_balance':            float(balance),
        'remaining_budget':           float(balance - amount),
        'estimated_days_until_shortfall': 3 if decision == 'risky' else None,
    })


# ── Admin-only views ──────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def admin_users_view(request):
    users = User.objects.all().select_related('profile', 'ml_insight')
    data  = []
    for u in users:
        profile = getattr(u, 'profile', None)
        insight = getattr(u, 'ml_insight', None)
        data.append({
            'id':           u.id,
            'name':         u.get_full_name() or u.username,
            'email':        u.email,
            'income_type':  profile.income_type  if profile else None,
            'income_cycle': profile.income_cycle if profile else None,
            'cluster':      insight.user_cluster  if insight else None,
            'risk_level':   insight.risk_level    if insight else None,
            'date_joined':  u.date_joined,
        })
    return Response(data)


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def admin_dashboard_view(request):
    total_users    = User.objects.count()
    total_expenses = Expense.objects.aggregate(t=Sum('amount'))['t'] or 0
    cluster_counts = {}
    for insight in MLInsight.objects.all():
        cluster_counts[insight.user_cluster] = cluster_counts.get(insight.user_cluster, 0) + 1

    return Response({
        'total_users':    total_users,
        'total_expenses': float(total_expenses),
        'cluster_distribution': cluster_counts,
    })