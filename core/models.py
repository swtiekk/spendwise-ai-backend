from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    INCOME_TYPE_CHOICES = [
        ('salary',    'Salary'),
        ('allowance', 'Allowance'),
        ('freelance', 'Freelance'),
        ('other',     'Other'),
    ]
    INCOME_CYCLE_CHOICES = [
        ('weekly',   'Weekly'),
        ('biweekly', 'Bi-weekly'),
        ('monthly',  'Monthly'),
    ]

    user                    = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    income_type             = models.CharField(max_length=20, choices=INCOME_TYPE_CHOICES, default='salary')
    income_cycle            = models.CharField(max_length=20, choices=INCOME_CYCLE_CHOICES, default='monthly')
    income_amount           = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    next_income_date        = models.DateField(null=True, blank=True)
    savings_goal            = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notifications_enabled   = models.BooleanField(default=True)
    dark_mode               = models.BooleanField(default=False)
    currency                = models.CharField(max_length=10, default='PHP')
    language                = models.CharField(max_length=10, default='en')
    budget_alert_threshold  = models.IntegerField(default=80)
    push_notifications      = models.BooleanField(default=True)
    email_notifications     = models.BooleanField(default=True)
    budget_alerts           = models.BooleanField(default=True)
    weekly_reports          = models.BooleanField(default=True)
    spending_reminders      = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username}'s profile"


class Category(models.Model):
    CATEGORY_CHOICES = [
        ('food',          'Food & Dining'),
        ('transport',     'Transport'),
        ('entertainment', 'Entertainment'),
        ('utilities',     'Utilities'),
        ('shopping',      'Shopping'),
        ('health',        'Health'),
        ('education',     'Education'),
        ('savings',       'Savings'),
        ('other',         'Other'),
    ]
    key   = models.CharField(max_length=20, choices=CATEGORY_CHOICES, unique=True)
    label = models.CharField(max_length=50)
    icon  = models.CharField(max_length=10)
    color = models.CharField(max_length=10)

    def __str__(self):
        return self.label


class Expense(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    amount      = models.DecimalField(max_digits=10, decimal_places=2)
    category    = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True)
    timestamp   = models.DateTimeField()
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} - ₱{self.amount}"


class Income(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incomes')
    amount     = models.DecimalField(max_digits=10, decimal_places=2)
    source     = models.CharField(max_length=100)
    date       = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - ₱{self.amount} from {self.source}"


class SavingsGoal(models.Model):
    user           = models.ForeignKey(User, on_delete=models.CASCADE, related_name='savings_goals')
    name           = models.CharField(max_length=100)
    target_amount  = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deadline       = models.DateField(null=True, blank=True)
    category       = models.CharField(max_length=50, blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.name}"


class Alert(models.Model):
    ALERT_TYPES = [
        ('warning',  'Warning'),
        ('critical', 'Critical'),
        ('success',  'Success'),
        ('info',     'Info'),
    ]
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alerts')
    type       = models.CharField(max_length=20, choices=ALERT_TYPES)
    title      = models.CharField(max_length=100)
    message    = models.TextField()
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class MLInsight(models.Model):
    CLUSTER_CHOICES = [
        ('Frugal',    'Frugal'),
        ('Balanced',  'Balanced'),
        ('Impulsive', 'Impulsive'),
        ('High-Risk', 'High-Risk'),
    ]
    RISK_CHOICES = [
        ('safe',    'Safe'),
        ('caution', 'Caution'),
        ('danger',  'Danger'),
    ]

    user                = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ml_insight')
    user_cluster        = models.CharField(max_length=20, choices=CLUSTER_CHOICES, default='Balanced')
    cluster_description = models.TextField(blank=True)
    daily_burn_rate     = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    days_remaining      = models.IntegerField(default=0)
    risk_level          = models.CharField(max_length=20, choices=RISK_CHOICES, default='safe')
    model_accuracy      = models.FloatField(default=0)
    prediction          = models.TextField(blank=True)
    recommendations     = models.JSONField(default=list)
    weekly_trend        = models.JSONField(default=list)
    last_updated        = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.user_cluster} - {self.risk_level}"


class SmartPurchaseLog(models.Model):
    DECISION_CHOICES = [
        ('safe',    'Safe'),
        ('caution', 'Caution'),
        ('risky',   'Risky'),
    ]
    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='smart_purchases')
    amount      = models.DecimalField(max_digits=10, decimal_places=2)
    category    = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    decision    = models.CharField(max_length=20, choices=DECISION_CHOICES)
    risk_score  = models.IntegerField()
    reasoning   = models.TextField()
    suggestions = models.JSONField(default=list)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - ₱{self.amount} - {self.decision}"


# ── Signals ───────────────────────────────────────────────
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
        MLInsight.objects.get_or_create(user=instance)