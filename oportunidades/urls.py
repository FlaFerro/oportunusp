from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import register, CustomLoginView, user_profile, opportunity_edit_updateView


urlpatterns = [
    path('', views.home, name='home'),
    path('opportunity/<int:pk>/', views.opportunity_detail, name='opportunity_detail'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', register, name='register'), 
    path('opportunity/', views.opportunity_list, name='opportunity_list'),
    path('meu-perfil/', user_profile, name='user_profile'),
    path('opportunity_edit/<int:pk>/', views.opportunity_edit_updateView.as_view(), name='opportunity_edit'),
    path('criar/', views.create_opportunity, name='create_opportunity'),
]
