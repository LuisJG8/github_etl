import os
import time 
import random 

from celery import Celery
import os 
import asyncio
import time
from datetime import datetime
from github import Auth, Github
from dotenv import load_dotenv
load_dotenv()


app = Celery(
    'github_repos',
    broker = os.getenv('CELERY_BROKER_URL'),
    backend = os.getenv('CELERY_BACKEND_URL')
)

api_token = os.getenv("GITHUB_API_TOKEN")
print(api_token)
auth = Auth.Token(api_token)
gh = Github(auth=auth)


repositories = gh.get_repos(since=0)


@app.task
def get_github_data():
    mylist = []
    
    for repo in repositories:
        print(repo)
        print(repo.stargazers_count)
        mylist.append(repo)

        break
    
    return f"the name is {mylist[0] if mylist else 'No repos found'}"

# @app.task
# def random_number(max_value):
#     time.sleep(5)
#     return 'hello i am sponge bob'