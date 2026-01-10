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
def get_github_data(self):
    counter = 0
    repo_collection = []

    repositories = gh.get_repos(since=0)
    rate_limit = gh.rate_limiting
    print(f"Rate limit: {rate_limit[0]} remaining / {rate_limit[1]} total")

    connection = None
    channel = None

    try:
        connection = get_connection()
        channel = connection.channel()  
        
        channel.queue_declare(queue=QUEUE_NAME, durable=True)

        for repo in repositories:
            github_data_points = {
                # ===== MESSAGE METADATA =====
                # message_id and timestamp are handled by the Pydantic model defaults
                "message_id": self.request.id,

                # ===== BASIC INFO =====
                "got_data_in": todays_date if todays_date else None,
                "repo_id": repo.id if repo.id else None,
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



            repo_v = RabbitMQ_Data_Validation(**github_data_points)

            channel.basic_publish(
                exchange='',
                routing_key=QUEUE_NAME,
                body=repo_v.model_dump_json(),
                properties=pika.BasicProperties(delivery_mode=2)
            )


            counter += 1
            print(github_data_points)

            remaining_api_calls = gh.rate_limiting
            remaining = remaining_api_calls[0]

            if int(remaining) == 4020:
                print("found it")
                # TODO
                # Put worker.py on wait for 60 minutes
                # run the worker.py script with different env variables so that I can use the other
                # github account and it's credentials to have 1000 more API calls
                pass    

            print("Remaining api calls")
            print(remaining)

    except Exception as e:
        print(e)

    finally:
        # Path("data").mkdir(parents=True, exist_ok=True)
        # Path("data/github_repos.json").write_text(
        #     json.dumps(repo_collection, default=str, ensure_ascii=False, indent=2),
        #     encoding="utf-8",
        # )

        if connection:
            connection.close()
        else:
            print("The connection does not exist")


    # s3_url = save_to_s3(data=repo_collection, file_directory="github_repos/test.json")
    logger.info(f"Processed {len(repo_collection)} repositories")

    return repo_collection

logger.info("Worker module loaded")