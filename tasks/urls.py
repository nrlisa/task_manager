# tasks/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # This maps to the functions you wrote in tasks/views.py
    path('', views.task_list, name='task_list'),
    path('create/', views.create_task, name='create_task'),
    path('edit/<int:pk>/', views.edit_task, name='edit_task'),
    path('delete/<int:pk>/', views.delete_task, name='delete_task'),
    path('admin-dashboard/', views.admin_task_list, name='admin_task_list'),
    path('audit-logs/', views.admin_audit_log, name='admin_audit_log'),
]