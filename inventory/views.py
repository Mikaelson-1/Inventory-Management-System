# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.db import models
from .models import Item, Category, StockOut, Supplier, Purchase
from users.models import ActivityLog
import pandas as pd
from users.utils import log_activity



@login_required
def item_list(request):
    query = request.GET.get('q')
    items = Item.objects.filter(is_active=True)

    # items = Item.objects.select_related('category')

    if query:
        items = items.filter(name__icontains=query)

    return render(request, 'inventory/item_list.html', {
        'items': items,
        'role': request.user.role,
        'search_query': query or ''
    })


@login_required
def item_create(request):
    if request.user.role != 'admin':
        return HttpResponseForbidden("Only admins can add inventory.")

    categories = Category.objects.all()

    if request.method == 'POST':
        name = request.POST['name']
        category_id = request.POST['category']
        quantity = request.POST['quantity']
        reorder_level = request.POST['reorder_level']
        

        category = Category.objects.get(id=category_id)

        item = Item.objects.create(
            name=name,
            category=category,
            quantity_in_stock=quantity,
            reorder_level=reorder_level,
            

        )

           # 📜 Log the action
        log_activity(request.user, 'item_create', f"Created item '{item.name}' in category '{item.category.name}'")


        return redirect('item_list')

    return render(request, 'inventory/item_form.html', {'categories': categories, 'action': 'Create'})


@login_required
def item_edit(request, item_id):
    if request.user.role != 'admin':
        return HttpResponseForbidden("Only admins can edit inventory.")

    item = get_object_or_404(Item, id=item_id)
    categories = Category.objects.all()

    if request.method == 'POST':
        item.name = request.POST['name']
        item.category_id = request.POST['category']
        item.quantity_in_stock = request.POST['quantity']
        item.reorder_level = request.POST['reorder_level']
        item.updated_by = request.user  #
        item.save()

        log_activity(request.user, 'item_delete', f"Deleted item '{item.name}' in category '{item.category.name}'")
        
        return redirect('item_list')

    return render(request, 'inventory/item_form.html', {'item': item, 'categories': categories, 'action': 'Edit'})


@login_required
def item_delete(request, item_id):
    if request.user.role != 'admin':
        return HttpResponseForbidden("Only admins can delete inventory.")

    item = get_object_or_404(Item, id=item_id)
    item.is_active = False
    item.deleted_by = request.user
    item.save()

    ActivityLog.objects.create(
        user=request.user,
        action='item_delete',
        description=f"Deleted item: {item.name}"
    )

    return redirect('item_list')

@login_required
def category_list(request):
    if request.user.role != 'admin':
        return HttpResponseForbidden("Admin access only")

    categories = Category.objects.all()
    return render(request, 'inventory/category_list.html', {'categories': categories})


@login_required
def category_create(request):
    if request.user.role != 'admin':
        return HttpResponseForbidden("Admin access only")

    if request.method == 'POST':
        name = request.POST['name']
        category = Category.objects.create(name=name)
        log_activity(request.user, 'Create Category', f"Created Category '{category.name}'")
        return redirect('category_list')

    

    return render(request, 'inventory/category_form.html', {'action': 'Create'})


@login_required
def category_edit(request, cat_id):
    if request.user.role != 'admin':
        return HttpResponseForbidden("Admin access only")

    category = get_object_or_404(Category, id=cat_id)

    if request.method == 'POST':
        category.name = request.POST['name']
        log_activity(request.user, 'Edit Category', f"Edited Category '{category.name}' ")
        category.save()
        return redirect('category_list')

    return render(request, 'inventory/category_form.html', {'category': category, 'action': 'Edit'})


@login_required
def category_delete(request, cat_id):
    if request.user.role != 'admin':
        return HttpResponseForbidden("Admin access only")

    category = get_object_or_404(Category, id=cat_id)
    log_activity(request.user, 'Delete Category', f"Deleted Category '{category.name}'")
    category.delete()
    return redirect('category_list')



@login_required
def supplier_list(request):
    if request.user.role not in ['admin', 'store_officer']:
        return HttpResponseForbidden("Access denied.")

    #suppliers = Supplier.objects.all()
    suppliers = Supplier.objects.filter(is_active=True)
    return render(request, 'inventory/supplier_list.html', {'suppliers': suppliers})


