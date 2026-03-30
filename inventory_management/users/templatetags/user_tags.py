from django import template
from users.utils import is_user_online  # adjust if it's elsewhere

register = template.Library()

@register.filter
def online_status(user_id):
    return is_user_online(user_id)
