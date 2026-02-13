import logging
from pathlib import Path
from datetime import datetime
from celery.result import AsyncResult
from worker import build_repo_chord
from rb_queue.rabbitmq import consume_repos
import polars as pl

DIRECT = Path("/usr/local/airflow/project/data")

def save_to_parquet(the_data):
    today = datetime.now().strftime("%Y-%m-%d")

    # if not Path(f"data/{today}/").exists():
    #     Path(f"data/{today}").mkdir(parents=True, exist_ok=True)
    
    fi_direct = DIRECT / today
    fi_direct.mkdir(parents=True, exist_ok=True)

    print("This is the else of the client")
    print(the_data)

    df = pl.DataFrame(the_data)
    df.write_parquet(f"{fi_direct}/github_data.parquet", compression="zstd")
    print("Valid Parquet data")


def get_data_from_queue():
    try:
        print("Getting the result")
        
        response = build_repo_chord(total=5000, batch_size=500)
        the_data = response.get(timeout=3600)  # 1 hour timeout
        print(f"Result: {the_data}")

    except Exception as e:
        print(f"Error: {e}")

    return save_to_parquet(the_data)


if __name__ == "__main__":
    get_data_from_queue()