@login_required
def supplier_create(request):
    if request.user.role not in ['admin', 'store_officer']:
        return HttpResponseForbidden("Access denied.")

    if request.method == 'POST':
        supplier = Supplier.objects.create(
            name=request.POST['name'],
            contact_person=request.POST['contact_person'],
            phone=request.POST['phone'],
            email=request.POST['email'],
            address=request.POST['address']
        )
        log_activity(request.user, 'Add Supplier', f"Added Supplier '{supplier.name}' in supplier '{Supplier.created_by}'")
        return redirect('supplier_list')

    return render(request, 'inventory/supplier_form.html', {'action': 'Create'})


@login_required
def supplier_edit(request, supplier_id):
    if request.user.role not in ['admin', 'store_officer']:
        return HttpResponseForbidden("Access denied.")

    supplier = get_object_or_404(Supplier, id=supplier_id)

    if request.method == 'POST':
        supplier.name = request.POST['name']
        supplier.contact_person = request.POST['contact_person']
        supplier.phone = request.POST['phone']
        supplier.email = request.POST['email']
        supplier.address = request.POST['address']
        supplier.updated_by = request.user  #
        log_activity(request.user, 'Edit Supplier', f"Edited Supplier '{supplier.name}' in Supplier '")
        supplier.save()
        return redirect('supplier_list')

    return render(request, 'inventory/supplier_form.html', {'supplier': supplier, 'action': 'Edit'})


@login_required
def supplier_delete(request, supplier_id):
    if request.user.role not in ['admin', 'store_officer']:
        return HttpResponseForbidden("Access denied.")

    supplier = get_object_or_404(Supplier, id=supplier_id)
    supplier.deleted_by = request.user
    log_activity(request.user, 'item_delete', f"Deleted Supplier '{supplier.name}' in Supplier '")
    supplier.delete()
    return redirect('supplier_list')


@login_required
def purchase_create(request):
    if request.user.role not in ['admin', 'store_officer']:
        return HttpResponseForbidden("Access denied")

    suppliers = Supplier.objects.all()
    items = Item.objects.all()

    if request.method == 'POST':
        supplier_id = request.POST['supplier']
        item_id = request.POST['item']
        quantity = int(request.POST['quantity'])
        cost_price = float(request.POST['cost_price'])

        supplier = Supplier.objects.get(id=supplier_id)
        item = Item.objects.get(id=item_id)

        # Update item stock
        item.quantity_in_stock += quantity
        item.save()

        purchase = Purchase.objects.create(
            supplier=supplier,
            item=item,
            quantity=quantity,
            cost_price=cost_price,
            purchased_by=request.user
        )

        log_activity(request.user, 'Purchase Item', f"{purchase.quantity} {item} purchased from '{supplier.name}' for ₦{purchase.cost_price}' ")
        
        return redirect('purchase_list')

    return render(request, 'inventory/purchase_form.html', {
        'suppliers': suppliers,
        'items': items
    })


@login_required
def purchase_list(request):
    if request.user.role not in ['admin', 'store_officer']:
        return HttpResponseForbidden("Access denied")

    query = request.GET.get('q')
    purchases = Purchase.objects.select_related('supplier', 'item', 'purchased_by')

    if query:
        purchases = purchases.filter(
            models.Q(item__name__icontains=query) |
            models.Q(supplier__name__icontains=query)
        )

    purchases = purchases.order_by('-purchase_date')

    return render(request, 'inventory/purchase_list.html', {
        'purchases': purchases,
        'search_query': query or ''
    })



@login_required
def stockout_create(request):
    if request.user.role not in ['admin', 'store_officer']:
        return HttpResponseForbidden("Access denied")

    items = Item.objects.all()

    if request.method == 'POST':
        item_id = request.POST['item']
        department = request.POST['department']
        quantity = int(request.POST['quantity'])

        item = Item.objects.get(id=item_id)

        if quantity > item.quantity_in_stock:
            messages.error(request, 'Not enough stock available.')
            return redirect('stockout_create')

        # Deduct from stock
        item.quantity_in_stock -= quantity
        item.save()

        stockout = StockOut.objects.create(
            item=item,
            department=department,
            quantity_issued=quantity,
            issued_by=request.user
        )

        log_activity(
            request.user,
            'stock_out',
            f"{stockout.issued_by} issued {stockout.item} to {stockout.department})"
        )
        

        return redirect('stockout_list')

    return render(request, 'inventory/stockout_form.html', {'items': items})


