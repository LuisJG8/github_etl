import os
import random 
from celery import Celery
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

    counter = 0

    for repo in repositories:
        try:
            repo.full_name
        except Exception as e:
            print(e)
            print("Full name not found")
        else:
            print(repo.full_name)

        try:
            repo.id
        except Exception as e:
            print(e)
            print("Repo id not found")
        else:
            print(repo.id)

        try:
            repo.forks_count
        except Exception as e:
            print(e)
            print("Repo id not found")
        else:
            print(repo.forks_count)
        
        counter += 1
        if counter == 1005:
            break
    
    return f" the name of the repo is actually going to be {repo.full_name}" if repo else "idk man"

# @app.task
# def random_number(max_value):
#     time.sleep(5)
#     return 'hello i am sponge bob'