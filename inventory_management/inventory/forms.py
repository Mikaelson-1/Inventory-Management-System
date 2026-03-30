from django import forms
from .models import DepartmentRequest

class DepartmentRequestForm(forms.ModelForm):
    class Meta:
        model = DepartmentRequest
        fields = ['item', 'quantity', 'purpose']
        widgets = {
            'purpose': forms.Textarea(attrs={'rows': 3}),
        }
