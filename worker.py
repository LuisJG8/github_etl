import os
import random 
import json
import boto3
from celery import Celery
from datetime import datetime
from github import Auth, Github
from dotenv import load_dotenv
load_dotenv()


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
print(api_token)
auth = Auth.Token(api_token)
gh = Github(auth=auth)


@app.task
def get_github_data():

    mylist = []

    repositories = gh.get_repos(since=0)
    counter = 0

    for repo in repositories:
        repo_data = {
            "full_name": repo.full_name,
            "id": repo.id,
            "forks_count": repo.forks_count,
        }
        
        mylist.append(repo_data)

        counter += 1
        if counter == 5:
            break

    filekey = "github_repos/kotomatsukami.json"
    s3_url = save_to_s3(mylist, filekey)

    print("data saved to s3")
    
    # return f" the name of the repo is actually going to be {repo.full_name}" if repo else "idk man"

# @app.task
# def random_number(max_value):
#     time.sleep(5)
#     return 'hello i am sponge bob'
