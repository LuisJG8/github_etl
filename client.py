import time
import logging
from datetime import datetime
from celery.result import AsyncResult
from worker import get_github_data, app 
from rb_queue.rabbitmq import consume_repos
from models.github import RabbitMQ_Data_Validation


celery_task_get_repos = get_github_data.delay()
result = AsyncResult(celery_task_get_repos.id, app=app)

# Getting the data from RabbitMQ, note: convert to lambda
def rabbitmq_process_data(repo_data: RabbitMQ_Data_Validation):
    return print("This is the data from the RMQ: ", repo_data)

consume_repos(callback=rabbitmq_process_data)

print('Done')
print('The result state of the queue', result.state) 



# while True:
#     if result.ready():
#         print('Getting the result', result.get())
#         repo_list = result.get()
#         break
#     else:
#         print("Results are not ready")
#         print(result.state)
#         time.sleep(1)

# if isinstance(repo_list, list):
#     for repo_data in repo_list:
#         try:
#             publish_repo(repo_data)
#             print(f"Published repo: {repo_data.get('Full Name', repo_data.get('Name', 'unknown'))}")
#         except Exception as e:
#             logging.error(f"Failed to publish repo: {e}")
