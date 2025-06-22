web: gunicorn order_management.wsgi:application
worker: celery -A order_management worker -l info --pool=solo
beat: celery -A order_management beat -l info