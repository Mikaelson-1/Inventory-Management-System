from django.urls import path
from . import views

urlpatterns = [
    path('', views.item_list, name='item_list'),
    path('create/', views.item_create, name='item_create'),
    path('<int:item_id>/edit/', views.item_edit, name='item_edit'),
    path('<int:item_id>/delete/', views.item_delete, name='item_delete'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:cat_id>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:cat_id>/delete/', views.category_delete, name='category_delete'),
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/create/', views.supplier_create, name='supplier_create'),
    path('suppliers/<int:supplier_id>/edit/', views.supplier_edit, name='supplier_edit'),
    path('suppliers/<int:supplier_id>/delete/', views.supplier_delete, name='supplier_delete'),
    path('purchases/', views.purchase_list, name='purchase_list'),
    path('purchases/create/', views.purchase_create, name='purchase_create'),
    path('stockout/', views.stockout_list, name='stockout_list'),
    path('stockout/create/', views.stockout_create, name='stockout_create'),
    path('items/export/excel/', views.export_items_excel, name='export_items_excel'),
    path('request/', views.create_stock_request, name='create_stock_request'),
    path('requests/', views.review_requests_view, name='review_requests'),
    #path('requests/<int:request_id>/<str:status>/', views.update_request_status, name='update_request_status'),
    path('report/fancy/', views.fancy_report_view, name='fancy_report'),
    path('department/request/', views.request_item_view, name='request_item'),
    path('department/requests/', views.department_requests_view, name='department_requests'),
    path('requests/<int:pk>/approve/', views.approve_request, name='approve_request'),
    path('requests/<int:pk>/decline/', views.decline_request, name='decline_request'),


]
