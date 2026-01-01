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



print("Waiting for Celery task to complete")

# Collection to store all repository data from RabbitMQ
collected_repos = []

# Callback to collect data from RabbitMQ
def collect_repo_data(repo_data: RabbitMQ_Data_Validation):
    print("Received data from RMQ: ", repo_data.name if hasattr(repo_data, 'name') else repo_data)
    # Convert Pydantic model to dict for JSON serialization
    collected_repos.append(repo_data.model_dump())

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

            # Consume messages from RabbitMQ and collect data
            consume_repos(callback=collect_repo_data)

            # Ensure the data directory exists (persisted via Docker volume)
            os.makedirs("data", exist_ok=True)
            
            # Save collected data to JSON file in the mounted volume
            data_file_path = "data/gh_data.json"
            with open(data_file_path, mode="w") as f:
                json.dump(collected_repos, f, default=str, indent=2)
            
            print(f"Saved {len(collected_repos)} repositories to {data_file_path}")
            break
    else:
        print("Results are not ready")
        print(result.state)
        time.sleep(1)