from django.utils.timezone import now
from django.contrib.auth import get_user_model
from django.core.cache import cache

User = get_user_model()

class ActiveUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Save user online timestamp to cache
            cache.set(f'user_online_{request.user.id}', True, timeout=60)  # online for 1 minute
        response = self.get_response(request)
        return response
