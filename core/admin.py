from django.contrib import admin
from .models import UserProfile, Category, Expense, Income, SavingsGoal, Alert, MLInsight, SmartPurchaseLog

admin.site.register(UserProfile)
admin.site.register(Category)
admin.site.register(Expense)
admin.site.register(Income)
admin.site.register(SavingsGoal)
admin.site.register(Alert)
admin.site.register(MLInsight)
admin.site.register(SmartPurchaseLog)