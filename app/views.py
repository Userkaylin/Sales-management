from django.shortcuts import render,redirect
from . models import *
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
import stripe
from django.shortcuts import get_object_or_404
from django.conf import settings
# Create your views here.

@login_required(login_url='/login/')
def home(request):
    user = CustomUser.objects.get(id=request.user.id)
    
    # Check user role
    if user.role == 'worker':
        total_sales = Sales.all_time_sales(user.outlet)
        total_purchase = Purchase.all_time_purchases(user.outlet)
        sales = Sales.objects.filter(outlet=user.outlet)
        purchases = Purchase.objects.filter(outlet=user.outlet)
        today_net_profit = Sales.today_net_profit(user.outlet)
        weekly_net_profit = Sales.weekly_net_profit(user.outlet)
        monthly_net_profit = Sales.monthly_net_profit(user.outlet)

        context = {
            'user': user,
            'sales': sales,
            'total_sales': total_sales,
            'total_purchase': total_purchase,
            'purchases': purchases,
            'today_net_profit': today_net_profit,
            'weekly_net_profit': weekly_net_profit,
            'monthly_net_profit': monthly_net_profit,
        }
        return render(request, 'dashboard.html', context)
    else:
        # Redirect to another dashboard for non-worker users
        return redirect('management_dashboard')
@login_required(login_url='/login/')
def management_dashboard(request):
    # Get aggregated data using the model methods
    total_sales_sum = Sales.sum_all_sales()
    total_purchases_sum = Purchase.sum_all_purchases()
    total_workers_count = CustomUser.total_workers()
    total_outlets_count = Outlet.total_outlets()

    # Get net profit data
    today_net_profit = Sales.super_net_profit_today()
    weekly_net_profit = Sales.super_net_profit_this_week()
    monthly_net_profit = Sales.super_net_profit_this_month()

    # Get sales percentage data
    sales_percentage = Sales.cost_analysis_percentage()

    # Create context to pass to the template
    context = {
        'total_sales_sum': total_sales_sum,
        'total_purchases_sum': total_purchases_sum,
        'total_workers_count': total_workers_count,
        'total_outlets_count': total_outlets_count,
        'sales_percentage': sales_percentage,
        'today_net_profit': today_net_profit,
        'weekly_net_profit': weekly_net_profit,
        'monthly_net_profit': monthly_net_profit,
    }

    return render(request, 'super_dashboard.html', context)



def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            
            
            return redirect("home")  
        else:
            messages.error(request, "Invalid username or password")
    
    return render(request, "login.html")
def signup(request):
    if request.method == "POST":
        # Get form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        outlet_id = request.POST.get('outlet')
        profile_photo = request.FILES.get('profile_photo')
        print(profile_photo)
        # Create new user
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            profile_picture = profile_photo,
            role = 'worker'
        )

        
        
        # Save the selected outlet
        if outlet_id:
            outlet = Outlet.objects.get(id=outlet_id)
            user.outlet = outlet
        
        # Save the user instance with profile photo and outlet
        user.save()


        # Redirect to a success page or dashboard
        return redirect('login')  # Replace 'home' with your desired redirect URL name

    else:
        # GET request: Display the form with outlets
        outlets = Outlet.objects.all()
        context = {
            'outlets': outlets
        }
        return render(request, 'signup.html', context)
    
def custom_logout(request):
    """Logs out the user and redirects to the home page."""
    logout(request)
    return redirect('/login/')  # Redirect to home or any other URL
@login_required(login_url='/login/')
def add_sale(request):
    outlets = Outlet.objects.all()
    user = CustomUser.objects.get(id=request.user.id)
    
    
    if request.method == 'POST':
        # Handle form submission
        outlet = request.POST.get('outlet')
        date = request.POST.get('date')
        total_sales = request.POST.get('total_sales')
        
        
        # Save the new Sale object
        Sales.objects.create(
            outlet=user.outlet,
            date=date,
            total_sales=total_sales,
            recorded_by=user
        )
        return redirect('/')  # Redirect after successful form submission
    
    return render(request, 'add_sale.html')
@login_required(login_url='/login/')
def add_purchase(request):
    user = CustomUser.objects.get(id=request.user.id)
    
    if request.method == 'POST':
        # Handle form submission
        date = request.POST.get('date')
        total_purchases = request.POST.get('total_purchases')
        
        # Save the new Purchase object
        Purchase.objects.create(
            outlet=user.outlet,
            date=date,
            total_purchases=total_purchases,
            recorded_by=user
        )
        return redirect('/')  # Redirect after successful form submission
    
    return render(request, 'add_purchase.html')
