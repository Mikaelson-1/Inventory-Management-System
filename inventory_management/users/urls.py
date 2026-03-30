from django.urls import path
from . import views

from .views import (
    login_view, logout_view, dashboard,
    store_dashboard, department_dashboard, landing_page
    
)

urlpatterns = [
    path('', landing_page, name='landing_page'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('store/', store_dashboard, name='store_dashboard'),
    path('department/', department_dashboard, name='department_dashboard'),
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    path('logs/', views.activity_log, name='activity_log'),
    path('items/recycle-bin/', views.item_archive, name='item_archive'),
    path('items/<int:item_id>/restore/', views.item_restore, name='item_restore'),
    path('requests/review/', views.review_requests, name='review_requests'),
    path('requests/<int:request_id>/approve/', views.approve_request, name='approve_request'),
    path('requests/<int:request_id>/reject/', views.reject_request, name='reject_request'),

]