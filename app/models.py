from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum
class Outlet(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200, blank=True, null=True)
    manager_name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name
    @staticmethod
    def total_outlets():
        return Outlet.objects.count()

class CustomUser(AbstractUser):
    USER_ROLES = (
        ('worker', 'Worker'),
        ('management', 'Management'),
    )

    role = models.CharField(max_length=10, choices=USER_ROLES)
    outlet = models.ForeignKey(Outlet, on_delete=models.SET_NULL, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    def __str__(self):
        return f'{self.username} - {self.role}'
    @staticmethod
    def total_workers():
        return CustomUser.objects.filter(role='worker').count()
class Sales(models.Model):
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE)
    date = models.DateField()
    total_sales = models.DecimalField(max_digits=10, decimal_places=2)
    recorded_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'Sales on {self.date} - {self.outlet.name}'
    @staticmethod
    def cost_analysis_percentage():
        # Calculate the total sales across all outlets
        total_sales_all_outlets = Sales.objects.aggregate(total=Sum('total_sales'))['total'] or 0
        
        if total_sales_all_outlets == 0:
            # Handle the case where total sales are zero to avoid division by zero
            return {}
        
        # Get sales grouped by outlet
        sales_by_outlet = Sales.objects.values('outlet').annotate(total=Sum('total_sales'))
        
        # Calculate the percentage of total sales for each outlet
        outlet_sales_percentage = {}
        for sales in sales_by_outlet:
            outlet_id = sales['outlet']
            outlet_sales = sales['total']
            percentage = (outlet_sales / total_sales_all_outlets) * 100
            outlet_sales_percentage[outlet_id] = percentage
        
        return outlet_sales_percentage
    @staticmethod
    def sum_all_sales():
        total_sales = Sales.objects.aggregate(total=Sum('total_sales'))['total'] or 0
        return total_sales
    # Today's sales of an outlet
    @staticmethod
    def today_sales(outlet):
        today = timezone.now().date()
        return Sales.objects.filter(outlet=outlet, date=today).aggregate(total=models.Sum('total_sales'))['total'] or 0

    # Weekly sales of an outlet
    @staticmethod
    def weekly_sales(outlet):
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())  # Monday as the start of the week
        return Sales.objects.filter(outlet=outlet, date__gte=start_of_week, date__lte=today).aggregate(total=models.Sum('total_sales'))['total'] or 0

    # Monthly sales of an outlet
    @staticmethod
    def monthly_sales(outlet):
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        return Sales.objects.filter(outlet=outlet, date__gte=start_of_month, date__lte=today).aggregate(total=models.Sum('total_sales'))['total'] or 0

    # Total sales of an outlet recorded by a specific user
    @staticmethod
    def total_sales_by_user(outlet, user):
        return Sales.objects.filter(outlet=outlet, recorded_by=user).aggregate(total=models.Sum('total_sales'))['total'] or 0

    # Sum of all-time sales for an outlet
    @staticmethod
    def all_time_sales(outlet):
        return Sales.objects.filter(outlet=outlet).aggregate(total=models.Sum('total_sales'))['total'] or 0
    @staticmethod
    def calculate_net_profit(outlet, start_date=None, end_date=None):
        # Calculate sales
        sales_total = Sales.objects.filter(outlet=outlet, date__range=(start_date, end_date)).aggregate(total=Sum('total_sales'))['total'] or 0
        # Calculate purchases
        purchases_total = Purchase.objects.filter(outlet=outlet, date__range=(start_date, end_date)).aggregate(total=Sum('total_purchases'))['total'] or 0
        # Net profit
        return sales_total - purchases_total

    @staticmethod
    def today_net_profit(outlet):
        today = timezone.now().date()
        return Sales.calculate_net_profit(outlet, start_date=today, end_date=today)

    @staticmethod
    def weekly_net_profit(outlet):
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        return Sales.calculate_net_profit(outlet, start_date=start_of_week, end_date=today)

    @staticmethod
    def monthly_net_profit(outlet):
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        return Sales.calculate_net_profit(outlet, start_date=start_of_month, end_date=today)
    
    @staticmethod
    def super_net_profit_today():
        today = timezone.now().date()
        return Sales.objects.filter(date=today).aggregate(total=Sum('total_sales'))['total'] or 0

    @staticmethod
    def super_net_profit_this_week():
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        return Sales.objects.filter(date__gte=start_of_week, date__lte=today).aggregate(total=Sum('total_sales'))['total'] or 0

    @staticmethod
    def super_net_profit_this_month():
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        return Sales.objects.filter(date__gte=start_of_month, date__lte=today).aggregate(total=Sum('total_sales'))['total'] or 0
class Purchase(models.Model):
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE)
    date = models.DateField()
    total_purchases = models.DecimalField(max_digits=10, decimal_places=2)
    recorded_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'Purchase on {self.date} - {self.outlet.name}'
    
    @staticmethod
    def super_today_purchases():
        today = timezone.now().date()
        return Purchase.objects.filter(date=today).aggregate(total=Sum('total_purchases'))['total'] or 0

    @staticmethod
    def super_weekly_purchases():
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        return Purchase.objects.filter(date__gte=start_of_week, date__lte=today).aggregate(total=Sum('total_purchases'))['total'] or 0

    @staticmethod
    def super_monthly_purchases():
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        return Purchase.objects.filter(date__gte=start_of_month, date__lte=today).aggregate(total=Sum('total_purchases'))['total'] or 0

    @staticmethod
    def total_purchases_by_user(user):
        return Purchase.objects.filter(recorded_by=user).aggregate(total=Sum('total_purchases'))['total'] or 0
    @staticmethod
    def sum_all_purchases():
        total_purchases = Purchase.objects.aggregate(total=Sum('total_purchases'))['total'] or 0
        return total_purchases
    # Today's purchases of an outlet
    @staticmethod
    def today_purchases(outlet):
        today = timezone.now().date()
        return Purchase.objects.filter(outlet=outlet, date=today).aggregate(total=models.Sum('total_purchases'))['total'] or 0

    # Weekly purchases of an outlet
    @staticmethod
    def weekly_purchases(outlet):
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())  # Monday as the start of the week
        return Purchase.objects.filter(outlet=outlet, date__gte=start_of_week, date__lte=today).aggregate(total=models.Sum('total_purchases'))['total'] or 0

    # Monthly purchases of an outlet
    @staticmethod
    def monthly_purchases(outlet):
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        return Purchase.objects.filter(outlet=outlet, date__gte=start_of_month, date__lte=today).aggregate(total=models.Sum('total_purchases'))['total'] or 0

    # Total purchases of an outlet recorded by a specific user
    @staticmethod
    def total_purchases_by_user(outlet, user):
        return Purchase.objects.filter(outlet=outlet, recorded_by=user).aggregate(total=models.Sum('total_purchases'))['total'] or 0

    # Sum of all-time purchases for an outlet
    @staticmethod
    def all_time_purchases(outlet):
        return Purchase.objects.filter(outlet=outlet).aggregate(total=models.Sum('total_purchases'))['total'] or 0
class MonthlyReport(models.Model):
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE)
    month = models.DateField()
    total_sales = models.DecimalField(max_digits=15, decimal_places=2)
    total_purchases = models.DecimalField(max_digits=15, decimal_places=2)
    profit_or_loss = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f'Monthly Report for {self.outlet.name} - {self.month}'
class RevenueVsCost(models.Model):
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE)
    month = models.DateField()
    revenue = models.DecimalField(max_digits=15, decimal_places=2)
    cost = models.DecimalField(max_digits=15, decimal_places=2)
    net_profit = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f'Revenue vs Cost for {self.outlet.name} - {self.month}'