@login_required
def stockout_list(request):
    if request.user.role not in ['admin', 'store_officer']:
        return HttpResponseForbidden("Access denied")

    query = request.GET.get('q')
    stockouts = StockOut.objects.select_related('item', 'issued_by')

    if query:
        stockouts = stockouts.filter(
            models.Q(item__name__icontains=query) |
            models.Q(department__icontains=query)
        )

    stockouts = stockouts.order_by('-issued_date')

    return render(request, 'inventory/stockout_list.html', {
        'stockouts': stockouts,
        'search_query': query or ''
    })


import pandas as pd
from django.http import HttpResponse
from io import BytesIO
from .models import Item

def export_items_excel(request):
    items = Item.objects.all().values('name', 'category__name', 'quantity_in_stock', 'reorder_level')
    df = pd.DataFrame(items)

    output = BytesIO()
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=items.xlsx'

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Items')

    response.write(output.getvalue())
    return response


from django.shortcuts import render, redirect, get_object_or_404
from .models import StockRequest, Item, Department
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from inventory.models import Item, DepartmentRequest
from users.utils import log_activity  # ✅ import logging helper

# 🔘 Department Users create request
@login_required
def create_stock_request(request):
    if request.method == "POST":
        item_id = request.POST.get('item')
        quantity = request.POST.get('quantity')
        purpose = request.POST.get('purpose')

        item = get_object_or_404(Item, id=item_id)
        department = request.user.department  # assuming user has a department field

        stockrequest = DepartmentRequest.objects.create(
            department=department,
            requested_by=request.user,
            item=item,
            quantity=quantity,
            purpose=purpose
        )

        # 📜 Log action
        log_activity(
            request.user,
            'user_action',
            f"Requested {stockrequest.quantity} '{stockrequest.item.name}' for purpose: {stockrequest.purpose}"
        )

        return redirect('request_success')

    items = Item.objects.filter(is_active=True)
    return render(request, 'inventory/request_form.html', {'items': items})


# 🔍 Review Requests (Admin / Store Officer)
@login_required
def review_requests_view(request):
    if request.user.role not in ['admin', 'store_officer']:
        return redirect('dashboard')

    requests = DepartmentRequest.objects.all().order_by('-created_at')
    return render(request, 'inventory/review_requests.html', {'requests': requests})


# ✅ Approve Request
@login_required
def approve_request(request, pk):
    if request.method == "POST" and request.user.role in ['admin', 'store_officer']:
        req = get_object_or_404(DepartmentRequest, pk=pk)

        # Reduce stock from main inventory
        if req.item.quantity_in_stock >= req.quantity:
            req.item.quantity_in_stock -= req.quantity
            req.item.save()

            # Update request status
            req.status = "approved"
            req.issued_date = now()
            req.save()

            # 📜 Log approval
            log_activity(
                request.user,
                'stock_out',
                f"Approved request #{req.id} for {req.quantity} '{req.item.name}' to department user {req.department.username}"
            )
        else:
            if request.user.is_authenticated:
                messages.error(request, "Not enough stock to approve request.")

    return redirect('review_requests')


# ❌ Decline Request
@login_required
def decline_request(request, pk):
    if request.method == "POST" and request.user.role in ['admin', 'store_officer']:
        req = get_object_or_404(DepartmentRequest, pk=pk)
        req.status = "declined"
        req.save()

        # 📜 Log decline
        log_activity(
            request.user,
            'user_action',
            f"Declined request #{req.id} for {req.quantity} '{req.item.name}' from department user {req.department.username}"
        )

    return redirect('review_requests')



# # ✅ Approve or Reject
# @login_required
# def update_request_status(request, request_id, status):
#     stock_request = get_object_or_404(StockRequest, id=request_id)
#     stock_request.status = status
#     stock_request.reviewed_at = timezone.now()
#     stock_request.save()
#     return redirect('review_requests')

from django.db.models import Count
from .models import Category, Item, StockRequest

from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from .models import Item, Purchase, StockOut, Category, StockRequest
from django.db import models


