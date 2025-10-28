from django.urls import path
from . import views
from .views import health

urlpatterns = [
    path('', views.upload_and_view, name='upload_and_view'),
    path('trade_list/', views.trade_list, name='trade_list'),
    path('toggle_trade_list/', views.toggle_trade_list, name='toggle_trade_list'),
    path('clear_all/', views.clear_all, name='clear_all'),
    path('remove_all_from_trade_list/', views.remove_all_from_trade_list, name='remove_all_from_trade_list'),
    path('create-admin/', views.temp_create_admin, name='temp_create_admin'),  # Temporary - remove after setup
    path('register/', views.register, name='register'),
    path('health/', health.health_check, name='health_check'),
]