from django.urls import path

from . import views

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('reports/', views.ReportListView.as_view(), name='report_list'),
    path('new/', views.ReportCreateView.as_view(), name='report_new'),
    path('<int:pk>/edit/',
         views.ReportUpdateView.as_view(), name='report_edit'),
    path('<int:pk>/',
         views.ReportDetailView.as_view(), name='report_detail'),
    path('<int:pk>/delete/',
         views.ReportDeleteView.as_view(), name='report_delete'),
]
