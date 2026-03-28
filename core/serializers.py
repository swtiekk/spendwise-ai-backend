from django.contrib.auth.models import User
from rest_framework import serializers
from .models import (
    UserProfile, Category, Expense, Income,
    SavingsGoal, Alert, MLInsight, SmartPurchaseLog
)


class RegisterSerializer(serializers.ModelSerializer):
    password     = serializers.CharField(write_only=True)
    income_type  = serializers.CharField(write_only=True, required=False)
    income_cycle = serializers.CharField(write_only=True, required=False)

    class Meta:
        model  = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'income_type', 'income_cycle']

    def create(self, validated_data):
        income_type  = validated_data.pop('income_type',  'other')
        income_cycle = validated_data.pop('income_cycle', 'monthly')
        password     = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        # signal already created profile, so get_or_create instead of create
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.income_type  = income_type
        profile.income_cycle = income_cycle
        profile.save()
        MLInsight.objects.get_or_create(user=user)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = UserProfile
        fields = [
            'income_type', 'income_cycle', 'income_amount', 'next_income_date',
            'savings_goal', 'notifications_enabled', 'dark_mode', 'currency',
            'language', 'budget_alert_threshold', 'push_notifications',
            'email_notifications', 'budget_alerts', 'weekly_reports', 'spending_reminders',
        ]


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model  = User
        fields = ['id', 'username', 'email', 'first_name', 'profile']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Category
        fields = '__all__'


class ExpenseSerializer(serializers.ModelSerializer):
    category_key = serializers.CharField(write_only=True)
    category     = CategorySerializer(read_only=True)

    class Meta:
        model  = Expense
        fields = ['id', 'amount', 'category', 'category_key', 'description', 'timestamp', 'created_at', 'updated_at']

    def create(self, validated_data):
        category_key = validated_data.pop('category_key')
        category     = Category.objects.get(key=category_key)
        return Expense.objects.create(category=category, **validated_data)

    def update(self, instance, validated_data):
        category_key = validated_data.pop('category_key', None)
        if category_key:
            instance.category = Category.objects.get(key=category_key)
        return super().update(instance, validated_data)


class IncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Income
        fields = ['id', 'amount', 'source', 'date', 'created_at', 'updated_at']


class SavingsGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model  = SavingsGoal
        fields = ['id', 'name', 'target_amount', 'current_amount', 'deadline', 'category', 'created_at', 'updated_at']


class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Alert
        fields = ['id', 'type', 'title', 'message', 'is_read', 'created_at']


class MLInsightSerializer(serializers.ModelSerializer):
    class Meta:
        model  = MLInsight
        fields = [
            'user_cluster', 'cluster_description', 'daily_burn_rate',
            'days_remaining', 'risk_level', 'model_accuracy',
            'prediction', 'recommendations', 'weekly_trend', 'last_updated',
        ]


class SmartPurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model  = SmartPurchaseLog
        fields = ['id', 'amount', 'category', 'description', 'decision', 'risk_score', 'reasoning', 'suggestions', 'created_at']