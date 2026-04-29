from django.urls import path
from .views import SignUpView, CustomLogoutView, profile_view, dashboard_view, bypass_login_view

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('profile/', profile_view, name='profile'),
    path('login/', bypass_login_view, name='login'),
]
