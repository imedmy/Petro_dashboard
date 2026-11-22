# apps/users/urls.py
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.user_list_view, name='user_list'),
    path('create/', views.user_create_view, name='user_create'),
    path('edit/<int:user_id>/', views.user_edit_view, name='user_edit'),
    path('delete/<int:user_id>/', views.user_delete_view, name='user_delete'),
    path('permissions/', views.permission_management_view, name='permissions'),
    
    # APIs
    path('api/pages/', views.api_pages, name='api_pages'),
    path('api/save-permission/', views.api_save_permission, name='api_save_permission'),
    path('api/delete-permission/<int:perm_id>/', views.api_delete_permission, name='api_delete_permission'),
]