@login_required(login_url='/login/')
def sales_data(request):
    user = CustomUser.objects.get(id=request.user.id)

    
    today_sales = Sales.today_sales(user.outlet)

    
    weekly_sales = Sales.weekly_sales(user.outlet)

    monthly_sales = Sales.monthly_sales(user.outlet)
    print(today_sales,weekly_sales,monthly_sales)
    # Calculate sales by the current user
    user_sales = Sales.total_sales_by_user(user.outlet,user)
   
    sales = Sales.objects.filter(outlet=user.outlet)

    context = {
        'today_sales': today_sales,
        'weekly_sales': weekly_sales,
        'monthly_sales': monthly_sales,
        'user_sales': user_sales,
        'sales': sales,
    }

    return render(request, 'sales_data.html', context)
@login_required(login_url='/login/')
def super_sales_data(request):
    
    
    # Get sales data using the existing model methods
    today_sales = Sales.super_net_profit_today()  # Assuming this is a method that gives today's sales
    weekly_sales = Sales.super_net_profit_this_week()  # Assuming this is a method that gives weekly sales
    monthly_sales = Sales.super_net_profit_this_month()  # Assuming this is a method that gives monthly sales
    
    

    # Get all sales for the outlet
    sales = Sales.objects.all()
    
    context = {
        'today_sales': today_sales,
        'weekly_sales': weekly_sales,
        'monthly_sales': monthly_sales,
        
        'sales': sales,
    }
    
    return render(request, 'super_sales_data.html', context)
@login_required(login_url='/login/')
def purchase_overview(request):
    outlet = Outlet.objects.first()  # Modify this to get the desired outlet
    user = request.user
    
    # Calculate purchase stats
    today_purchases = Purchase.today_purchases(outlet)
    weekly_purchases = Purchase.weekly_purchases(outlet)
    monthly_purchases = Purchase.monthly_purchases(outlet)
    total_purchases_by_user = Purchase.total_purchases_by_user(outlet, user)
    
    # Fetch all purchases
    purchases = Purchase.objects.filter(outlet=outlet).order_by('-date')
    
    context = {
        'today_purchases': today_purchases,
        'weekly_purchases': weekly_purchases,
        'monthly_purchases': monthly_purchases,
        'total_purchases_by_user': total_purchases_by_user,
        'purchases': purchases
    }
    
    return render(request, 'purchase_overview.html', context)
@login_required(login_url='/login/')
def super_purchase_data(request):
    
    # Get purchase data using the model methods
    today_purchases = Purchase.super_today_purchases()
    weekly_purchases = Purchase.super_weekly_purchases()
    monthly_purchases = Purchase.super_monthly_purchases()
    
    
    # Get all purchases recorded by the user
    purchases = Purchase.objects.all()
    
    context = {
        'today_purchases': today_purchases,
        'weekly_purchases': weekly_purchases,
        'monthly_purchases': monthly_purchases,
        'purchases': purchases,
    }
    
    return render(request, 'super_purchase_data.html', context)
@login_required(login_url='/login/')
def analysis_report_view(request):
    user = CustomUser.objects.get(id=request.user.id)
    outlet = user.outlet
    today_net_profit = Sales.today_net_profit(outlet)
    weekly_net_profit = Sales.weekly_net_profit(outlet)
    monthly_net_profit = Sales.monthly_net_profit(outlet)
    # today_margin = Sales.today_gross_profit_margin(outlet)
    # Pass these values to your template context
    return render(request, 'analysis_report.html', {
        'today_net_profit': today_net_profit,
        'weekly_net_profit': weekly_net_profit,
        'monthly_net_profit': monthly_net_profit,
        # 'today_margin': today_margin,
        # Add other values as needed
    })
@login_required(login_url='/login/')
def workers_list(request):
    workers = CustomUser.objects.filter(role='worker')
    
    context = {
        'workers': workers,
    }
    
    return render(request, 'workers_list.html', context)
@login_required(login_url='/login/')
def outlets_list(request):
    outlets = Outlet.objects.all()
    
    context = {
        'outlets': outlets,
    }
    
    return render(request, 'outlets_list.html', context)
@login_required(login_url='/login/')
def add_outlet(request):
    if request.method == 'POST':
        # Retrieve form data using request.POST.get()
        name = request.POST.get('name')
        location = request.POST.get('location')
        manager_name = request.POST.get('manager_name')
        
        # Basic validation (You can add more validation as needed)
        if name and location and manager_name:
            # Create a new Outlet instance and save it
            Outlet.objects.create(
                name=name,
                location=location,
                manager_name=manager_name
            )
            messages.success(request, 'Outlet added successfully!')
            return redirect('outlets-list')  # Redirect to a list view or another page
        else:
            messages.error(request, 'Please fill out all fields.')
    
    return render(request, 'add-outlet.html')



