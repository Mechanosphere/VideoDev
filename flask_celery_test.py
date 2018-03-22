from flask import Flask
from celery import Celery

"""flask_celery_test.py -- web app displaying long running operations testing flask and celery"""

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


@celery.task
def my_background_task(arg1, arg2):
    # some long running task here
    return result


