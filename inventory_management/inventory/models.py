from django.db import models
from users.models import User

# Create your models here.
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Item(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    quantity_in_stock = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='items_created')
    updated_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='items_updated')
    deleted_by = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='items_deleted'
    )



    def __str__(self):
        return self.name

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name



class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='supplier_created')
    updated_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='supplier_updated')
    deleted_by = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='supplier_deleted'
    )




    def __str__(self):
        return self.name
    
class Purchase(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchased_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    purchase_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.item.name} - {self.quantity} units from {self.supplier.name}"

class StockOut(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
    quantity_issued = models.PositiveIntegerField()
    issued_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    issued_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.item.name} → {self.department} ({self.quantity_issued})"


class StockRequest(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
    ], default='Pending')
    purpose = models.TextField()
    requested_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)


from django.db import models
from django.conf import settings
from inventory.models import Item

class DepartmentRequest(models.Model):
    department = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    purpose = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    #requested_by = models.ForeignKey(User, on_delete=models.CASCADE)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='approved_requests'
    )

    def __str__(self):
        return f"{self.department} requested {self.quantity} x {self.item.name}"
