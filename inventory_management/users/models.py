from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('store_officer', 'Store Officer'),
        ('department_user', 'Department User'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='department_user')
    department = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return f"{self.username} ({self.role})"

class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('stock_in', 'Stock In'),
        ('stock_out', 'Stock Out'),
        ('item_create', 'Item Created'),
        ('item_edit', 'Item Edited'),
        ('item_delete', 'Item Deleted'),
        ('supplier_action', 'Supplier Action'),
        ('purchase', 'Purchase'),
        ('user_action', 'User Action'),
    ]

    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


