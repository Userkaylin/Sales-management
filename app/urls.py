
from django.urls import path
from . import views
urlpatterns = [
    path('',views.home,name='home'),
    path('login/',views.login,name='login'),
    path('signup/',views.signup,name='signup'),
    path('add-sale/', views.add_sale, name='add_sale'),
    path('add-purchase/', views.add_purchase, name='add_purchase'),
    path('sales-data/', views.sales_data, name='sales_data'),
    path('super-sales-data/', views.super_sales_data, name='super_sales_data'),
    path('purchase-overview/', views.purchase_overview, name='purchase_overview'),
    path('analysis-report/', views.analysis_report_view, name='analysis_report'),
    path('management-dashboard/', views.management_dashboard, name='management_dashboard'),
    path('super_purchase-data/', views.super_purchase_data, name='super_purchase_data'),
    path('workers/', views.workers_list, name='workers-list'),
    path('outlets/', views.outlets_list, name='outlets-list'),
    path('add-outlet/', views.add_outlet, name='add-outlet'),
    path('logout/', views.custom_logout, name='logout'),
]