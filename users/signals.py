from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from users.models import ActivityLog, User
from inventory.models import Item, Supplier, Purchase, StockOut, DepartmentRequest
from django.utils.timezone import now

@receiver(post_save, sender=Item)
def test_item_signal(sender, instance, created, **kwargs):
    print(f"📌 Logging action: user={instance.created_by}, action=item_create")

def create_log(user, action, description):
    """Helper to safely log user actions."""
    if user and hasattr(user, 'id'):
        ActivityLog.objects.create(user=user, action=action, description=description)
        

# 📦 Item Created / Updated
@receiver(post_save, sender=Item)
def log_item_save(sender, instance, created, **kwargs):
    if created:
        create_log(instance.created_by, 'item_create', f"Item '{instance.name}' created in category '{instance.category.name}'")
    else:
        create_log(instance.updated_by, 'item_edit', f"Item '{instance.name}' updated")

# ❌ Item Deleted
@receiver(post_delete, sender=Item)
def log_item_delete(sender, instance, **kwargs):
    create_log(getattr(instance, 'deleted_by', None), 'item_delete', f"Item '{instance.name}' deleted")

# 🚚 Supplier Created / Updated
@receiver(post_save, sender=Supplier)
def log_supplier_save(sender, instance, created, **kwargs):
    action = 'supplier_action'
    if created:
        create_log(instance.created_by, action, f"Supplier '{instance.name}' added")
    else:
        create_log(instance.updated_by, action, f"Supplier '{instance.name}' updated")

# 🧾 Purchase Recorded
@receiver(post_save, sender=Purchase)
def log_purchase(sender, instance, created, **kwargs):
    if created:
        create_log(instance.purchased_by, 'purchase', f"Purchased {instance.quantity} of '{instance.item.name}' from {instance.supplier.name}")

# # 📤 Stock Out Recorded
# @receiver(post_save, sender=StockOut)
# def log_stockout(sender, instance, created, **kwargs):
#     if created:
#         create_log(instance.issued_by, 'stock_out', f"Issued {instance.quantity_issued} '{instance.item.name}' to {instance.department.name}")

# 🏢 Department Request Approved/Declined
@receiver(post_save, sender=DepartmentRequest)
def log_department_request(sender, instance, created, **kwargs):
    if not created:
        if instance.status == 'approved':
            create_log(instance.approved_by, 'stock_out', f"Approved request for {instance.quantity} '{instance.item.name}' to {instance.department.username}")
        elif instance.status == 'declined':
            create_log(instance.approved_by, 'user_action', f"Declined request for {instance.item.name} to {instance.department.username}")