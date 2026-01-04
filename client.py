import time
import logging
from datetime import datetime
from celery.result import AsyncResult
from worker import get_github_data, app 
from rb_queue.rabbitmq import consume_repos
from pydantic_models.github import RabbitMQ_Data_Validation

all_data_collected = []
celery_task_get_repos = get_github_data.delay()
result = AsyncResult(celery_task_get_repos.id, app=app)

print("Waiting for Celery task to complete")

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

            repo_data_ = consume_repos(callback = lambda repo_data: print("This is the data from the RMQ: ", repo_data))
            all_data_collected.append(repo_data_)
            break
    else:
        print("Results are not ready")
        print(result.state)
        time.sleep(1)