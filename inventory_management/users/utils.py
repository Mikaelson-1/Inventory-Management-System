from users.models import ActivityLog

def log_activity(user, action, description):
    ActivityLog.objects.create(
        user=user,
        action=action,
        description=description
    )


from django.core.cache import cache

def is_user_online(user_id):
    return cache.get(f'user_online_{user_id}') is not None
