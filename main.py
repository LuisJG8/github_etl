import os 
import asyncio
import time
from datetime import datetime
from github import Auth, Github
from dotenv import load_dotenv
load_dotenv()

api_token = os.getenv("GITHUB_API_TOKEN")
print(api_token)
auth = Auth.Token(api_token)
gh = Github(auth=auth)


repositories = gh.get_repos(since=0)

def get_github_data():
    time_before = datetime.now()

    counter = 0
    for repo in repositories:
        print(repo)
        print(time_before)
        print(repo.stargazers_count)
        
        counter += 1
        if counter == 10:
            break
    
    return f" the name of the repo is actually going to be {repo.full_name}" if repo else "idk man"


get_github_data()