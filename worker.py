import os
import pika
from pathlib import Path
import json
import boto3
from celery import Celery
from celery.utils.log import get_task_logger
from datetime import datetime
from github import Auth, Github # pylint: disable=no-name-in-module
from dotenv import load_dotenv
from pydantic_models.github import RabbitMQ_Data_Validation
from rb_queue.rabbitmq import get_connection, QUEUE_NAME
load_dotenv()


logger = get_task_logger(__name__)
todays_date = datetime.now().strftime("%m-%d-%Y")
S3_BUCKET_NAME = "github-etl-data-bucket"


s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION", "us-east-1")
)


def save_to_s3(data, file_directory):
    s3_client.put_object(
        Bucket=S3_BUCKET_NAME,
        Key=file_directory,
        Body=json.dumps(data, default=str)
    )


app = Celery(
    'github_repos',
    broker = os.getenv('CELERY_BROKER_URL'),
    backend = os.getenv('CELERY_BACKEND_URL')
)


api_token, api_token_two = os.getenv("GITHUB_API_TOKEN"), os.getenv("GITHUB_API_TOKEN_SECOND_ACCOUNT")
auth, auth_two = Auth.Token(api_token), Auth.Token(api_token_two)
gh, gh_two = Github(auth=auth), Github(auth=auth_two)


# bind = True allows to get task data, like task id
@app.task(bind=True)
def get_github_data(self, start_in_repo_num: int = 0, github_instance: Github = gh):
    counter = 0
    repo_collection = []
    connection = None
    channel = None

    repositories = github_instance.get_repos(since=start_in_repo_num)
    rate_limit = github_instance.rate_limiting
    print(f"Rate limit: {rate_limit[0]} remaining / {rate_limit[1]} total")

    try:
        connection = get_connection()
        channel = connection.channel()  
        channel.queue_declare(queue=QUEUE_NAME, durable=True)

        for repo in repositories:
            github_data_points = {
                "message_id": self.request.id,
                "got_data_in": todays_date if todays_date else None,
                "repo_id": repo.id if repo.id else None,
                "name": repo.name if repo.name else None,
                "full_name": repo.full_name if repo.full_name else None,
                "description": repo.description if repo.description else None,
                "github_url": repo.html_url if repo.html_url else None,
                "homepage": repo.homepage if repo.homepage else None,
                "default_branch": repo.default_branch if repo.default_branch else None,
                "stargazers_count": repo.stargazers_count if repo.stargazers_count else 0,
                "forks_count": repo.forks_count if repo.forks_count else 0,
                "watchers_count": repo.watchers_count if repo.watchers_count else 0,
                "open_issues_count": repo.open_issues_count if repo.open_issues_count else 0,
                "created_at": repo.created_at if repo.created_at else None,
                "updated_at": repo.updated_at if repo.updated_at else None,
                "pushed_at": repo.pushed_at if repo.pushed_at else None,
                "language": repo.language if repo.language else None,
                "topics": repo.topics if repo.topics else [],
                "visibility": repo.visibility if repo.visibility else "public",
                "size_kb": repo.size if repo.size else 0,
                "is_fork": repo.fork if repo.fork else False,
                "is_archived": repo.archived if repo.archived else False,
                "is_private": repo.private if repo.private else False,
                "owner_login": repo.owner.login if repo.owner else None,
                "owner_type": repo.owner.type if repo.owner else None,
            }

            repo_collection.append(github_data_points)


            repo_v = RabbitMQ_Data_Validation(**github_data_points)

            channel.basic_publish(
                exchange='',
                routing_key=QUEUE_NAME,
                body=repo_v.model_dump_json(),
                properties=pika.BasicProperties(delivery_mode=2)
            )

            counter += 1
            print(github_data_points)

            remaining_api_calls = github_instance.rate_limiting
            remaining = remaining_api_calls[0]

            # if int(remaining) <= 0:
            if counter == 5:
                print("reached the rate limit of 5000 API calls")
                print("waiting for 60 minutes")

                start_in_repo_num = counter
                github_instance = gh_two

                # raise self.retry(countdown=3600)
            
                # TODO
                # run the worker.py script with different env variables so that I can use the other
                # github account and it's credentials to have 1000 more API calls
            elif counter == 10:
                print('new ones')
                print(start_in_repo_num)
                print(github_instance)
                break

            else:
                print("Remaining api calls")
                print(remaining)

    except Exception as e:
        print(e)

    finally:
        if connection:
            connection.close()
        else:
            print("The connection does not exist")


    # s3_url = save_to_s3(data=repo_collection, file_directory="github_repos/test.json")
    logger.info(f"Processed {len(repo_collection)} repositories")

    return repo_collection

logger.info("Worker module loaded")