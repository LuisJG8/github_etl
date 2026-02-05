from airflow.sdk import dag, task
from pendulum import datetime
from celery import Celery
import os

app = Celery(
    'airflow_client',
    broker = os.getenv('CELERY_BROKER_URL'),
    backend = os.getenv('CELERY_BACKEND_URL')
)

@dag(
    schedule="@hourly",
    start_date=datetime(2026, 2, 3),
    description="Run Celery queue with RabbitMQ as the broker \
                 in order to get GitHub data from the GitHub API",
    tags=["celery_queue"],
    max_consecutive_failed_dag_runs=3,
)
def run_queue():
    
    @task
    def run_the_queue():
        app.send_task("worker.get_data_from_queue", args=[100, 500])

        
    run_the_queue()


run_queue()