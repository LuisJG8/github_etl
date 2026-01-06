import time
import logging
from datetime import datetime
from celery.result import AsyncResult
from worker import get_github_data, app 
from rb_queue.rabbitmq import consume_repos
from pydantic_models.github import RabbitMQ_Data_Validation


celery_task_get_repos = get_github_data.delay()
result = AsyncResult(celery_task_get_repos.id, app=app)

print("Waiting for Celery task to complete")

# page = 0
# while True:
#     res = get_github_data.apply_async(kwargs={"page": page})   # kick off one batch/task
#     data_or_path = res.get(timeout=600)   # wait until done
#     if not data_or_path:                  # worker can return None to signal “no more”
#         break
#     page += 1

while True:
    if result.ready():
        try:
            print('Getting the result')
            res = get_github_data.delay()
            hey = res.get()

        except Exception as e:
            print(e)
            break
        
        else:
            print('Done. The result state of the queue', result.state)
            print(hey)
            # repo_data_ = consume_repos(callback = lambda repo_data: print("This is the data from the RMQ: ", repo_data))
            # all_data_collected.append(repo_data_)
            
    else:
        print("Results are not ready")
        print(result.state)
        time.sleep(1)