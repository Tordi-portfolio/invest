from django.urls import path
from . import views
from .views import scrape_quotes

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('base', views.base, name='base'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('view_plan/<str:pk>', views.view_plan, name='view_plan'),

    path('forgot-password/', views.ForgotPassword, name='forgot-password'),
    path('password-reset-sent/<str:reset_id>/', views.PasswordResetSent, name='password-reset-sent'),
    path('reset-password/<str:reset_id>/', views.ResetPassword, name='reset-password'),

    path('quotes/', views.scrape_quotes, name='scrape_quotes'),
]