import time
import logging
from pathlib import Path
from datetime import datetime
from celery.result import AsyncResult
from worker import get_github_data, app 
from rb_queue.rabbitmq import consume_repos
from pydantic_models.github import RabbitMQ_Data_Validation
import polars as pl
from worker import get_github_data, gh


# celery_task_get_repos = get_github_data.delay()
# result = AsyncResult(celery_task_get_repos.id, app=app)

print("Waiting for Celery task to complete")

# page = 0
# while True:
#     res = get_github_data.apply_async(kwargs={"page": page})   # kick off one batch/task
#     data_or_path = res.get(timeout=600)   # wait until done
#     if not data_or_path:                  # worker can return None to signal “no more”
#         break
#     page += 1

while True:
    try:
        print('Getting the result')
        response = get_github_data.apply_async()
        get_data = response.get()
        print("The type is here", type(get_data))

    except Exception as e:
        print(e)
        break
    
    else:
        print("this is the else")
        print(get_data)

        df = pl.DataFrame(get_data)
        df.write_parquet("data/testing.parquet", compression="zstd")
        
        remaining_api_calls = gh.rate_limiting
        remaining = remaining_api_calls[0]

        if int(remaining) == 3970:
            break