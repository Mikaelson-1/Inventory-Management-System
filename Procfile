web: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn inventory_management.wsgi:application --bind 0.0.0.0:8000
