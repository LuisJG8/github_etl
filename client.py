import time
import logging
from datetime import datetime
from celery.result import AsyncResult
from worker import get_github_data, app 
from rb_queue.rabbitmq import consume_repos
from pydantic_models.github import RabbitMQ_Data_Validation


celery_task_get_repos = get_github_data.delay()
result = AsyncResult(celery_task_get_repos.id, app=app)

while True:
    if result.ready():
        try:
            print('Getting the result')
            result.get()
        except Exception as e:
            print(e)
            break
        else:
            print('Done. The result state of the queue', result.state)

            consume_repos(callback=rabbitmq_process_data)
            break
    else:
        print("Results are not ready")
        print(result.state)
        time.sleep(1)