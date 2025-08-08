import os
import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aamarpay_project.settings')
app = Celery('aamarpay_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
