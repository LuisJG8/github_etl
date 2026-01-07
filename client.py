import time
import logging
from pathlib import Path
from datetime import datetime
from celery.result import AsyncResult
from worker import get_github_data, app 
from rb_queue.rabbitmq import consume_repos
from pydantic_models.github import RabbitMQ_Data_Validation
import polars as pl
from worker import get_github_data
import json


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
        res = get_github_data.apply_async()
        hey = res.get()
        print("The type is here", type(hey))

    except Exception as e:
        print(e)
        break
    
    else:
        print("this is the else")
        print(hey)
        # repo_data_ = consume_repos(callback = lambda repo_data: print("This is the data from the RMQ: ", repo_data))
        # all_data_collected.append(repo_data_)

        m_dir = Path("data").mkdir(parents=True, exist_ok=True)
        maa = pl.DataFrame()
        maa.write_parquet("data/testing.parquet", compression="zstd")
        break