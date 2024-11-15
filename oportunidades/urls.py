from django.urls import path
from . import views

urlpatterns = [
    path('', views.opportunity_list, name='opportunity_list'),
    path('opportunity/<int:pk>/', views.opportunity_detail, name='opportunity_detail'),
]
