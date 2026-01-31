from airflow.sdk import dag, task
from pendulum import datetime

@dag(
    schedule="@daily",
    start_date=datetime(2026, 1, 31),
    description="test dag",
    tags=["first dag"],
    max_consecutive_failed_dag_runs=3,
)
def my_dag():
    
    @task
    def _task_a():
        print("hello")

    _task_a()