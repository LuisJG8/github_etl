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

today = datetime.utcnow().strftime("%Y-%m-%d")

print("Waiting for Celery task to complete")

try:
    print('Getting the result')
    response = get_github_data.apply_async()
    get_data = response.get(timeout=3600)  # 1 hour timeout
    print(f"Received {len(get_data)} records")

except Exception as e:
    print(f"Error: {e}")

else:
    if not Path(f"data/{today}/").exists():
        Path(f"data/{today}").mkdir(parents=True, exist_ok=True)

    print("this is the else")
    print(get_data)

    df = pl.DataFrame(get_data)
    df.write_parquet(f"data/{today}/github_data.parquet", compression="zstd")