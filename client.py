import time
import boto3
from datetime import datetime
from celery.result import AsyncResult
from worker import get_github_data, app 
from pydantic import BaseModel
from typing import List
from rb_queue.rabbitmq import publish_repo


result_future = get_github_data.delay()
result = AsyncResult(result_future.id, app=app)

print('Done')
print('The result state of the queue', result.state) 


while True:
    if result.ready():
        print('Getting the result', result.get())
        repo_list = result.get()
        break
    else:
        print(result.state)
        time.sleep(1)

if isinstance(repo_list, list):
    for repo_data in repo_list:
        try:
            publish_repo(repo_data)
            print(f"Published repo: {repo_data.get('Full Name', repo_data.get('Name', 'unknown'))}")
        except Exception as e:
            print(f"Failed to publish repo: {e}")