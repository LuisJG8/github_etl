import os
from airflow.sdk import dag, task
from pendulum import datetime
from celery import Celery
from github import Auth, Github, GithubException 


api_token, api_token_two = os.getenv("GITHUB_API_TOKEN"), os.getenv("GITHUB_API_TOKEN_SECOND_ACCOUNT")
auth, auth_two = Auth.Token(api_token), Auth.Token(api_token_two)
gh, gh_two = Github(auth=auth), Github(auth=auth_two)

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
def run_github_data_queue():
            
    @task
    def check_rate_limit():
        rate_limit = gh.rate_limiting
        print(f"Rate limit: {rate_limit[0]} remaining / {rate_limit[1]} total")

        return {
                "remaining": rate_limit[0], 
                "total": rate_limit[1]
                }

    
    @task
    def run_the_queue(rate_limit: str):
        print(f'rate limit: {rate_limit["total"]}, remaining {rate_limit["remaining"]}')

        if rate_limit["remaining"] > 4900:
            app.send_task("worker.get_data_from_queue", args=[100, 500])

    val = check_rate_limit()
    run_the_queue(rate_limit=val)


run_github_data_queue()