@login_required
def fancy_report_view(request):
    # LOW STOCK ITEMS
    low_stock_items = Item.objects.filter(quantity_in_stock__lte=models.F('reorder_level'))
    low_stock_labels = [item.name for item in low_stock_items]
    low_stock_values = [item.quantity_in_stock for item in low_stock_items]

    # STOCK IN vs STOCK OUT BY MONTH
    stock_in = Purchase.objects.annotate(month=TruncMonth('purchase_date')) \
                .values('month').annotate(total=Sum('quantity')).order_by('month')
    stock_out = StockOut.objects.annotate(month=TruncMonth('issued_date')) \
                .values('month').annotate(total=Sum('quantity_issued')).order_by('month')


    all_months = sorted(set([s['month'] for s in stock_in] + [s['month'] for s in stock_out]))
    labels = [m.strftime('%b %Y') for m in all_months]

    stock_in_dict = {s['month'].strftime('%b %Y'): s['total'] for s in stock_in}
    stock_out_dict = {s['month'].strftime('%b %Y'): s['total'] for s in stock_out}

    stock_in_data = [stock_in_dict.get(month, 0) for month in labels]
    stock_out_data = [stock_out_dict.get(month, 0) for month in labels]

    # ITEMS PER CATEGORY
    categories = Category.objects.all()
    category_labels = [cat.name for cat in categories]
    category_counts = [cat.item_set.count() for cat in categories]

    # MOST REQUESTED ITEMS
    item_data = StockRequest.objects.values('item__name').annotate(total=Count('id')).order_by('-total')[:5]
    item_labels = [d['item__name'] for d in item_data]
    item_counts = [d['total'] for d in item_data]

    return render(request, 'inventory/fancy_report.html', {
        'low_stock_labels': low_stock_labels,
        'low_stock_values': low_stock_values,
        'labels': labels,
        'stock_in_data': stock_in_data,
        'stock_out_data': stock_out_data,
        'category_labels': category_labels,
        'category_counts': category_counts,
        'item_labels': item_labels,
        'item_counts': item_counts,
    })


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import DepartmentRequest, Item

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from inventory.models import Item, DepartmentRequest
from django.contrib.auth.decorators import login_required

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from inventory.models import Item, DepartmentRequest
from django.contrib.auth.decorators import login_required

@login_required
def request_item_view(request):
    if request.user.role != 'department_user':
        return redirect('dashboard')

    if request.method == 'POST':
        item_id = request.POST.get('item')
        quantity_str = request.POST.get('quantity')
        
        # Ensure quantity is valid number
        try:
            quantity = int(quantity_str)
            if quantity <= 0:
                if request.user.is_authenticated:
                    messages.error(request, "Please enter a valid quantity greater than zero.")
                return redirect('request_item')
        except (ValueError, TypeError):
            messages.error(request, "Invalid quantity entered.")
            return redirect('request_item')

        item = get_object_or_404(Item, id=item_id)

        # 🚫 Block if item is out of stock
        if item.quantity_in_stock <= 0:
            messages.error(request, f"'{item.name}' is out of stock and cannot be requested.")
            return redirect('request_item')

        # 🚫 Block if requested quantity > available stock
        if quantity > item.quantity_in_stock:
            messages.error(request, f"Only {item.quantity_in_stock} '{item.name}' available in stock.")
            return redirect('request_item')

        # ✅ Create request
        deptrequest = DepartmentRequest.objects.create(
            department=request.user,
            item=item,
            quantity=quantity,
            purpose=request.POST.get('purpose', '')
        )

        log_activity(
            request.user,
            'department_request',
            f"{deptrequest.department} requested for {deptrequest.quantity} {deptrequest.item})"
        )

        if request.user.is_authenticated:
            messages.success(request, f"Request for {quantity} {item.name} submitted successfully.")
        return redirect('department_requests')

    # Only show items that have stock > 0
    items = Item.objects.filter(is_active=True, quantity_in_stock__gt=0)
    return render(request, 'department/request_item.html', {'items': items})


@login_required
def department_requests_view(request):
    if request.user.role != 'department_user':
        return redirect('dashboard')

    requests = DepartmentRequest.objects.filter(department=request.user).order_by('-created_at')


    return render(request, 'department/my_requests.html', {'requests': requests})
