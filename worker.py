import os
import random 
import json
import boto3
from celery import Celery
from datetime import datetime
from github import Auth, Github
from dotenv import load_dotenv
from rb_queue.rabbitmq import publish_repo, consume_repos
load_dotenv()


todays_date = datetime.now().strftime("%m-%d-%Y")
S3_BUCKET_NAME = "github-etl-data-bucket"


s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION", "us-east-1")
)


app = Celery(
    'github_repos',
    broker = os.getenv('CELERY_BROKER_URL'),
    backend = os.getenv('CELERY_BACKEND_URL')
)


def save_to_s3(data, file_directory):
    s3_client.put_object(
        Bucket=S3_BUCKET_NAME,
        Key=file_directory,
        Body=json.dumps(data, default=str)
    )


api_token = os.getenv("GITHUB_API_TOKEN")
auth = Auth.Token(api_token)
gh = Github(auth=auth)


@app.task
def get_github_data():

    counter = 0
    repo_collection = []

    repositories = gh.get_repos(since=0)
    rate_limit = gh.rate_limiting
    print(f"Rate limit: {rate_limit[0]} remaining / {rate_limit[1]} total")

    for repo in repositories:
        github_data_points = {
            # ===== MESSAGE METADATA =====
            # message_id and timestamp are handled by the Pydantic model defaults

            # ===== BASIC INFO =====
            "id": repo.id if repo.id else None,
            "name": repo.name if repo.name else None,
            "full_name": repo.full_name if repo.full_name else None,
            "description": repo.description if repo.description else None,
            "github_url": repo.html_url if repo.html_url else None,
            "homepage": repo.homepage if repo.homepage else None,
            "default_branch": repo.default_branch if repo.default_branch else None,

            # ===== POPULARITY METRICS =====
            "stargazers_count": repo.stargazers_count if repo.stargazers_count else 0,
            "forks_count": repo.forks_count if repo.forks_count else 0,
            "watchers_count": repo.watchers_count if repo.watchers_count else 0,
            "open_issues_count": repo.open_issues_count if repo.open_issues_count else 0,

            # ===== DATES =====
            "created_at": repo.created_at if repo.created_at else None,
            "updated_at": repo.updated_at if repo.updated_at else None,
            "pushed_at": repo.pushed_at if repo.pushed_at else None,

            # ===== REPOSITORY SETTINGS =====
            "language": repo.language if repo.language else None,
            "topics": repo.topics if repo.topics else [],
            "visibility": repo.visibility if repo.visibility else "public",
            "size_kb": repo.size if repo.size else 0,

            # ===== BOOLEAN FLAGS =====
            "is_fork": repo.fork if repo.fork else False,
            "is_archived": repo.archived if repo.archived else False,
            "is_private": repo.private if repo.private else False,

            # ===== OWNER INFO =====
            "owner_login": repo.owner.login if repo.owner else None,
            "owner_type": repo.owner.type if repo.owner else None,
        }

        repo_collection.append(github_data_points)

        publish_repo(github_data_points)

        counter += 1
        if counter == 5:
            break


    filekey = "github_repos/test.json"
    # s3_url = save_to_s3(repo_collection, filekey)
    print(repo_collection)


print("data saved to s3")