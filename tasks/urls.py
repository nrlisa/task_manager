# tasks/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # This maps to the functions you wrote in tasks/views.py
    path('', views.task_list, name='task_list'),
    path('create/', views.create_task, name='create_task'),
]