from airflow.sdk import dag, task
from pendulum import datetime

@dag(
    schedule="@hourly",
    start_date=datetime(2026, 2, 2),
    description="Run Celery queue with RabbitMQ as the broker \
                 in order to get GitHub data from the GitHub API",
    tags=["celery_queue"],
    max_consecutive_failed_dag_runs=3,
)
def run_queue():
    
    @task
    def run_the_queue():
        print("hello")

    run_the_queue()


run_queue()