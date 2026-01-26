import logging
from pathlib import Path
from datetime import datetime
from celery.result import AsyncResult
from worker import get_github_data, app, gh, distribute_tasks
from rb_queue.rabbitmq import consume_repos
import polars as pl


today = datetime.utcnow().strftime("%Y-%m-%d")

print("Waiting for Celery task to complete")

try:
    print("Getting the result")
    response = distribute_tasks.apply_async()
    the_data = response.get(timeout=3600)  # 1 hour timeout
    print(f"Result: {the_data}")

    # if distribute_tasks.apply_async() == True:   
    #     print("A subtask failed")


except Exception as e:
    print(f"Error: {e}")

else:
    if not Path(f"data/{today}/").exists():
        Path(f"data/{today}").mkdir(parents=True, exist_ok=True)

    print("This is the else of the client")
    print(the_data)

    df = pl.DataFrame(the_data)
    df.write_parquet(f"data/{today}/github_data.parquet", compression="zstd")
    print("Valid Parquet data")
