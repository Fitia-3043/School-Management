from django.urls import path
from .views import SignUpView, CustomLogoutView, profile_view, dashboard_view

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('profile/', profile_view, name='profile'),
    path('dashboard/', dashboard_view, name='dashboard'),
]
