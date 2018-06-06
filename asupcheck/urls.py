from django.urls import path
from asupcheck import views

urlpatterns = [
        path('thanks2', views.thanks2, name='thanks2'),
        path('dashboard/', views.dashboard, name='dashboard'),
        path('dashboard2/', views.dashboard2, name='dashboard2'),
        path('asupcheck/', views.asupcheckv1view, name='asupcheck'), ]
