import os, time

from celery import Celery
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')


app = Celery('server')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.broker_url = settings.CELERY_BROKER_URL
app.autodiscover_tasks()


#docker-compose run --rm web-app sh -c "python manage.py shell"
#from celery_app import debug_task
#debug_task.delay()
@app.task()
def debug_task():
    time.sleep(5)
    print('test task!!')
    