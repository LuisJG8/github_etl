import logging
from pathlib import Path
from datetime import datetime
from celery.result import AsyncResult
from worker import get_github_data, app, gh
from rb_queue.rabbitmq import consume_repos
import polars as pl


# celery_task_get_repos = get_github_data.delay()
# result = AsyncResult(celery_task_get_repos.id, app=app)

today = datetime.utcnow().strftime("%Y-%m-%d")
all_data = []

print("Waiting for Celery task to complete")

try:
    print("Getting the result")
    response = get_github_data.apply_async()
    get_data = response.get(timeout=3600)  # 1 hour timeout
    print(f"Result: {get_data}")

except Exception as e:
    print(f"Error: {e}")
    df = pl.DataFrame(get_data)
    df.write_parquet(f"data/{today}/github_data.parquet", compression="zstd")

else:
    if not Path(f"data/{today}/").exists():
        Path(f"data/{today}").mkdir(parents=True, exist_ok=True)

    print("This is the else of the client")
    print(get_data)

    df = pl.DataFrame(get_data)
    df.write_parquet(f"data/{today}/github_data.parquet", compression="zstd")
    print("Valid Parquet data")