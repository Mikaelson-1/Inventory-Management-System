from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from inventory.models import Item, StockOut, Supplier, Category, Purchase
from users.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import ActivityLog
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db import models
from django.db.models import F
from django.utils.timezone import now
from datetime import timedelta


def landing_page(request):
    return render(request, 'landing.html', {'user': request.user})

def login_view(request):
    if request.user.is_authenticated:
        return redirect_user_based_on_role(request.user)

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
    
        if user is not None:
            login(request, user)
            from inventory.views import log_activity
            log_activity(request.user, 'user_login', f"{user.username} Logged In ")
            return redirect_user_based_on_role(user)
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'users/login.html')


# 👇 Helper function for smart redirect
def redirect_user_based_on_role(user):
    if user.role == 'admin':
        return redirect('dashboard')
    elif user.role == 'store_officer':
        return redirect('store_dashboard')  # 👈 create this later
    elif user.role == 'department_user':
        return redirect('department_dashboard')  # 👈 create this later
    else:
        return redirect('login')  # fallback



def logout_view(request):
    logout(request)
    return redirect('login')


from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from datetime import timedelta
from django.db.models import F
from django.shortcuts import render
from django.http import HttpResponseForbidden
from inventory.models import Item, Category, Purchase, StockOut, Supplier
from users.models import User  # or get_user_model()

@login_required
def dashboard(request):
    user = request.user
    role = user.role  # 'admin', 'store_officer', 'department'

    notifications = []
    total_items = total_categories = total_purchases = total_issued = total_suppliers = total_users = 0

    if role in ['admin', 'store_officer']:
        total_items = Item.objects.filter(is_active=True).count()
        total_categories = Category.objects.count()
        total_purchases = Purchase.objects.count()
        total_issued = StockOut.objects.count()
        total_suppliers = Supplier.objects.filter(is_active=True).count()
        total_users = User.objects.filter(is_active=True).count()

        # 🔴 Danger: Out of Stock
        out_of_stock = Item.objects.filter(is_active=True, quantity_in_stock=0).count()
        if out_of_stock:
            notifications.append({
                "type": "danger",
                "message": f"{out_of_stock} item(s) are completely out of stock!"
            })

        # 🟡 Warning: Low Stock
        low_stock = Item.objects.filter(is_active=True, quantity_in_stock__lt=F('reorder_level')).count()
        if low_stock:
            notifications.append({
                "type": "warning",
                "message": f"{low_stock} item(s) are below reorder level."
            })

        # 🔵 Info: New suppliers this week
        this_week = now() - timedelta(days=7)
        new_suppliers = Supplier.objects.filter(is_active=True, created_at__gte=this_week).count()
        if new_suppliers:
            notifications.append({
                "type": "info",
                "message": f"{new_suppliers} new supplier(s) added in the last 7 days."
            })

        if not low_stock and not out_of_stock:
            notifications.append({
                "type": "success",
                "message": "All stock levels are okay 🎉"
            })

    elif role == 'department_user':
        # Customize this for department dashboard later
        notifications.append({
            "type": "info",
            "message": "Welcome to your department dashboard."
        })

    else:
        return HttpResponseForbidden("Your role is not recognized.")

    return render(request, 'users/dashboard.html', {
        'total_items': total_items,
        'total_categories': total_categories,
        'total_purchases': total_purchases,
        'total_issued': total_issued,
        'notifications': notifications,
        'total_suppliers': total_suppliers,
        'total_users': total_users,
        #'role': role,
        'role': request.user.role,
    })


@login_required
def store_dashboard(request):
    if request.user.role != 'store_officer':
        return HttpResponseForbidden("No access for this role.")
    return render(request, 'users/dashboard.html')


@login_required
def department_dashboard(request):
    if request.user.role != 'department_user':
        return HttpResponseForbidden("No access for this role.")
    return render(request, 'users/dashboard.html')


User = get_user_model()
from users.utils import is_user_online

@login_required
def user_list(request):
    if request.user.role != 'admin':
        return HttpResponseForbidden("Access Denied")

    users = User.objects.all()
    #users = User.objects.filter(is_active=True)
    return render(request, 'users/user_list.html', {'users': users, 'is_user_online': is_user_online,})


@login_required
def user_create(request):
    if request.user.role != 'admin':
        return HttpResponseForbidden("Access Denied")

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        role = request.POST['role']
        department = request.POST['department']

        User.objects.create(
            username=username,
            password=make_password(password),
            role=role,
            department=department
        )
        return redirect('user_list')

    return render(request, 'users/user_form.html', {'action': 'Create'})


@login_required
def user_edit(request, user_id):
    if request.user.role != 'admin':
        return HttpResponseForbidden("Access Denied")

    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        user.username = request.POST['username']
        user.role = request.POST['role']
        user.department = request.POST['department']
        if request.POST['password']:
            user.password = make_password(request.POST['password'])
        user.save()
        return redirect('user_list')

    return render(request, 'users/user_form.html', {'user': user, 'action': 'Edit'})


@login_required
def user_delete(request, user_id):
    if request.user.role != 'admin':
        return HttpResponseForbidden("Access Denied")

    user = User.objects.get(id=user_id)
    if user != request.user:
        user.delete()
    return redirect('user_list')




@login_required
def activity_log(request):
    if request.user.role != 'admin':
        return HttpResponseForbidden("Only admin can view logs")

    logs = ActivityLog.objects.select_related('user').order_by('-timestamp')[:100]

    return render(request, 'inventory/activity_log.html', {
        'logs': logs
    })


@login_required
def item_archive(request):
    if request.user.role != 'admin':
        return HttpResponseForbidden("Access denied")

    archived_items = Item.objects.filter(is_active=False)
    return render(request, 'inventory/item_archive.html', {
        'items': archived_items
    })

@login_required
def item_restore(request, item_id):
    if request.user.role != 'admin':
        return HttpResponseForbidden("Access denied")

    item = get_object_or_404(Item, id=item_id)
    item.is_active = True
    item.save()

    ActivityLog.objects.create(
        user=request.user,
        action='item_edit',
        description=f"Restored deleted item: {item.name}"
    )

    return redirect('item_archive')

from users.decorators import store_officer_required
from inventory.models import StockRequest
@login_required
@store_officer_required
def review_requests(request):
    pending_requests = StockRequest.objects.filter(status='pending').order_by('-created_at')
    return render(request, 'inventory/store_officer_review.html', {
        'pending_requests': pending_requests
    })

@login_required
@store_officer_required
def approve_request(request, request_id):
    req = StockRequest.objects.get(id=request_id)
    item = req.item
    if item.quantity_in_stock >= req.quantity:
        item.quantity_in_stock -= req.quantity
        item.save()
        req.status = 'approved'
    else:
        messages.warning(request, "Not enough stock.")
        return redirect('review_requests')
    req.save()
    return redirect('review_requests')

@login_required
@store_officer_required
def reject_request(request, request_id):
    req = StockRequest.objects.get(id=request_id)
    req.status = 'rejected'
    req.save()
    return redirect('review_requests')
