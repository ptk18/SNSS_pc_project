from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_form_view, name='login'),
    path('login_user/', views.login_user, name='login_user'),
    path('signup_form/', views.signup_form_view, name='signup_form'),
    path('signup_user/', views.signup_user, name='signup_user'),
    path('master/', views.master_data_view, name='master'),
    path('customer/', views.customer_order_view, name='customer'),
    path('templates/', views.templates_view, name= 'templates'),
    path('normal_template/', views.normal_template, name='normal_template'),
    path('special_template/', views.special_template, name='special_template'),
    path('get_normal_tems/', views.get_normal_templates, name='get_normal_tems'),
    path('get_special_tems/', views.get_special_templates, name='get_special_tems'),
    path('importOrder_form/', views.importOrder_form, name='importOrder_form'),
    path('get_all_template_names_IDs/', views.get_all_template_names_IDs, name='get_all_template_names_IDs'),
    path('delete_template/<int:template_id>/', views.delete_template, name='delete_template'),
    path('update_template/<int:template_id>/', views.update_template, name='update_template'),
    path('delete_special_template/<int:template_id>/', views.delete_special_template, name='delete_special_template'),
    path('update_special_template/<int:template_id>/', views.update_special_template, name='update_special_template'),
    path('handle_template_and_file/', views.handle_template_and_file, name='handle_template_and_file'),
    path('save_customer_orders/', views.save_customer_orders, name='save_customer_orders'),
    path('save_customer_orders_forecast/', views.save_customer_orders_forecast, name='save_customer_orders_forecast'),
    path('orderPlan_form/', views.orderPlan_form, name='orderPlan_form'),
    #path('get_customerOrder_frame/', views.get_customerOrder_frame, name='get_customerOrder_frame'),
    path('get_customerOrder_frame/<str:customerName>/', views.get_customerOrder_frame, name='get_customerOrder_frame'),
    path('master_customer_data/', views.master_customer_data, name='master_customer_data'),
    path('save_customer_data/', views.save_customer_data, name='save_customer_data'),
    path('get_all_customer_data/', views.get_all_customer_data, name='get_all_customer_data'),
    path('update_customer_data/<int:customer_id>/', views.update_customer_data, name='update_customer_data'),
    path('delete_customer_data/<int:customer_id>/', views.delete_customer_data, name='delete_customer_data'),
    path('get_all_customer_names/', views.get_all_customer_names, name='get_all_customer_names'),
    path('get_all_customerPartNumbers_master/<str:customerName>/', views.get_all_customer_Part_Numbers_master, name='get_all_customerPartNumbers_master'),
    path('get_nsk_group_customers_master/', views.get_nsk_group_customers_master, name='get_nsk_group_customers_master'),
    path('test_tt/', views.test_tt, name='test_tt'),
    path('stock_file_upload/', views.stock_file_upload, name='stock_file_upload'),
    path('save_stock_data/', views.save_stock_data, name='save_stock_data'),
    path('get_stockData_for_tdy/', views.get_stockData_for_tdy, name='get_stockData_for_tdy'),
]
# Serve static files during development
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)