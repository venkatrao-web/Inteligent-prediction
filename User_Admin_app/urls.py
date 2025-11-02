from django.urls import path
from . import views

urlpatterns = [
    # 🏠 Home Page
    path('', views.home_page, name='home_page'),

    # 👤 User Registration & Login
    path('register/', views.register_page, name='register_page'),
    path('login/', views.login_page, name='login_page'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),

    # 🚪 Logout
    path('logout/', views.logout_user, name='logout_user'),

    # 🧑‍💼 Admin Login & Dashboard
    path('admin_login/', views.admin_login, name='admin_login'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('approve_user/<int:user_id>/', views.approve_user, name='approve_user'),
    path('reject_user/<int:user_id>/', views.reject_user, name='reject_user'),
]
