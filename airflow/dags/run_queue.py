import os
from airflow.sdk import dag, task
from pendulum import datetime
from celery import Celery
from github import Auth, Github, GithubException 
from client import get_data_from_queue
from datetime import timedelta
import time


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
    max_consecutive_failed_dag_runs=3
)
def run_github_data_queue():
            
    @task(do_xcom_push=True, multiple_outputs=True)
    def check_rate_limit(**context):
        api_token, api_token_two = os.getenv("GITHUB_API_TOKEN"), os.getenv("GITHUB_API_TOKEN_SECOND_ACCOUNT")
        auth, auth_two = Auth.Token(api_token), Auth.Token(api_token_two)
        gh, gh_two = Github(auth=auth), Github(auth=auth_two)   
 
        rate_limit = gh.rate_limiting
        print(f"Rate limit: {rate_limit[0]} remaining / {rate_limit[1]} total")

        return {
                "remaining": rate_limit[0], 
                "total": rate_limit[1]
                }

    @task
    def run_queue(**context):
        rate_limit = context["ti"].xcom_pull(task_ids="check_rate_limit", key="remaining")
        max_total_api_calls = context["ti"].xcom_pull(task_ids="check_rate_limit", key="total")

        if rate_limit > 100:
            print("IT WORKS")
            print(rate_limit)

            celery_worker = app.send_task("worker.get_github_data")

            print(celery_worker)

        time.sleep(500)
    
    @task
    def save_data_from_queue():

        get_data_from_queue()
            
            

    check_rate_limit() >> run_queue() >> save_data_from_queue()


run_github_data_queue()