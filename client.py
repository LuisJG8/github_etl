import os
import time
import json
import logging
from datetime import datetime
from celery.result import AsyncResult
from worker import get_github_data, app 
from rb_queue.rabbitmq import consume_repos
from pydantic_models.github import RabbitMQ_Data_Validation


celery_task_get_repos = get_github_data.delay()
result = AsyncResult(celery_task_get_repos.id, app=app)

# Getting the data from RabbitMQ, note: convert to lambda
def rabbitmq_process_data(repo_data: RabbitMQ_Data_Validation):
    print("This is the data from the RMQ: ", repo_data)

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

            consume_repos(callback = lambda repo_data: print("This is the data from the RMQ: ", repo_data))

            with open("gh_data.json", mode="a") as f:
                json.dump(rabbitmq_process_data, f, default=str, indent=2)

            os.makedirs("data", exist_ok=True)
            
            with open("data/gh_data.json", mode="w") as fi:
                json.dump(rabbitmq_process_data, fi, default=str, indent=2)
            break
    else:
        print("Results are not ready")
        print(result.state)
        time.sleep(1)