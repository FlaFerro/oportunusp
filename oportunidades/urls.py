from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import register, CustomLoginView, user_profile


urlpatterns = [
    path('', views.home, name='home'),
    path('opportunity/<int:pk>/', views.opportunity_detail, name='opportunity_detail'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', register, name='register'), 
    path('opportunity/', views.opportunity_list, name='opportunity_list'),
    path('meu-perfil/', user_profile, name='user_profile'),
]
