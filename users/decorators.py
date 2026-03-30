from django.shortcuts import redirect
from django.contrib import messages


def store_officer_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.role != 'store_officer':
            messages.error(request, "Access Denied: Store Officer only")
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper
